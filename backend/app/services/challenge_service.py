import uuid
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.models.user import User
from app.models.progress import ReadingProgress, UserStats
from app.models.reading_plan import ReadingPlan
from app.models.challenge import (
    ChurchChallenge, ChallengeMember, Family, FamilyMember, BuddyGroup, BuddyMember,
    JoinRequest, ChallengeReward, Encouragement,
    ChallengeMemberStatus, GroupMemberRole, GroupMemberStatus, RequestStatus, RequestType,
)
from app.models.leaderboard import LeaderboardConfig
from app.models.group import RootedGroup, UserGroupMembership
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.services.reading_status import completed_today_user_ids
from app.services import audit_service
from app.services.notification_service import notify
from app.schemas.challenge import (
    RootedIdLookupOut, ChallengeCreate, ChallengeUpdate, ChallengeAdminOut,
    ChallengeSummaryOut, TodayReadingOut, ChallengeGroupSummary, ChallengeDetailOut,
    GroupCreate, GroupMemberOut, GroupDetailOut, JoinRequestOut, RewardCreate, RewardOut, RewardEarnedOut,
    EncouragementCreate, GroupAdminSummaryOut,
    LeaderboardConfigOut, LeaderboardConfigUpdate, LeaderboardEntryOut, LeaderboardOut,
)

# Product rule: Family ranks show only the #1 spot, every other scope
# (individual participants and each Rooted Group) shows the top 3 -
# admin can override per challenge via LeaderboardConfig.
_DEFAULT_RANKING_LIMITS = {"family": 1}
_DEFAULT_RANKING_LIMIT = 3

_ENCOURAGEMENT_MESSAGES = {
    "Keep going.", "Stay rooted.", "Great job completing today's reading.",
    "Keep growing in the Word.", "Praying for you.", "Well done.",
}


