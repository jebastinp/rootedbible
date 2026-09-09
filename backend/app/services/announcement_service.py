import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.announcement_repository import AnnouncementRepository, SettingsRepository
from app.schemas.misc import AnnouncementCreate, AnnouncementUpdate, ChurchSettingsUpdate


class AnnouncementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnnouncementRepository(db)

    def list_active(self):
        return self.repo.list_active()

    def list_all(self, page=1, page_size=20):
        return self.repo.list_all(page, page_size)

    def create(self, payload: AnnouncementCreate, created_by: uuid.UUID | None = None):
        data = payload.model_dump()
        data["created_by"] = created_by
        return self.repo.create(**data)

    def update(self, announcement_id: uuid.UUID, payload: AnnouncementUpdate):
        a = self.repo.get_by_id(announcement_id)
        if not a:
            raise NotFoundError("Announcement not found")
        return self.repo.update(a, **payload.model_dump(exclude_unset=True))

    def delete(self, announcement_id: uuid.UUID):
        a = self.repo.get_by_id(announcement_id)
        if not a:
            raise NotFoundError("Announcement not found")
        self.repo.delete(a)


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SettingsRepository(db)

    def get(self):
        settings_row = self.repo.get()
        if not settings_row:
            settings_row = self.repo.update()
        return settings_row

    def update(self, payload: ChurchSettingsUpdate):
        return self.repo.update(**payload.model_dump(exclude_unset=True))
