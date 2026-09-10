"""Church and Fellowship - standalone community entities, same
Request -> Approval -> Membership pattern as Family/Buddy (see
ChallengeService), sharing the same JoinRequest table via `type`.

Unlike Family/Buddy (which any user creates for themselves), a Church or
Fellowship may only be created by an admin/super_admin - enforced by
`require_admin` on the POST /community/church and /community/fellowship
routes. Members only ever join an existing one.
"""
import secrets
import string
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.models.user import User
from app.models.church import Church, ChurchMember
from app.models.fellowship import Fellowship, FellowshipMember
from app.models.group import RootedGroup, UserGroupMembership
from app.models.challenge import JoinRequest, RequestStatus
from app.services import audit_service
from app.services.notification_service import notify
from app.schemas.community import (
    ChurchCreate, ChurchOut, ChurchDetailOut, ChurchMemberOut,
    FellowshipCreate, FellowshipOut, FellowshipDetailOut,
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
        MemberModel = self._member_model(kind)
        fk = self._fk(kind)
        row = self.db.query(MemberModel).filter(getattr(MemberModel, fk) == entity_id, MemberModel.user_id == user_id, MemberModel.status == "active").first()
        return row.role if row else None

    def _require_membership(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID):
        role = self._my_role(kind, entity_id, user_id)
        if not role:
            raise ForbiddenError(f"You are not a member of this {kind}.")
        return role

    def _require_admin(self, kind: str, entity_id: uuid.UUID, user_id: uuid.UUID):
        role = self._require_membership(kind, entity_id, user_id)
        if role not in ("owner", "admin"):
            raise ForbiddenError("Only the owner or an admin can do this.")
        return role

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

    def admin_create_church(self, owner_id: uuid.UUID, payload: ChurchCreate) -> Church:
        church = Church(
            name=payload.name, description=payload.description, address=payload.address,
            owner_id=owner_id, church_code=self._generate_church_code(), privacy=payload.privacy,
        )
        self.db.add(church)
        self.db.flush()
        self.db.add(ChurchMember(church_id=church.id, user_id=owner_id, role="owner", status="active"))
        audit_service.record(self.db, owner_id, "church_created", "church", church.id, {"name": church.name})
        self.db.commit()
        self.db.refresh(church)
        return church

    def _get_church(self, church_id: uuid.UUID) -> Church:
        church = self.db.query(Church).filter(Church.id == church_id).first()
        if not church:
            raise NotFoundError("Church not found.")
        return church

    def _to_church_out(self, church: Church, user_id: uuid.UUID | None) -> ChurchOut:
        return ChurchOut(
            id=church.id, name=church.name, church_code=church.church_code, description=church.description,
            address=church.address, privacy=church.privacy, status=church.status,
            member_count=self._member_count("church", church.id), my_role=self._my_role("church", church.id, user_id) if user_id else None,
            created_at=church.created_at,
        )

    def list_discoverable_churches(self, user_id: uuid.UUID) -> list[ChurchOut]:
        my_ids = {m.church_id for m in self.db.query(ChurchMember).filter(ChurchMember.user_id == user_id, ChurchMember.status == "active").all()}
        churches = self.db.query(Church).filter(Church.status == "active", Church.privacy == "public").order_by(Church.created_at.desc()).all()
        return [self._to_church_out(c, user_id) for c in churches if c.id not in my_ids]

    def admin_list_all_churches(self) -> list[ChurchOut]:
        churches = self.db.query(Church).order_by(Church.created_at.desc()).all()
        return [self._to_church_out(c, None) for c in churches]

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
    def admin_create_fellowship(self, owner_id: uuid.UUID, payload: "FellowshipCreate") -> Fellowship:
        if payload.church_id:
            self._require_membership("church", payload.church_id, owner_id)
        fellowship = Fellowship(name=payload.name, description=payload.description, church_id=payload.church_id, owner_id=owner_id, privacy=payload.privacy)
        self.db.add(fellowship)
        self.db.flush()
        self.db.add(FellowshipMember(fellowship_id=fellowship.id, user_id=owner_id, role="owner", status="active"))
        audit_service.record(self.db, owner_id, "fellowship_created", "fellowship", fellowship.id, {"name": fellowship.name})
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
        return FellowshipOut(
            id=fellowship.id, name=fellowship.name, description=fellowship.description, church_id=fellowship.church_id,
            church_name=church_name, privacy=fellowship.privacy, status=fellowship.status,
            member_count=self._member_count("fellowship", fellowship.id), my_role=self._my_role("fellowship", fellowship.id, user_id) if user_id else None,
            created_at=fellowship.created_at,
        )

    def admin_list_all_fellowships(self) -> list[FellowshipOut]:
        fellowships = self.db.query(Fellowship).order_by(Fellowship.created_at.desc()).all()
        return [self._to_fellowship_out(f, None) for f in fellowships]

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

    def request_join_fellowship(self, user_id: uuid.UUID, fellowship_id: uuid.UUID) -> JoinRequest:
        fellowship = self._get_fellowship(fellowship_id)
        if fellowship.status != "active":
            raise ValidationError("This fellowship is not accepting new members.")

        existing = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == fellowship_id, FellowshipMember.user_id == user_id).first()
        if existing and existing.status == "active":
            raise ConflictError("You already belong to this fellowship.")

        pending = self.db.query(JoinRequest).filter(JoinRequest.type == "fellowship", JoinRequest.fellowship_id == fellowship_id, JoinRequest.requester_id == user_id, JoinRequest.status == RequestStatus.pending.value).first()
        if pending:
            raise ConflictError("Your request to join is already pending.")

        request = JoinRequest(type="fellowship", requester_id=user_id, fellowship_id=fellowship_id, status=RequestStatus.pending.value)
        self.db.add(request)
        audit_service.record(self.db, user_id, "fellowship_join_requested", "fellowship", fellowship_id, {"user_id": str(user_id)})
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