class ChallengeService:
    def __init__(self, db: Session):
        self.db = db
        self.plans = ReadingPlanRepository(db)

    # -----------------------------------------------------------------
    # Rooted ID lookup
    # -----------------------------------------------------------------
    def lookup_rooted_id(self, rooted_id: str) -> RootedIdLookupOut:
        user = self.db.query(User).filter(User.user_id == rooted_id.strip().upper(), User.deleted_at.is_(None)).first()
        if not user:
            raise NotFoundError("Rooted ID not found.")
        return RootedIdLookupOut(user_id=user.user_id, name=user.name, photo_url=user.photo_url)

    def _get_user_by_rooted_id(self, rooted_id: str) -> User:
        user = self.db.query(User).filter(User.user_id == rooted_id.strip().upper(), User.deleted_at.is_(None)).first()
        if not user:
            raise NotFoundError("Rooted ID not found.")
        return user

    # -----------------------------------------------------------------
    # Admin: Church Challenge CRUD
    # -----------------------------------------------------------------
    def _participant_count(self, challenge_id: uuid.UUID) -> int:
        return (
            self.db.query(ChallengeMember)
            .filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.status == ChallengeMemberStatus.active.value)
            .count()
        )

    def admin_create_challenge(self, actor_id: uuid.UUID, payload: ChallengeCreate) -> ChurchChallenge:
        challenge = ChurchChallenge(
            name=payload.name, church_name=payload.church_name, description=payload.description,
            reading_plan_id=payload.reading_plan_id, start_date=payload.start_date, end_date=payload.end_date,
            participant_limit=payload.participant_limit, allow_families=payload.allow_families,
            allow_buddies=payload.allow_buddies, quiz_enabled=payload.quiz_enabled,
            rewards_enabled=payload.rewards_enabled, status=payload.status, created_by=actor_id,
        )
        self.db.add(challenge)
        self.db.flush()
        audit_service.record(self.db, actor_id, "challenge_created", "church_challenge", challenge.id, {"name": challenge.name})
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def admin_update_challenge(self, actor_id: uuid.UUID, challenge_id: uuid.UUID, payload: ChallengeUpdate) -> ChurchChallenge:
        challenge = self._get_challenge(challenge_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(challenge, field, value)
        audit_service.record(self.db, actor_id, "challenge_updated", "church_challenge", challenge.id)
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def admin_delete_challenge(self, actor_id: uuid.UUID, challenge_id: uuid.UUID) -> None:
        challenge = self._get_challenge(challenge_id)
        challenge.status = "archived"
        audit_service.record(self.db, actor_id, "challenge_archived", "church_challenge", challenge.id)
        self.db.commit()

    def admin_list_challenges(self) -> list[ChallengeAdminOut]:
        challenges = self.db.query(ChurchChallenge).filter(ChurchChallenge.deleted_at.is_(None)).order_by(ChurchChallenge.created_at.desc()).all()
        return [
            ChallengeAdminOut(
                id=c.id, name=c.name, church_name=c.church_name, description=c.description,
                reading_plan_id=c.reading_plan_id, start_date=c.start_date, end_date=c.end_date,
                participant_limit=c.participant_limit, participant_count=self._participant_count(c.id),
                status=c.status, allow_families=c.allow_families,
                allow_buddies=c.allow_buddies, quiz_enabled=c.quiz_enabled,
                rewards_enabled=c.rewards_enabled, created_at=c.created_at,
            )
            for c in challenges
        ]

    def _get_challenge(self, challenge_id: uuid.UUID) -> ChurchChallenge:
        challenge = self.db.query(ChurchChallenge).filter(ChurchChallenge.id == challenge_id, ChurchChallenge.deleted_at.is_(None)).first()
        if not challenge:
            raise NotFoundError("Church Challenge not found.")
        return challenge

    # -----------------------------------------------------------------
    # Membership helpers
    # -----------------------------------------------------------------
    def _active_challenge_membership(self, challenge_id: uuid.UUID, user_id: uuid.UUID) -> ChallengeMember | None:
        return (
            self.db.query(ChallengeMember)
            .filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.user_id == user_id, ChallengeMember.status == ChallengeMemberStatus.active.value)
            .first()
        )

    def _require_active_participant(self, challenge_id: uuid.UUID, user_id: uuid.UUID) -> ChallengeMember:
        member = self._active_challenge_membership(challenge_id, user_id)
        if not member:
            raise ForbiddenError("You are not a participant of this Church Challenge.")
        return member

    # -----------------------------------------------------------------
    # User: request to join a Church Challenge (concurrency-safe capacity)
    # -----------------------------------------------------------------
    def request_join_challenge(self, user_id: uuid.UUID, challenge_id: uuid.UUID) -> JoinRequest:
        challenge = self._get_challenge(challenge_id)
        if challenge.status not in ("active", "draft"):
            raise ValidationError("This Church Challenge is not accepting new participants.")

        existing_member = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.user_id == user_id).first()
        if existing_member and existing_member.status == ChallengeMemberStatus.active.value:
            raise ConflictError("You already belong to this Church Challenge.")
        if existing_member and existing_member.status == ChallengeMemberStatus.pending.value:
            raise ConflictError("Your request to join is already pending.")

        pending = (
            self.db.query(JoinRequest)
            .filter(JoinRequest.type == RequestType.challenge.value, JoinRequest.challenge_id == challenge_id, JoinRequest.requester_id == user_id, JoinRequest.status == RequestStatus.pending.value)
            .first()
        )
        if pending:
            raise ConflictError("Your request to join is already pending.")

        # Lock the challenge row so two simultaneous joins at capacity can't both succeed.
        # participant_limit of None means unlimited - never gate on it.
        self.db.query(ChurchChallenge).filter(ChurchChallenge.id == challenge_id).with_for_update().first()
        if challenge.participant_limit is not None:
            count = self._participant_count(challenge_id)
            if count >= challenge.participant_limit:
                raise ConflictError("Challenge is full.")

        if existing_member:
            existing_member.status = ChallengeMemberStatus.pending.value
        else:
            self.db.add(ChallengeMember(challenge_id=challenge_id, user_id=user_id, status=ChallengeMemberStatus.pending.value))

        request = JoinRequest(type=RequestType.challenge.value, requester_id=user_id, target_user_id=None, challenge_id=challenge_id, status=RequestStatus.pending.value)
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def admin_approve_challenge_member(self, actor_id: uuid.UUID, request_id: uuid.UUID, approve: bool) -> None:
        request = self._get_request(request_id)
        if request.type != RequestType.challenge.value or request.status != RequestStatus.pending.value:
            raise NotFoundError("Request not found.")
        member = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == request.challenge_id, ChallengeMember.user_id == request.requester_id).first()

        if approve:
            self.db.query(ChurchChallenge).filter(ChurchChallenge.id == request.challenge_id).with_for_update().first()
            challenge = self._get_challenge(request.challenge_id)
            if challenge.participant_limit is not None:
                count = self._participant_count(request.challenge_id)
                if count >= challenge.participant_limit:
                    raise ConflictError("Challenge is full.")
            if member:
                member.status = ChallengeMemberStatus.active.value
                member.joined_at = datetime.now(timezone.utc)
            request.status = RequestStatus.approved.value
            audit_service.record(self.db, actor_id, "challenge_member_approved", "challenge_member", request.challenge_id, {"user_id": str(request.requester_id)})
            notify(self.db, request.requester_id, "challenge_request_approved", f"You're in! {challenge.name}", link=f"/community/challenges/{request.challenge_id}")
        else:
            if member:
                self.db.delete(member)
            request.status = RequestStatus.declined.value
            audit_service.record(self.db, actor_id, "challenge_member_declined", "challenge_member", request.challenge_id, {"user_id": str(request.requester_id)})
            challenge = self._get_challenge(request.challenge_id)
            notify(self.db, request.requester_id, "challenge_request_declined", f"Your request to join {challenge.name} was declined")

        request.responded_at = datetime.now(timezone.utc)
        request.responded_by_id = actor_id
        self.db.commit()

    def admin_remove_challenge_member(self, actor_id: uuid.UUID, challenge_id: uuid.UUID, target_rooted_id: str) -> None:
        target = self._get_user_by_rooted_id(target_rooted_id)
        member = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.user_id == target.id).first()
        if not member:
            raise NotFoundError("This user is not a participant of this challenge.")
        member.status = ChallengeMemberStatus.removed.value

        for fm in self.db.query(FamilyMember).join(Family, Family.id == FamilyMember.family_id).filter(Family.challenge_id == challenge_id, FamilyMember.user_id == target.id, FamilyMember.status == GroupMemberStatus.active.value).all():
            fm.status = GroupMemberStatus.removed.value
        for bm in self.db.query(BuddyMember).join(BuddyGroup, BuddyGroup.id == BuddyMember.buddy_group_id).filter(BuddyGroup.challenge_id == challenge_id, BuddyMember.user_id == target.id, BuddyMember.status == GroupMemberStatus.active.value).all():
            bm.status = GroupMemberStatus.removed.value

        audit_service.record(self.db, actor_id, "challenge_member_removed", "challenge_member", challenge_id, {"user_id": str(target.id)})
        self.db.commit()

    def admin_list_pending_requests(self, challenge_id: uuid.UUID) -> list["ChallengeRequestAdminOut"]:
        from app.schemas.challenge import ChallengeRequestAdminOut
        rows = (
            self.db.query(JoinRequest, User)
            .join(User, User.id == JoinRequest.requester_id)
            .filter(JoinRequest.type == RequestType.challenge.value, JoinRequest.challenge_id == challenge_id, JoinRequest.status == RequestStatus.pending.value)
            .order_by(JoinRequest.created_at)
            .all()
        )
        return [ChallengeRequestAdminOut(request_id=r.id, user_id=u.user_id, name=u.name, requested_at=r.created_at) for r, u in rows]

    def admin_list_challenge_members(self, challenge_id: uuid.UUID) -> list["ChallengeMemberAdminOut"]:
        from app.schemas.challenge import ChallengeMemberAdminOut
        rows = (
            self.db.query(ChallengeMember, User)
            .join(User, User.id == ChallengeMember.user_id)
            .filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.status == ChallengeMemberStatus.active.value)
            .all()
        )
        user_ids = [u.id for _, u in rows]
        completed_ids = completed_today_user_ids(self.db, user_ids)
        stats_by_user = {s.user_id: s for s in self.db.query(UserStats).filter(UserStats.user_id.in_(user_ids)).all()}

        family_by_user: dict[uuid.UUID, str] = {}
        for fm, f in (
            self.db.query(FamilyMember, Family)
            .join(Family, Family.id == FamilyMember.family_id)
            .filter(Family.challenge_id == challenge_id, FamilyMember.status == GroupMemberStatus.active.value)
            .all()
        ):
            family_by_user[fm.user_id] = f.name

        buddy_by_user: dict[uuid.UUID, str] = {}
        for bm, g in (
            self.db.query(BuddyMember, BuddyGroup)
            .join(BuddyGroup, BuddyGroup.id == BuddyMember.buddy_group_id)
            .filter(BuddyGroup.challenge_id == challenge_id, BuddyMember.status == GroupMemberStatus.active.value)
            .all()
        ):
            buddy_by_user[bm.user_id] = g.name

        out = []
        for member, u in rows:
            out.append(ChallengeMemberAdminOut(
                user_id=u.user_id, name=u.name, family_name=family_by_user.get(u.id), buddy_group_name=buddy_by_user.get(u.id),
                progress_percent=self._my_progress_percent(u.id), streak=stats_by_user[u.id].current_streak if u.id in stats_by_user else 0,
                completed_today=u.id in completed_ids, status=member.status,
            ))
        return out

    # -----------------------------------------------------------------
    # User: list my challenges / detail
    # -----------------------------------------------------------------
    def _my_progress_percent(self, user_id: uuid.UUID) -> int:
        total_days = self.plans.total_days()
        if not total_days:
            return 0
        completed = self.db.query(ReadingProgress).filter(ReadingProgress.user_id == user_id, ReadingProgress.completed.is_(True)).count()
        return round((completed / total_days) * 100)

    def list_my_challenges(self, user_id: uuid.UUID) -> list[ChallengeSummaryOut]:
        rows = (
            self.db.query(ChallengeMember, ChurchChallenge)
            .join(ChurchChallenge, ChurchChallenge.id == ChallengeMember.challenge_id)
            .filter(ChallengeMember.user_id == user_id, ChallengeMember.status.in_([ChallengeMemberStatus.active.value, ChallengeMemberStatus.pending.value]), ChurchChallenge.deleted_at.is_(None))
            .all()
        )
        today_plan = self.plans.get_today()
        total_days = self.plans.total_days()
        out = []
        for member, challenge in rows:
            has_family = self.db.query(FamilyMember).join(Family, Family.id == FamilyMember.family_id).filter(Family.challenge_id == challenge.id, FamilyMember.user_id == user_id, FamilyMember.status == GroupMemberStatus.active.value).first() is not None
            has_buddy = self.db.query(BuddyMember).join(BuddyGroup, BuddyGroup.id == BuddyMember.buddy_group_id).filter(BuddyGroup.challenge_id == challenge.id, BuddyMember.user_id == user_id, BuddyMember.status == GroupMemberStatus.active.value).first() is not None
            out.append(ChallengeSummaryOut(
                id=challenge.id, name=challenge.name, church_name=challenge.church_name, status=challenge.status,
                day_number=today_plan.day_number if today_plan else None, total_days=total_days,
                my_progress_percent=self._my_progress_percent(user_id) if member.status == ChallengeMemberStatus.active.value else 0,
                my_status=member.status, has_family=has_family, has_buddy_group=has_buddy,
            ))
        return out

    def list_joinable_challenges(self, user_id: uuid.UUID) -> list[ChallengeAdminOut]:
        my_ids = {m.challenge_id for m in self.db.query(ChallengeMember).filter(ChallengeMember.user_id == user_id).all()}
        challenges = self.db.query(ChurchChallenge).filter(ChurchChallenge.status.in_(["active", "draft"]), ChurchChallenge.deleted_at.is_(None)).order_by(ChurchChallenge.created_at.desc()).all()
        return [
            ChallengeAdminOut(
                id=c.id, name=c.name, church_name=c.church_name, description=c.description,
                reading_plan_id=c.reading_plan_id, start_date=c.start_date, end_date=c.end_date,
                participant_limit=c.participant_limit, participant_count=self._participant_count(c.id),
                status=c.status, allow_families=c.allow_families,
                allow_buddies=c.allow_buddies, quiz_enabled=c.quiz_enabled,
                rewards_enabled=c.rewards_enabled, created_at=c.created_at,
            )
            for c in challenges if c.id not in my_ids
        ]

    def get_challenge_detail(self, user_id: uuid.UUID, challenge_id: uuid.UUID) -> ChallengeDetailOut:
        challenge = self._get_challenge(challenge_id)
        member = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.user_id == user_id).first()
        if not member:
            raise ForbiddenError("You are not a participant of this Church Challenge.")

        today_plan = self.plans.get_today()
        total_days = self.plans.total_days()
        today_out = None
        stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if member.status == ChallengeMemberStatus.active.value and today_plan:
            progress = self.db.query(ReadingProgress).filter(ReadingProgress.user_id == user_id, ReadingProgress.reading_plan_id == today_plan.id).first()
            today_out = TodayReadingOut(
                old_testament=today_plan.old_testament, new_testament=today_plan.new_testament,
                estimated_minutes=today_plan.estimated_minutes, completed=bool(progress and progress.completed),
            )

        family_summary = None
        family_member = self.db.query(FamilyMember).join(Family, Family.id == FamilyMember.family_id).filter(Family.challenge_id == challenge_id, FamilyMember.user_id == user_id, FamilyMember.status == GroupMemberStatus.active.value).first()
        if family_member:
            family = self.db.query(Family).filter(Family.id == family_member.family_id).first()
            active_ids = [m.user_id for m in self.db.query(FamilyMember).filter(FamilyMember.family_id == family.id, FamilyMember.status == GroupMemberStatus.active.value).all()]
            completed = completed_today_user_ids(self.db, active_ids)
            family_summary = ChallengeGroupSummary(id=family.id, name=family.name, member_count=len(active_ids), max_members=None, completed_today_count=len(completed))

        buddy_summary = None
        buddy_member = self.db.query(BuddyMember).join(BuddyGroup, BuddyGroup.id == BuddyMember.buddy_group_id).filter(BuddyGroup.challenge_id == challenge_id, BuddyMember.user_id == user_id, BuddyMember.status == GroupMemberStatus.active.value).first()
        if buddy_member:
            group = self.db.query(BuddyGroup).filter(BuddyGroup.id == buddy_member.buddy_group_id).first()
            active_ids = [m.user_id for m in self.db.query(BuddyMember).filter(BuddyMember.buddy_group_id == group.id, BuddyMember.status == GroupMemberStatus.active.value).all()]
            completed = completed_today_user_ids(self.db, active_ids)
            buddy_summary = ChallengeGroupSummary(id=group.id, name=group.name, member_count=len(active_ids), max_members=None, completed_today_count=len(completed))

        return ChallengeDetailOut(
            id=challenge.id, name=challenge.name, church_name=challenge.church_name, description=challenge.description,
            status=challenge.status, day_number=today_plan.day_number if today_plan else None, total_days=total_days,
            my_progress_percent=self._my_progress_percent(user_id) if member.status == ChallengeMemberStatus.active.value else 0,
            my_streak=stats.current_streak if stats else 0, my_status=member.status, today=today_out,
            family=family_summary, buddy_group=buddy_summary, quiz_enabled=challenge.quiz_enabled,
            rewards_enabled=challenge.rewards_enabled, participant_count=self._participant_count(challenge_id),
            participant_limit=challenge.participant_limit,
        )

    # -----------------------------------------------------------------
    # Family / Buddy - shared implementation via a `kind` switch
    # -----------------------------------------------------------------
    def _group_model(self, kind: str):
        return Family if kind == "family" else BuddyGroup

    def _member_model(self, kind: str):
        return FamilyMember if kind == "family" else BuddyMember

    def _group_fk(self, kind: str) -> str:
        return "family_id" if kind == "family" else "buddy_group_id"

    def _allowed_for(self, kind: str, challenge: ChurchChallenge) -> bool:
        return challenge.allow_families if kind == "family" else challenge.allow_buddies

    def list_my_groups(self, kind: str, user_id: uuid.UUID) -> list[GroupDetailOut]:
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        group_ids = [
            getattr(row, fk)
            for row in self.db.query(MemberModel).filter(MemberModel.user_id == user_id, MemberModel.status == GroupMemberStatus.active.value).all()
        ]
        return [self.get_group_detail(kind, user_id, group_id) for group_id in group_ids]

    def admin_list_all_groups(self, kind: str) -> list[GroupAdminSummaryOut]:
        """Super Admin's platform-wide view - every Family/Buddy Group,
        regardless of privacy or whether it's linked to a Church Challenge.
        Private groups are never visible to other normal users, but this
        endpoint is admin-only (see require_admin on the route)."""
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)

        groups = self.db.query(GroupModel).order_by(GroupModel.created_at.desc()).all()
        out = []
        for group in groups:
            owner = self.db.query(User).filter(User.id == group.owner_id).first()
            member_count = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == group.id, MemberModel.status == GroupMemberStatus.active.value).count()
            challenge_name = None
            if group.challenge_id:
                challenge = self.db.query(ChurchChallenge).filter(ChurchChallenge.id == group.challenge_id).first()
                challenge_name = challenge.name if challenge else None
            out.append(GroupAdminSummaryOut(
                id=group.id, name=group.name, owner_user_id=owner.user_id if owner else "?", owner_name=owner.name if owner else "?",
                member_count=member_count, challenge_id=group.challenge_id, challenge_name=challenge_name,
                privacy=getattr(group, "privacy", "private"), created_at=group.created_at,
            ))
        return out

    def create_group(self, kind: str, user_id: uuid.UUID, payload: GroupCreate, challenge_id: uuid.UUID | None = None):
        """Family/Buddy Group are standalone - `challenge_id` is an optional
        opt-in link to a single Church Challenge this group is currently
        participating in. No size cap either way."""
        if challenge_id is not None:
            challenge = self._get_challenge(challenge_id)
            self._require_active_participant(challenge_id, user_id)
            if not self._allowed_for(kind, challenge):
                raise ValidationError(f"{'Families' if kind == 'family' else 'Buddy groups'} are not enabled for this challenge.")

        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)

        group = GroupModel(challenge_id=challenge_id, name=payload.name, owner_id=user_id, description=payload.description)
        self.db.add(group)
        self.db.flush()
        self.db.add(MemberModel(**{fk: group.id, "user_id": user_id, "role": GroupMemberRole.owner.value, "status": GroupMemberStatus.active.value}))
        audit_service.record(self.db, user_id, f"{kind}_created", kind, group.id, {"name": group.name, "challenge_id": str(challenge_id) if challenge_id else None})
        self.db.commit()
        self.db.refresh(group)
        return group

    def _require_group_membership(self, kind: str, group_id: uuid.UUID, user_id: uuid.UUID):
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        member = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == group_id, MemberModel.user_id == user_id, MemberModel.status == GroupMemberStatus.active.value).first()
        if not member:
            raise ForbiddenError("You are not a member of this group.")
        return member

    def get_group_detail(self, kind: str, user_id: uuid.UUID, group_id: uuid.UUID) -> GroupDetailOut:
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise NotFoundError("Group not found.")
        my_membership = self._require_group_membership(kind, group_id, user_id)

        rows = (
            self.db.query(MemberModel, User)
            .join(User, User.id == MemberModel.user_id)
            .filter(getattr(MemberModel, fk) == group_id, MemberModel.status == GroupMemberStatus.active.value)
            .all()
        )
        user_ids = [u.id for _, u in rows]
        completed_ids = completed_today_user_ids(self.db, user_ids)
        stats_by_user = {s.user_id: s for s in self.db.query(UserStats).filter(UserStats.user_id.in_(user_ids)).all()}

        members = [
            GroupMemberOut(
                user_id=u.user_id, name=u.name, photo_url=u.photo_url, role=member.role,
                completed_today=u.id in completed_ids, current_streak=stats_by_user[u.id].current_streak if u.id in stats_by_user else 0,
            )
            for member, u in rows
        ]
        return GroupDetailOut(
            id=group.id, challenge_id=group.challenge_id, name=group.name,
            description=getattr(group, "description", None), my_role=my_membership.role,
            max_members=None, members=members,
        )

    def invite_to_group(self, kind: str, actor_id: uuid.UUID, group_id: uuid.UUID, rooted_id: str) -> JoinRequest:
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise NotFoundError("Group not found.")
        self._require_group_membership(kind, group_id, actor_id)

        target = self._get_user_by_rooted_id(rooted_id)
        if group.challenge_id is not None and not self._active_challenge_membership(group.challenge_id, target.id):
            raise ValidationError(f"{target.name} is not a participant of this Church Challenge.")

        already_member = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == group_id, MemberModel.user_id == target.id, MemberModel.status == GroupMemberStatus.active.value).first()
        if already_member:
            raise ConflictError(f"{target.name} is already in this group.")

        pending = self.db.query(JoinRequest).filter(JoinRequest.type == kind, getattr(JoinRequest, fk) == group_id, JoinRequest.target_user_id == target.id, JoinRequest.status == RequestStatus.pending.value).first()
        if pending:
            raise ConflictError("A request is already pending for this person.")

        request = JoinRequest(type=kind, requester_id=actor_id, target_user_id=target.id, status=RequestStatus.pending.value, **{fk: group_id})
        self.db.add(request)
        audit_service.record(self.db, actor_id, f"{kind}_invite_sent", kind, group_id, {"target_user_id": str(target.id)})
        notify(self.db, target.id, f"{kind}_invite", f"You've been invited to join {group.name}", link="/community/requests")
        self.db.commit()
        self.db.refresh(request)
        return request

    def respond_to_group_request(self, kind: str, user_id: uuid.UUID, request_id: uuid.UUID, accept: bool) -> None:
        request = self._get_request(request_id)
        if request.type != kind or request.status != RequestStatus.pending.value or request.target_user_id != user_id:
            raise NotFoundError("Request not found.")

        fk = self._group_fk(kind)
        group_id = getattr(request, fk)
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()

        if accept:
            if group.challenge_id is not None and not self._active_challenge_membership(group.challenge_id, user_id):
                raise ValidationError("You are no longer a participant of the parent Church Challenge.")

            existing = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == group_id, MemberModel.user_id == user_id).first()
            if existing:
                existing.status = GroupMemberStatus.active.value
            else:
                self.db.add(MemberModel(**{fk: group_id, "user_id": user_id, "role": GroupMemberRole.member.value, "status": GroupMemberStatus.active.value}))
            request.status = RequestStatus.approved.value
            notify(self.db, request.requester_id, f"{kind}_request_approved", f"Your invitation to {group.name} was accepted", link=f"/community/{'family' if kind == 'family' else 'buddy-group'}/{group_id}")
        else:
            request.status = RequestStatus.declined.value
            notify(self.db, request.requester_id, f"{kind}_request_declined", f"Your invitation to {group.name} was declined")

        request.responded_at = datetime.now(timezone.utc)
        request.responded_by_id = user_id
        self.db.commit()

    def remove_group_member(self, kind: str, actor_id: uuid.UUID, group_id: uuid.UUID, target_rooted_id: str) -> None:
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise NotFoundError("Group not found.")
        if group.owner_id != actor_id:
            raise ForbiddenError("Only the owner can remove members.")

        target = self._get_user_by_rooted_id(target_rooted_id)
        if target.id == group.owner_id:
            raise ValidationError("The owner cannot be removed. Delete the group instead.")
        member = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == group_id, MemberModel.user_id == target.id, MemberModel.status == GroupMemberStatus.active.value).first()
        if not member:
            raise NotFoundError("This person is not in the group.")
        member.status = GroupMemberStatus.removed.value
        audit_service.record(self.db, actor_id, f"{kind}_member_removed", kind, group_id, {"user_id": str(target.id)})
        self.db.commit()

    def leave_group(self, kind: str, user_id: uuid.UUID, group_id: uuid.UUID) -> None:
        GroupModel = self._group_model(kind)
        MemberModel = self._member_model(kind)
        fk = self._group_fk(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise NotFoundError("Group not found.")
        if group.owner_id == user_id:
            raise ValidationError("The owner cannot leave. Delete the group instead.")
        member = self._require_group_membership(kind, group_id, user_id)
        member.status = GroupMemberStatus.left.value
        self.db.commit()

    def delete_group(self, kind: str, user_id: uuid.UUID, group_id: uuid.UUID) -> None:
        GroupModel = self._group_model(kind)
        group = self.db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise NotFoundError("Group not found.")
        if group.owner_id != user_id:
            raise ForbiddenError("Only the owner can delete this group.")
        audit_service.record(self.db, user_id, f"{kind}_deleted", kind, group_id, {"name": group.name})
        self.db.delete(group)
        self.db.commit()

    # -----------------------------------------------------------------
    # Requests - unified incoming/outgoing across challenge/family/buddy
    # -----------------------------------------------------------------
    def _get_request(self, request_id: uuid.UUID) -> JoinRequest:
        request = self.db.query(JoinRequest).filter(JoinRequest.id == request_id).first()
        if not request:
            raise NotFoundError("Request not found.")
        return request

    def list_my_requests(self, user_id: uuid.UUID) -> dict:
        incoming = self.db.query(JoinRequest).filter(JoinRequest.target_user_id == user_id, JoinRequest.status == RequestStatus.pending.value).all()
        outgoing = self.db.query(JoinRequest).filter(JoinRequest.requester_id == user_id, JoinRequest.status == RequestStatus.pending.value).all()

        def scope_name(r: JoinRequest) -> str:
            if r.type == RequestType.challenge.value:
                c = self.db.query(ChurchChallenge).filter(ChurchChallenge.id == r.challenge_id).first()
                return c.name if c else "Church Challenge"
            if r.type == RequestType.family.value:
                f = self.db.query(Family).filter(Family.id == r.family_id).first()
                return f.name if f else "Family"
            g = self.db.query(BuddyGroup).filter(BuddyGroup.id == r.buddy_group_id).first()
            return g.name if g else "Buddy Group"

        def to_out(r: JoinRequest, direction: str) -> JoinRequestOut:
            other_id = r.target_user_id if direction == "outgoing" and r.type != RequestType.challenge.value else r.requester_id
            other = self.db.query(User).filter(User.id == other_id).first() if other_id else None
            return JoinRequestOut(
                id=r.id, type=r.type, direction=direction, challenge_id=r.challenge_id, family_id=r.family_id,
                buddy_group_id=r.buddy_group_id, scope_name=scope_name(r),
                other_party_user_id=other.user_id if other else None, other_party_name=other.name if other else None,
                status=r.status, created_at=r.created_at,
            )

        return {
            "incoming": [to_out(r, "incoming") for r in incoming],
            "outgoing": [to_out(r, "outgoing") for r in outgoing],
        }

    def cancel_request(self, user_id: uuid.UUID, request_id: uuid.UUID) -> None:
        request = self._get_request(request_id)
        if request.requester_id != user_id or request.status != RequestStatus.pending.value:
            raise NotFoundError("Request not found.")
        if request.type == RequestType.challenge.value:
            member = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == request.challenge_id, ChallengeMember.user_id == user_id).first()
            if member:
                self.db.delete(member)
        request.status = RequestStatus.cancelled.value
        self.db.commit()

    # -----------------------------------------------------------------
    # Rewards
    # -----------------------------------------------------------------
    def admin_create_reward(self, actor_id: uuid.UUID, challenge_id: uuid.UUID, payload: RewardCreate) -> ChallengeReward:
        self._get_challenge(challenge_id)
        reward = ChallengeReward(challenge_id=challenge_id, **payload.model_dump())
        self.db.add(reward)
        audit_service.record(self.db, actor_id, "reward_created", "challenge_reward", None, {"name": reward.name, "challenge_id": str(challenge_id)})
        self.db.commit()
        self.db.refresh(reward)
        return reward

    def admin_list_rewards(self, challenge_id: uuid.UUID) -> list[RewardOut]:
        rows = self.db.query(ChallengeReward).filter(ChallengeReward.challenge_id == challenge_id).order_by(ChallengeReward.requirement_value).all()
        return [RewardOut(id=r.id, challenge_id=r.challenge_id, name=r.name, description=r.description, requirement_type=r.requirement_type, requirement_value=r.requirement_value, badge_icon=r.badge_icon) for r in rows]

    def admin_delete_reward(self, actor_id: uuid.UUID, reward_id: uuid.UUID) -> None:
        reward = self.db.query(ChallengeReward).filter(ChallengeReward.id == reward_id).first()
        if not reward:
            raise NotFoundError("Reward not found.")
        audit_service.record(self.db, actor_id, "reward_deleted", "challenge_reward", None, {"name": reward.name})
        self.db.delete(reward)
        self.db.commit()

    def list_my_rewards(self, user_id: uuid.UUID, challenge_id: uuid.UUID) -> list[RewardEarnedOut]:
        self._require_active_participant(challenge_id, user_id)
        stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
        streak = stats.current_streak if stats else 0
        longest = stats.longest_streak if stats else 0
        completion_pct = self._my_progress_percent(user_id)
        rewards = self.admin_list_rewards(challenge_id)
        out = []
        for r in rewards:
            if r.requirement_type == "streak":
                earned = longest >= r.requirement_value or streak >= r.requirement_value
            else:
                earned = completion_pct >= r.requirement_value
            out.append(RewardEarnedOut(**r.model_dump(), earned=earned))
        return out

    # -----------------------------------------------------------------
    # Encouragement
    # -----------------------------------------------------------------
    def send_group_encouragement(self, kind: str, actor_id: uuid.UUID, group_id: uuid.UUID, payload: EncouragementCreate) -> Encouragement:
        self._require_group_membership(kind, group_id, actor_id)
        if payload.message not in _ENCOURAGEMENT_MESSAGES:
            raise ValidationError("Please choose one of the suggested encouragement messages.")

        to_user_id = None
        if payload.to_user_id:
            target = self._get_user_by_rooted_id(payload.to_user_id)
            self._require_group_membership(kind, group_id, target.id)
            to_user_id = target.id

        fk = self._group_fk(kind)
        encouragement = Encouragement(from_user_id=actor_id, to_user_id=to_user_id, message=payload.message, **{fk: group_id})
        self.db.add(encouragement)
        self.db.commit()
        self.db.refresh(encouragement)
        return encouragement

    # -----------------------------------------------------------------
    # Leaderboard
    # -----------------------------------------------------------------
    def _leaderboard_scope_labels(self) -> dict[str, str]:
        labels = {"individual": "Individual", "family": "Family", "buddy": "Buddy Group"}
        for g in self.db.query(RootedGroup).filter(RootedGroup.is_active.is_(True)).order_by(RootedGroup.sort_order).all():
            labels[g.name] = g.name
        return labels

    def _default_ranking_limit(self, scope: str) -> int:
        return _DEFAULT_RANKING_LIMITS.get(scope, _DEFAULT_RANKING_LIMIT)

    def _ranking_limit(self, challenge_id: uuid.UUID, scope: str) -> int:
        row = self.db.query(LeaderboardConfig).filter(LeaderboardConfig.challenge_id == challenge_id, LeaderboardConfig.scope == scope).first()
        return row.ranking_limit if row else self._default_ranking_limit(scope)

    def admin_list_leaderboard_config(self, challenge_id: uuid.UUID) -> list[LeaderboardConfigOut]:
        self._get_challenge(challenge_id)
        labels = self._leaderboard_scope_labels()
        return [
            LeaderboardConfigOut(scope=scope, label=label, ranking_limit=self._ranking_limit(challenge_id, scope))
            for scope, label in labels.items()
        ]

    def admin_set_leaderboard_config(self, actor_id: uuid.UUID, challenge_id: uuid.UUID, scope: str, payload: LeaderboardConfigUpdate) -> LeaderboardConfigOut:
        self._get_challenge(challenge_id)
        labels = self._leaderboard_scope_labels()
        if scope not in labels:
            raise NotFoundError("Unknown leaderboard scope.")
        row = self.db.query(LeaderboardConfig).filter(LeaderboardConfig.challenge_id == challenge_id, LeaderboardConfig.scope == scope).first()
        if row:
            row.ranking_limit = payload.ranking_limit
        else:
            row = LeaderboardConfig(challenge_id=challenge_id, scope=scope, ranking_limit=payload.ranking_limit)
            self.db.add(row)
        audit_service.record(self.db, actor_id, "leaderboard_config_updated", "church_challenge", challenge_id, {"scope": scope, "ranking_limit": payload.ranking_limit})
        self.db.commit()
        return LeaderboardConfigOut(scope=scope, label=labels[scope], ranking_limit=row.ranking_limit)

    def get_leaderboard(self, challenge_id: uuid.UUID, scope: str) -> LeaderboardOut:
        self._get_challenge(challenge_id)
        labels = self._leaderboard_scope_labels()
        if scope not in labels:
            raise NotFoundError("Unknown leaderboard scope.")
        limit = self._ranking_limit(challenge_id, scope)

        raw: list[tuple[str, str, int]] = []  # (entry_id, name, progress_percent)

        if scope == "individual":
            members = self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.status == ChallengeMemberStatus.active.value).all()
            for m in members:
                user = self.db.query(User).filter(User.id == m.user_id).first()
                if user:
                    raw.append((user.user_id, user.name, self._my_progress_percent(user.id)))
        elif scope == "family":
            families = self.db.query(Family).filter(Family.challenge_id == challenge_id).all()
            for fam in families:
                members = self.db.query(FamilyMember).filter(FamilyMember.family_id == fam.id, FamilyMember.status == GroupMemberStatus.active.value).all()
                if not members:
                    continue
                avg = round(sum(self._my_progress_percent(fm.user_id) for fm in members) / len(members))
                raw.append((str(fam.id), fam.name, avg))
        elif scope == "buddy":
            groups = self.db.query(BuddyGroup).filter(BuddyGroup.challenge_id == challenge_id).all()
            for grp in groups:
                members = self.db.query(BuddyMember).filter(BuddyMember.buddy_group_id == grp.id, BuddyMember.status == GroupMemberStatus.active.value).all()
                if not members:
                    continue
                avg = round(sum(self._my_progress_percent(bm.user_id) for bm in members) / len(members))
                raw.append((str(grp.id), grp.name, avg))
        else:
            rooted_group = self.db.query(RootedGroup).filter(RootedGroup.name == scope).first()
            if rooted_group:
                member_user_ids = {m.user_id for m in self.db.query(ChallengeMember).filter(ChallengeMember.challenge_id == challenge_id, ChallengeMember.status == ChallengeMemberStatus.active.value).all()}
                group_user_ids = {ugm.user_id for ugm in self.db.query(UserGroupMembership).filter(UserGroupMembership.group_id == rooted_group.id).all()}
                for user_id in member_user_ids & group_user_ids:
                    user = self.db.query(User).filter(User.id == user_id).first()
                    if user:
                        raw.append((user.user_id, user.name, self._my_progress_percent(user.id)))

        raw.sort(key=lambda t: t[2], reverse=True)
        entries = [
            LeaderboardEntryOut(rank=i + 1, entry_id=entry_id, name=name, progress_percent=pct)
            for i, (entry_id, name, pct) in enumerate(raw[:limit])
        ]
        return LeaderboardOut(scope=scope, label=labels[scope], ranking_limit=limit, entries=entries)
