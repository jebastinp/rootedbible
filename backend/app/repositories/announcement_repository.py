import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.misc import Announcement, ChurchSettings


class AnnouncementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, announcement_id: uuid.UUID) -> Announcement | None:
        return self.db.query(Announcement).filter(Announcement.id == announcement_id, Announcement.deleted_at.is_(None)).first()

    def list_active(self, today: date | None = None) -> list[Announcement]:
        today = today or date.today()
        query = self.db.query(Announcement).filter(
            Announcement.deleted_at.is_(None),
            Announcement.is_active.is_(True),
            Announcement.publish_date <= today,
        )
        results = query.order_by(Announcement.publish_date.desc()).all()
        return [a for a in results if not a.expiry_date or a.expiry_date >= today]

    def list_all(self, page: int = 1, page_size: int = 20) -> tuple[list[Announcement], int]:
        query = self.db.query(Announcement).filter(Announcement.deleted_at.is_(None))
        total = query.count()
        items = query.order_by(Announcement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def create(self, **kwargs) -> Announcement:
        a = Announcement(**kwargs)
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        return a

    def update(self, a: Announcement, **kwargs) -> Announcement:
        for key, value in kwargs.items():
            if value is not None:
                setattr(a, key, value)
        self.db.commit()
        self.db.refresh(a)
        return a

    def delete(self, a: Announcement) -> None:
        from datetime import datetime
        a.deleted_at = datetime.utcnow()
        a.is_active = False
        self.db.commit()


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self) -> ChurchSettings | None:
        return self.db.query(ChurchSettings).first()

    def update(self, **kwargs) -> ChurchSettings:
        settings_row = self.get()
        if not settings_row:
            settings_row = ChurchSettings()
            self.db.add(settings_row)
        for key, value in kwargs.items():
            if value is not None:
                setattr(settings_row, key, value)
        self.db.commit()
        self.db.refresh(settings_row)
        return settings_row
