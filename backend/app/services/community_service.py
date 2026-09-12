"""Church and Fellowship - standalone community entities, same
Request -> Approval -> Membership pattern as Family/Buddy (see
ChallengeService), sharing the same JoinRequest table via `type`.

Only Super Admin may create a Church or Fellowship (enforced by
`require_super_admin` on the POST /community/church and
/community/fellowship routes) - an `admin` already manages exactly one
organization and can never create another. Members only ever join one.

ROLE ARCHITECTURE (final): exactly 3 roles - member, admin, super_admin.
`admin` is ALWAYS scoped to exactly one Church or Fellowship, tracked in
AdminOrganizationAssignment - never inferred from ChurchMember/
FellowshipMember.role, which is kept only as cosmetic/display membership
metadata. See _is_org_admin, the single source of truth for "is this user
the assigned admin of this organization"."""
import secrets
import string
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.models.user import User, UserRole
from app.models.church import Church, ChurchMember
from app.models.fellowship import Fellowship, FellowshipMember
from app.models.admin_assignment import AdminOrganizationAssignment
from app.models.group import RootedGroup, UserGroupMembership
from app.models.challenge import JoinRequest, RequestStatus
from app.services import audit_service
from app.services.notification_service import notify
from app.schemas.community import (
    ChurchCreate, ChurchOut, ChurchDetailOut, ChurchMemberOut, ChurchUpdate,
    FellowshipCreate, FellowshipOut, FellowshipDetailOut, FellowshipUpdate,
    RootedGroupOut,
)

_CODE_ALPHABET = "".join(c for c in string.ascii_uppercase + string.digits if c not in "01OI")


