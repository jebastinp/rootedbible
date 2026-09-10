import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.models.user import UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services import audit_service


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def get(self, user_id: uuid.UUID):
        user = self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("Member not found")
        return user

    def list(self, search=None, role=None, status_filter=None, page=1, page_size=20):
        return self.users.list(search, role, status_filter, page, page_size)

    def create(self, payload: UserCreate):
        existing = self.users.get_by_user_code(payload.user_id)
        if existing:
            raise ConflictError(f"User ID '{payload.user_id}' already exists")
        data = payload.model_dump()
        data["user_id"] = data["user_id"].strip().upper()
        return self.users.create(**data)

    def update(self, user_id: uuid.UUID, payload: UserUpdate, actor_id: uuid.UUID | None = None):
        user = self.get(user_id)
        changes = payload.model_dump(exclude_unset=True)
        if actor_id and changes.get("role") is not None and changes["role"] != user.role:
            new_role = changes["role"]
            audit_service.record(self.db, actor_id, "role_changed", "user", user.id, {
                "from": user.role.value if hasattr(user.role, "value") else str(user.role),
                "to": new_role.value if hasattr(new_role, "value") else str(new_role),
            })
        updated = self.users.update(user, **changes)
        if actor_id:
            self.db.commit()
        return updated

    def deactivate(self, user_id: uuid.UUID, actor_id: uuid.UUID | None = None):
        user = self.get(user_id)
        updated = self.users.update(user, status=UserStatus.inactive)
        if actor_id:
            audit_service.record(self.db, actor_id, "user_suspended", "user", user.id, {"user_id": user.user_id})
            self.db.commit()
        return updated

    def activate(self, user_id: uuid.UUID, actor_id: uuid.UUID | None = None):
        user = self.get(user_id)
        updated = self.users.update(user, status=UserStatus.active)
        if actor_id:
            audit_service.record(self.db, actor_id, "user_reactivated", "user", user.id, {"user_id": user.user_id})
            self.db.commit()
        return updated

    def delete(self, user_id: uuid.UUID, actor_id: uuid.UUID | None = None):
        user = self.get(user_id)
        self.users.soft_delete(user)
        if actor_id:
            audit_service.record(self.db, actor_id, "user_deleted", "user", user.id, {"user_id": user.user_id})
            self.db.commit()

    def get_with_stats(self, user_id: uuid.UUID):
        user = self.get(user_id)
        stats = self.users.get_stats(user_id)
        return user, stats
