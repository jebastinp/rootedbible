import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.models.user import UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


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

    def update(self, user_id: uuid.UUID, payload: UserUpdate):
        user = self.get(user_id)
        return self.users.update(user, **payload.model_dump(exclude_unset=True))

    def deactivate(self, user_id: uuid.UUID):
        user = self.get(user_id)
        return self.users.update(user, status=UserStatus.inactive)

    def activate(self, user_id: uuid.UUID):
        user = self.get(user_id)
        return self.users.update(user, status=UserStatus.active)

    def delete(self, user_id: uuid.UUID):
        user = self.get(user_id)
        self.users.soft_delete(user)

    def get_with_stats(self, user_id: uuid.UUID):
        user = self.get(user_id)
        stats = self.users.get_stats(user_id)
        return user, stats