class CommunityService:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------------------------------
    # Shared helpers (kind = "church" | "fellowship")
    # -----------------------------------------------------------------
    def _entity_model(self, kind: str):
        return Church if kind == "church" else Fellowship

    def _member_model(self, kind: str):
        return ChurchMember if kind == "church" else FellowshipMember

    def _fk(self, kind: str) -> str:
        return "church_id" if kind == "church" else "fellowship_id"

    def _member_count(self, kind: str, entity_id: uuid.UUID) -> int:
        MemberModel = self._member_model(kind)
        fk = self._fk(kind)
        return self.db.query(MemberModel).filter(getattr(MemberModel, fk) == entity_id, MemberModel.status == "active").count()

    def _my_role(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
        """Cosmetic/display membership role only (church_member/
        fellowship_member.role) - NEVER the authorization source for admin
        actions. See _is_org_admin for that."""
        MemberModel = self._member_model(kind)
        fk = self._fk(kind)
        row = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == entity_id, MemberModel.user_id == user_id, MemberModel.status == "active").first()
        return row.role if row else None

    def _is_platform_super_admin(self, user_id: uuid.UUID) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        return bool(user and user.role == UserRole.super_admin)

    def _get_admin_assignment(self, user_id: uuid.UUID) -> AdminOrganizationAssignment | None:
        return self.db.query(AdminOrganizationAssignment).filter(AdminOrganizationAssignment.user_id == user_id).first()

    def _is_org_admin(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """The ONLY source of truth for "is this user allowed to administer
        this Church/Fellowship": role=super_admin (platform-wide override),
        or role=admin AND their one AdminOrganizationAssignment points at
        exactly this organization. ChurchMember/FellowshipMember.role is
        never consulted here - being a plain member of an org (or even its
        historical 'owner' membership row) grants no admin authority."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        if user.role == UserRole.super_admin:
            return True
        if user.role != UserRole.admin:
            return False
        assignment = self._get_admin_assignment(user_id)
        if not assignment or assignment.organization_type != kind:
            return False
        fk = self._fk(kind)
        return getattr(assignment, fk) == entity_id

    def _require_membership(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID):
        """Allowed to VIEW this org - its assigned admin, Super Admin, or a
        regular member. Returns a display-only role string."""
        if self._is_org_admin(kind, entity_id, user_id):
            return "admin"
        role = self._my_role(kind, entity_id, user_id)
        if not role:
            raise ForbiddenError(f"You are not a member of this {kind}.")
        return role

    def _require_admin(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID):
        if not self._is_org_admin(kind, entity_id, user_id):
            raise ForbiddenError("Only this organization's assigned admin (or Super Admin) can do this.")
        return "admin"

    def assign_org_admin(
        self, actor_id: uuid.UUID, kind: str, entity_id: uuid.UUID,
        admin_rooted_id: str | None = None, admin_email: str | None = None, reassign: bool = False,
    ) -> User:
        """The ONLY way to make someone a Church/Fellowship's ADMIN. The
        target must already be an existing Rooted member - there is no
        "pending invite" state; an unresolvable email fails immediately
        and clearly, matching the final architecture exactly. Super Admin
        can never be assigned (their role is never downgraded), and a
        person who already admins a DIFFERENT organization is rejected
        unless the caller explicitly passes reassign=True."""
        if admin_rooted_id:
            target = self._get_user_by_rooted_id(admin_rooted_id)
        elif admin_email:
            from app.repositories.user_repository import UserRepository
            normalized = admin_email.strip().lower()
            target = UserRepository(self.db).get_by_email(normalized)
            if not target:
                raise NotFoundError(
                    "No Rooted member exists with this email. They must register as a Rooted member first, using this exact registered email."
                )
        else:
            raise ValidationError("Provide either an admin_rooted_id or an admin_email.")

        if target.role == UserRole.super_admin:
            raise ValidationError("The Super Admin cannot be assigned as an organization Admin.")

        fk = self._fk(kind)

        target_assignment = self._get_admin_assignment(target.id)
        if target_assignment and getattr(target_assignment, fk) != entity_id:
            if not reassign:
                raise ConflictError(f"{target.name} already manages another organization. Reassign them explicitly if you want to move them here.")
            self.db.delete(target_assignment)
            self.db.flush()
            target_assignment = None

        current_assignment = self.db.query(AdminOrganizationAssignment).filter(getattr(AdminOrganizationAssignment, fk) == entity_id).first()
        if current_assignment and current_assignment.user_id != target.id:
            previous_admin = self.db.query(User).filter(User.id == current_assignment.user_id).first()
            if previous_admin and previous_admin.role == UserRole.admin:
                previous_admin.role = UserRole.member
            self.db.delete(current_assignment)
            self.db.flush()
            current_assignment = None

        if not target_assignment and not current_assignment:
            self.db.add(AdminOrganizationAssignment(user_id=target.id, organization_type=kind, **{fk: entity_id}))

        target.role = UserRole.admin

        # Keep a membership row for display/continuity - cosmetic only,
        # never consulted for authorization (see _is_org_admin).
        MemberModel = self._member_model(kind)
        member = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == entity_id, MemberModel.user_id == target.id).first()
        if member:
            member.status = "active"
            member.role = "owner"
        else:
            self.db.add(MemberModel(**{fk: entity_id, "user_id": target.id, "role": "owner", "status": "active"}))

        # Legacy display field kept in sync.
        entity_obj = self._get_church(entity_id) if kind == "church" else self._get_fellowship(entity_id)
        entity_obj.owner_id = target.id

        audit_service.record(self.db, actor_id, f"{kind}_admin_assigned", kind, entity_id, {"admin_user_id": str(target.id), "reassigned": reassign})
        # Sessions in this app run with autoflush=False - without an
        # explicit flush here, the new assignment row (and the role/member
        # changes above) would stay invisible to any query run before the
        # caller's own commit, including any the caller runs right after
        # calling this method.
        self.db.flush()
        return target

    # -----------------------------------------------------------------
    # Active calendar - which org's own reading plan/quiz bank a member
    # follows (both null = the shared platform default).
    # -----------------------------------------------------------------
    def list_calendar_options(self, user_id: uuid.UUID) -> list[dict]:
        from app.models.reading_plan import ReadingPlan, compute_scope_key

        options: list[dict] = []
        for row in self.db.query(ChurchMember).filter(ChurchMember.user_id == user_id, ChurchMember.status == "active").all():
            church = self.db.query(Church).filter(Church.id == row.church_id).first()
            if not church:
                continue
            has_calendar = self.db.query(ReadingPlan.id).filter(ReadingPlan.scope_key == compute_scope_key(church_id=church.id)).first() is not None
            if has_calendar:
                options.append({"kind": "church", "org_id": church.id, "name": church.name})
        for row in self.db.query(FellowshipMember).filter(FellowshipMember.user_id == user_id, FellowshipMember.status == "active").all():
            fellowship = self.db.query(Fellowship).filter(Fellowship.id == row.fellowship_id).first()
            if not fellowship:
                continue
            has_calendar = self.db.query(ReadingPlan.id).filter(ReadingPlan.scope_key == compute_scope_key(fellowship_id=fellowship.id)).first() is not None
            if has_calendar:
                options.append({"kind": "fellowship", "org_id": fellowship.id, "name": fellowship.name})
        return options

    def set_active_calendar(self, user_id: uuid.UUID, kind: str | None, org_id: uuid.UUID | None) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found.")
        if kind is None:
            user.active_calendar_church_id = None
            user.active_calendar_fellowship_id = None
        elif kind == "church":
            self._require_membership("church", org_id, user_id)
            user.active_calendar_church_id = org_id
            user.active_calendar_fellowship_id = None
        elif kind == "fellowship":
            self._require_membership("fellowship", org_id, user_id)
            user.active_calendar_fellowship_id = org_id
            user.active_calendar_church_id = None
        else:
            raise ValidationError("kind must be 'church' or 'fellowship'.")
        self.db.commit()

    def _get_user_by_rooted_id(self, rooted_id: str) -> User:
        user = self.db.query(User).filter(User.user_id == rooted_id.strip().upper(), User.deleted_at.is_(None)).first()
        if not user:
            raise NotFoundError("Rooted ID not found.")
        return user

    def _get_request(self, request_id: uuid.UUID) -> JoinRequest:
        request = self.db.query(JoinRequest).filter(JoinRequest.id == request_id).first()
        if not request:
            raise NotFoundError("Request not found.")
        return request

    # -----------------------------------------------------------------
    # Church
    # -----------------------------------------------------------------
    def _generate_church_code(self) -> str:
        for _ in range(20):
            code = "ROOTED-" + "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
            if not self.db.query(Church).filter(Church.church_code == code).first():
                return code
        raise RuntimeError("Could not allocate a unique church code")

    def admin_create_church(self, actor_id: uuid.UUID, payload: ChurchCreate) -> Church:
        """Super Admin only (enforced at the API layer). If admin_rooted_id
        or admin_email is given, that person must already be an existing
        Rooted member - assign_org_admin raises immediately and clearly if
        not; there is no pending/placeholder state. Without either, the
        church has no admin yet until Super Admin assigns one."""
        church = Church(
            name=payload.name, description=payload.description, address=payload.address,
            owner_id=actor_id, church_code=self._generate_church_code(), privacy=payload.privacy,
        )
        self.db.add(church)
        self.db.flush()
        assigned_admin = None
        if payload.admin_rooted_id or payload.admin_email:
            assigned_admin = self.assign_org_admin(actor_id, "church", church.id, payload.admin_rooted_id, payload.admin_email)
        audit_service.record(self.db, actor_id, "church_created", "church", church.id, {"name": church.name, "assigned_admin": str(assigned_admin.id) if assigned_admin else None})
        self.db.commit()
        self.db.refresh(church)
        return church

    def _get_church(self, church_id: uuid.UUID) -> Church:
        church = self.db.query(Church).filter(Church.id == church_id).first()
        if not church:
            raise NotFoundError("Church not found.")
        return church

    def _get_org_admin_info(self, kind: str, entity_id: uuid.UUID):
        from app.schemas.community import OrgAdminOut
        fk = self._fk(kind)
        assignment = self.db.query(AdminOrganizationAssignment).filter(getattr(AdminOrganizationAssignment, fk) == entity_id).first()
        if not assignment:
            return None
        admin_user = self.db.query(User).filter(User.id == assignment.user_id).first()
        if not admin_user:
            return None
        return OrgAdminOut(user_id=admin_user.user_id, name=admin_user.name, email=admin_user.email)

    def remove_org_admin(self, actor_id: uuid.UUID, kind: str, entity_id: uuid.UUID) -> None:
        fk = self._fk(kind)
        assignment = self.db.query(AdminOrganizationAssignment).filter(getattr(AdminOrganizationAssignment, fk) == entity_id).first()
        if not assignment:
            return
        admin_user = self.db.query(User).filter(User.id == assignment.user_id).first()
        if admin_user and admin_user.role == UserRole.admin:
            admin_user.role = UserRole.member
        self.db.delete(assignment)
        audit_service.record(self.db, actor_id, f"{kind}_admin_removed", kind, entity_id, {})

    def _to_church_out(self, church: Church, user_id: uuid.UUID | None) -> ChurchOut:
        my_role = self._my_role("church", church.id, user_id) if user_id else None
        # user_id=None means "Super Admin's own platform-wide list" (see
        # admin_list_all_churches, gated by require_super_admin) - always
        # show the admin there; otherwise only this church's own admin sees it.
        show_admin_fields = user_id is None or self._is_org_admin("church", church.id, user_id)
        return ChurchOut(
            id=church.id, name=church.name, church_code=church.church_code, description=church.description,
            address=church.address, privacy=church.privacy, status=church.status,
            member_count=self._member_count("church", church.id), my_role=my_role,
            admin=self._get_org_admin_info("church", church.id) if show_admin_fields else None,
            created_at=church.created_at,
        )

    def list_discoverable_churches(self, user_id: uuid.UUID) -> list[ChurchOut]:
        my_ids = {m.church_id for m in self.db.query(ChurchMember).filter(ChurchMember.user_id == user_id, ChurchMember.status == "active").all()}
        churches = self.db.query(Church).filter(Church.status == "active", Church.privacy == "public").order_by(Church.created_at.desc()).all()
        return [self._to_church_out(c, user_id) for c in churches if c.id not in my_ids]

    def admin_list_all_churches(self) -> list[ChurchOut]:
        churches = self.db.query(Church).order_by(Church.created_at.desc()).all()
        return [self._to_church_out(c, None) for c in churches]

    def admin_update_church(self, actor_id: uuid.UUID, church_id: uuid.UUID, payload: ChurchUpdate) -> Church:
        church = self._get_church(church_id)
        changes = payload.model_dump(exclude_unset=True)
        admin_email = changes.pop("admin_email", None)
        for field, value in changes.items():
            if value is not None:
                setattr(church, field, value)
        if admin_email is not None:
            normalized = admin_email.strip()
            if normalized:
                self.assign_org_admin(actor_id, "church", church.id, admin_email=normalized, reassign=True)
            else:
                self.remove_org_admin(actor_id, "church", church.id)
        audit_service.record(self.db, actor_id, "church_updated", "church", church.id, changes)
        self.db.commit()
        self.db.refresh(church)
        return church

    def admin_set_church_status(self, actor_id: uuid.UUID, church_id: uuid.UUID, status: str) -> Church:
        church = self._get_church(church_id)
        church.status = status
        audit_service.record(self.db, actor_id, "church_status_changed", "church", church.id, {"status": status})
        self.db.commit()
        self.db.refresh(church)
        return church

    def admin_delete_church(self, actor_id: uuid.UUID, church_id: uuid.UUID) -> None:
        church = self._get_church(church_id)
        audit_service.record(self.db, actor_id, "church_deleted", "church", church.id, {"name": church.name})
        self.db.delete(church)
        self.db.commit()

    def list_my_churches(self, user_id: uuid.UUID) -> list[ChurchOut]:
        rows = self.db.query(ChurchMember).filter(ChurchMember.user_id == user_id, ChurchMember.status == "active").all()
        churches = [self._get_church(r.church_id) for r in rows]
        return [self._to_church_out(c, user_id) for c in churches]

    def get_church_detail(self, user_id: uuid.UUID, church_id: uuid.UUID) -> ChurchDetailOut:
        church = self._get_church(church_id)
        my_role = self._my_role("church", church_id, user_id)
        members: list[ChurchMemberOut] = []
        if my_role:
            rows = self.db.query(ChurchMember, User).join(User, User.id == ChurchMember.user_id).filter(ChurchMember.church_id == church_id, ChurchMember.status == "active").all()
            members = [ChurchMemberOut(user_id=u.user_id, name=u.name, photo_url=u.photo_url, role=m.role, joined_at=m.joined_at) for m, u in rows]
        out = self._to_church_out(church, user_id)
        return ChurchDetailOut(**out.model_dump(), members=members)

    def find_church_by_code(self, church_code: str) -> ChurchOut | None:
        church = self.db.query(Church).filter(Church.church_code == church_code.strip().upper()).first()
        return church

    def list_pending_church_requests(self, actor_id: uuid.UUID, church_id: uuid.UUID) -> list[dict]:
        self._require_admin("church", church_id, actor_id)
        rows = self.db.query(JoinRequest, User).join(User, User.id == JoinRequest.requester_id).filter(
            JoinRequest.type == "church", JoinRequest.church_id == church_id, JoinRequest.status == RequestStatus.pending.value
        ).order_by(JoinRequest.created_at).all()
        return [{"request_id": r.id, "user_id": u.user_id, "name": u.name, "requested_at": r.created_at} for r, u in rows]

    def request_join_church(self, user_id: uuid.UUID, church_id: uuid.UUID | None = None, church_code: str | None = None) -> JoinRequest:
        church = self._get_church(church_id) if church_id else self.find_church_by_code(church_code or "")
        if not church:
            raise NotFoundError("Church not found.")
        if church.status != "active":
            raise ValidationError("This church is not accepting new members.")

        existing = self.db.query(ChurchMember).filter(ChurchMember.church_id == church.id, ChurchMember.user_id == user_id).first()
        if existing and existing.status == "active":
            raise ConflictError("You already belong to this church.")

        pending = self.db.query(JoinRequest).filter(JoinRequest.type == "church", JoinRequest.church_id == church.id, JoinRequest.requester_id == user_id, JoinRequest.status == RequestStatus.pending.value).first()
        if pending:
            raise ConflictError("Your request to join is already pending.")

        request = JoinRequest(type="church", requester_id=user_id, church_id=church.id, status=RequestStatus.pending.value)
        self.db.add(request)
        audit_service.record(self.db, user_id, "church_join_requested", "church", church.id, {"user_id": str(user_id)})
        requester = self.db.query(User).filter(User.id == user_id).first()
        notify(self.db, church.owner_id, "church_join_requested", f"{requester.name if requester else 'Someone'} wants to join {church.name}", link=f"/community/church/{church.id}")
        self.db.commit()
        self.db.refresh(request)
        return request

    def respond_to_church_request(self, actor_id: uuid.UUID, request_id: uuid.UUID, approve: bool) -> None:
        request = self._get_request(request_id)
        if request.type != "church" or request.status != RequestStatus.pending.value:
            raise NotFoundError("Request not found.")
        self._require_admin("church", request.church_id, actor_id)

        if approve:
            existing = self.db.query(ChurchMember).filter(ChurchMember.church_id == request.church_id, ChurchMember.user_id == request.requester_id).first()
            if existing:
                existing.status = "active"
            else:
                self.db.add(ChurchMember(church_id=request.church_id, user_id=request.requester_id, role="member", status="active"))
            request.status = RequestStatus.approved.value
            audit_service.record(self.db, actor_id, "church_member_approved", "church_member", request.church_id, {"user_id": str(request.requester_id)})
            church = self._get_church(request.church_id)
            notify(self.db, request.requester_id, "church_request_approved", f"Welcome to {church.name}", link=f"/community/church/{church.id}")
        else:
            request.status = RequestStatus.declined.value
            audit_service.record(self.db, actor_id, "church_member_declined", "church_member", request.church_id, {"user_id": str(request.requester_id)})
            church = self._get_church(request.church_id)
            notify(self.db, request.requester_id, "church_request_declined", f"Your request to join {church.name} was declined")

        request.responded_at = datetime.now(timezone.utc)
        request.responded_by_id = actor_id
        self.db.commit()

    def leave_church(self, user_id: uuid.UUID, church_id: uuid.UUID) -> None:
        church = self._get_church(church_id)
        if church.owner_id == user_id:
            raise ValidationError("The owner cannot leave. Transfer ownership or delete the church instead.")
        member = self.db.query(ChurchMember).filter(ChurchMember.church_id == church_id, ChurchMember.user_id == user_id, ChurchMember.status == "active").first()
        if not member:
            raise NotFoundError("You are not a member of this church.")
        member.status = "left"
        self.db.commit()

    def remove_church_member(self, actor_id: uuid.UUID, church_id: uuid.UUID, target_rooted_id: str) -> None:
        self._require_admin("church", church_id, actor_id)
        target = self._get_user_by_rooted_id(target_rooted_id)
        church = self._get_church(church_id)
        if target.id == church.owner_id:
            raise ValidationError("The owner cannot be removed.")
        member = self.db.query(ChurchMember).filter(ChurchMember.church_id == church_id, ChurchMember.user_id == target.id, ChurchMember.status == "active").first()
        if not member:
            raise NotFoundError("This person is not a member.")
        member.status = "removed"
        audit_service.record(self.db, actor_id, "church_member_removed", "church_member", church_id, {"user_id": str(target.id)})
        self.db.commit()

    # -----------------------------------------------------------------
    # Fellowship
    # -----------------------------------------------------------------
    def _generate_fellowship_code(self) -> str:
        for _ in range(20):
            code = "ROOTED-" + "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
            if not self.db.query(Fellowship).filter(Fellowship.fellowship_code == code).first():
                return code
        raise RuntimeError("Could not allocate a unique fellowship code")

    def admin_create_fellowship(self, actor_id: uuid.UUID, payload: "FellowshipCreate") -> Fellowship:
        fellowship = Fellowship(
            name=payload.name, fellowship_code=self._generate_fellowship_code(), description=payload.description,
            church_id=payload.church_id, owner_id=actor_id, privacy=payload.privacy,
        )
        self.db.add(fellowship)
        self.db.flush()
        assigned_admin = None
        if payload.admin_rooted_id or payload.admin_email:
            assigned_admin = self.assign_org_admin(actor_id, "fellowship", fellowship.id, payload.admin_rooted_id, payload.admin_email)
        audit_service.record(self.db, actor_id, "fellowship_created", "fellowship", fellowship.id, {"name": fellowship.name, "assigned_admin": str(assigned_admin.id) if assigned_admin else None})
        self.db.commit()
        self.db.refresh(fellowship)
        return fellowship

    def _get_fellowship(self, fellowship_id: uuid.UUID) -> Fellowship:
        fellowship = self.db.query(Fellowship).filter(Fellowship.id == fellowship_id).first()
        if not fellowship:
            raise NotFoundError("Fellowship not found.")
        return fellowship

    def _to_fellowship_out(self, fellowship: Fellowship, user_id: uuid.UUID | None) -> FellowshipOut:
        church_name = None
        if fellowship.church_id:
            church = self.db.query(Church).filter(Church.id == fellowship.church_id).first()
            church_name = church.name if church else None
        my_role = self._my_role("fellowship", fellowship.id, user_id) if user_id else None
        show_admin_fields = user_id is None or self._is_org_admin("fellowship", fellowship.id, user_id)
        return FellowshipOut(
            id=fellowship.id, name=fellowship.name, fellowship_code=fellowship.fellowship_code, description=fellowship.description, church_id=fellowship.church_id,
            church_name=church_name, privacy=fellowship.privacy, status=fellowship.status,
            member_count=self._member_count("fellowship", fellowship.id), my_role=my_role,
            admin=self._get_org_admin_info("fellowship", fellowship.id) if show_admin_fields else None,
            created_at=fellowship.created_at,
        )

    def admin_list_all_fellowships(self) -> list[FellowshipOut]:
        fellowships = self.db.query(Fellowship).order_by(Fellowship.created_at.desc()).all()
        return [self._to_fellowship_out(f, None) for f in fellowships]

    def admin_update_fellowship(self, actor_id: uuid.UUID, fellowship_id: uuid.UUID, payload: FellowshipUpdate) -> Fellowship:
        fellowship = self._get_fellowship(fellowship_id)
        changes = payload.model_dump(exclude_unset=True)
        admin_email = changes.pop("admin_email", None)
        for field, value in changes.items():
            if value is not None:
                setattr(fellowship, field, value)
        if admin_email is not None:
            normalized = admin_email.strip()
            if normalized:
                self.assign_org_admin(actor_id, "fellowship", fellowship.id, admin_email=normalized, reassign=True)
            else:
                self.remove_org_admin(actor_id, "fellowship", fellowship.id)
        audit_service.record(self.db, actor_id, "fellowship_updated", "fellowship", fellowship.id, changes)
        self.db.commit()
        self.db.refresh(fellowship)
        return fellowship

    def admin_set_fellowship_status(self, actor_id: uuid.UUID, fellowship_id: uuid.UUID, status: str) -> Fellowship:
        fellowship = self._get_fellowship(fellowship_id)
        fellowship.status = status
        audit_service.record(self.db, actor_id, "fellowship_status_changed", "fellowship", fellowship.id, {"status": status})
        self.db.commit()
        self.db.refresh(fellowship)
        return fellowship

    def admin_delete_fellowship(self, actor_id: uuid.UUID, fellowship_id: uuid.UUID) -> None:
        fellowship = self._get_fellowship(fellowship_id)
        audit_service.record(self.db, actor_id, "fellowship_deleted", "fellowship", fellowship.id, {"name": fellowship.name})
        self.db.delete(fellowship)
        self.db.commit()

    def list_discoverable_fellowships(self, user_id: uuid.UUID) -> list[FellowshipOut]:
        my_ids = {m.fellowship_id for m in self.db.query(FellowshipMember).filter(FellowshipMember.user_id == user_id, FellowshipMember.status == "active").all()}
        fellowships = self.db.query(Fellowship).filter(Fellowship.status == "active", Fellowship.privacy == "public").order_by(Fellowship.created_at.desc()).all()
        return [self._to_fellowship_out(f, user_id) for f in fellowships if f.id not in my_ids]

    def list_my_fellowships(self, user_id: uuid.UUID) -> list[FellowshipOut]:
        rows = self.db.query(FellowshipMember).filter(FellowshipMember.user_id == user_id, FellowshipMember.status == "active").all()
        fellowships = [self._get_fellowship(r.fellowship_id) for r in rows]
        return [self._to_fellowship_out(f, user_id) for f in fellowships]

    def get_fellowship_detail(self, user_id: uuid.UUID, fellowship_id: uuid.UUID) -> FellowshipDetailOut:
        fellowship = self._get_fellowship(fellowship_id)
        my_role = self._my_role("fellowship", fellowship_id, user_id)
        members: list[ChurchMemberOut] = []
        if my_role:
            rows = self.db.query(FellowshipMember, User).join(User, User.id == FellowshipMember.user_id).filter(FellowshipMember.fellowship_id == fellowship_id, FellowshipMember.status == "active").all()
            members = [ChurchMemberOut(user_id=u.user_id, name=u.name, photo_url=u.photo_url, role=m.role, joined_at=m.joined_at) for m, u in rows]
        out = self._to_fellowship_out(fellowship, user_id)
        return FellowshipDetailOut(**out.model_dump(), members=members)

    def list_pending_fellowship_requests(self, actor_id: uuid.UUID, fellowship_id: uuid.UUID) -> list[dict]:
        self._require_admin("fellowship", fellowship_id, actor_id)
        rows = self.db.query(JoinRequest, User).join(User, User.id == JoinRequest.requester_id).filter(
            JoinRequest.type == "fellowship", JoinRequest.fellowship_id == fellowship_id, JoinRequest.status == RequestStatus.pending.value
        ).order_by(JoinRequest.created_at).all()
        return [{"request_id": r.id, "user_id": u.user_id, "name": u.name, "requested_at": r.created_at} for r, u in rows]

    def find_fellowship_by_code(self, fellowship_code: str) -> Fellowship | None:
        return self.db.query(Fellowship).filter(Fellowship.fellowship_code == fellowship_code.strip().upper()).first()

    def request_join_fellowship(self, user_id: uuid.UUID, fellowship_id: uuid.UUID | None = None, fellowship_code: str | None = None) -> JoinRequest:
        fellowship = self._get_fellowship(fellowship_id) if fellowship_id else self.find_fellowship_by_code(fellowship_code or "")
        if not fellowship:
            raise NotFoundError("Fellowship not found.")
        if fellowship.status != "active":
            raise ValidationError("This fellowship is not accepting new members.")

        existing = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == fellowship.id, FellowshipMember.user_id == user_id).first()
        if existing and existing.status == "active":
            raise ConflictError("You already belong to this fellowship.")

        pending = self.db.query(JoinRequest).filter(JoinRequest.type == "fellowship", JoinRequest.fellowship_id == fellowship.id, JoinRequest.requester_id == user_id, JoinRequest.status == RequestStatus.pending.value).first()
        if pending:
            raise ConflictError("Your request to join is already pending.")

        request = JoinRequest(type="fellowship", requester_id=user_id, fellowship_id=fellowship.id, status=RequestStatus.pending.value)
        self.db.add(request)
        audit_service.record(self.db, user_id, "fellowship_join_requested", "fellowship", fellowship.id, {"user_id": str(user_id)})
        requester = self.db.query(User).filter(User.id == user_id).first()
        notify(self.db, fellowship.owner_id, "fellowship_join_requested", f"{requester.name if requester else 'Someone'} wants to join {fellowship.name}", link=f"/community/fellowship/{fellowship.id}")
        self.db.commit()
        self.db.refresh(request)
        return request

    def respond_to_fellowship_request(self, actor_id: uuid.UUID, request_id: uuid.UUID, approve: bool) -> None:
        request = self._get_request(request_id)
        if request.type != "fellowship" or request.status != RequestStatus.pending.value:
            raise NotFoundError("Request not found.")
        self._require_admin("fellowship", request.fellowship_id, actor_id)

        if approve:
            existing = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == request.fellowship_id, FellowshipMember.user_id == request.requester_id).first()
            if existing:
                existing.status = "active"
            else:
                self.db.add(FellowshipMember(fellowship_id=request.fellowship_id, user_id=request.requester_id, role="member", status="active"))
            request.status = RequestStatus.approved.value
            audit_service.record(self.db, actor_id, "fellowship_member_approved", "fellowship_member", request.fellowship_id, {"user_id": str(request.requester_id)})
            fellowship = self._get_fellowship(request.fellowship_id)
            notify(self.db, request.requester_id, "fellowship_request_approved", f"Welcome to {fellowship.name}", link=f"/community/fellowship/{fellowship.id}")
        else:
            request.status = RequestStatus.declined.value
            audit_service.record(self.db, actor_id, "fellowship_member_declined", "fellowship_member", request.fellowship_id, {"user_id": str(request.requester_id)})
            fellowship = self._get_fellowship(request.fellowship_id)
            notify(self.db, request.requester_id, "fellowship_request_declined", f"Your request to join {fellowship.name} was declined")

        request.responded_at = datetime.now(timezone.utc)
        request.responded_by_id = actor_id
        self.db.commit()

    def leave_fellowship(self, user_id: uuid.UUID, fellowship_id: uuid.UUID) -> None:
        fellowship = self._get_fellowship(fellowship_id)
        if fellowship.owner_id == user_id:
            raise ValidationError("The owner cannot leave. Transfer ownership or delete the fellowship instead.")
        member = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == fellowship_id, FellowshipMember.user_id == user_id, FellowshipMember.status == "active").first()
        if not member:
            raise NotFoundError("You are not a member of this fellowship.")
        member.status = "left"
        self.db.commit()

    def remove_fellowship_member(self, actor_id: uuid.UUID, fellowship_id: uuid.UUID, target_rooted_id: str) -> None:
        self._require_admin("fellowship", fellowship_id, actor_id)
        target = self._get_user_by_rooted_id(target_rooted_id)
        fellowship = self._get_fellowship(fellowship_id)
        if target.id == fellowship.owner_id:
            raise ValidationError("The owner cannot be removed.")
        member = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == fellowship_id, FellowshipMember.user_id == target.id, FellowshipMember.status == "active").first()
        if not member:
            raise NotFoundError("This person is not a member.")
        member.status = "removed"
        audit_service.record(self.db, actor_id, "fellowship_member_removed", "fellowship_member", fellowship_id, {"user_id": str(target.id)})
        self.db.commit()

    # -----------------------------------------------------------------
    # Rooted Group (Sunday / Blazer / Youth / Men / Women)
    # -----------------------------------------------------------------
    def list_groups(self) -> list[RootedGroupOut]:
        rows = self.db.query(RootedGroup).filter(RootedGroup.is_active.is_(True)).order_by(RootedGroup.sort_order).all()
        return [RootedGroupOut(id=g.id, name=g.name, sort_order=g.sort_order) for g in rows]

    def get_my_group_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        rows = self.db.query(UserGroupMembership).filter(UserGroupMembership.user_id == user_id).all()
        return [r.group_id for r in rows]

    def set_my_groups(self, user_id: uuid.UUID, group_ids: list[uuid.UUID]) -> None:
        valid_ids = {g.id for g in self.db.query(RootedGroup).filter(RootedGroup.id.in_(group_ids)).all()} if group_ids else set()
        self.db.query(UserGroupMembership).filter(UserGroupMembership.user_id == user_id).delete()
        for group_id in valid_ids:
            self.db.add(UserGroupMembership(user_id=user_id, group_id=group_id))
        self.db.commit()
