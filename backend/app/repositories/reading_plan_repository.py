from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.reading_plan import ReadingPlan, ReadingPlanPassage, compute_scope_key


class ReadingPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: uuid.UUID) -> ReadingPlan | None:
        return self.db.query(ReadingPlan).filter(ReadingPlan.id == plan_id, ReadingPlan.deleted_at.is_(None)).first()

    def get_by_day(self, day_number: int, scope_key: str = "platform") -> ReadingPlan | None:
        return self.db.query(ReadingPlan).filter(
            ReadingPlan.day_number == day_number, ReadingPlan.scope_key == scope_key, ReadingPlan.deleted_at.is_(None)
        ).first()

    def get_today(self, today: date | None = None, scope_key: str = "platform") -> ReadingPlan | None:
        today = today or date.today()
        return self.db.query(ReadingPlan).filter(
            ReadingPlan.reading_date == today, ReadingPlan.scope_key == scope_key, ReadingPlan.deleted_at.is_(None)
        ).first()

    def list(self, scope_key: str = "platform", search: str | None = None, page: int = 1, page_size: int = 30) -> tuple[list[ReadingPlan], int]:
        query = self.db.query(ReadingPlan).filter(ReadingPlan.scope_key == scope_key, ReadingPlan.deleted_at.is_(None))
        if search:
            like = f"%{search}%"
            query = query.filter((ReadingPlan.old_testament.ilike(like)) | (ReadingPlan.new_testament.ilike(like)))
        total = query.count()
        items = query.order_by(ReadingPlan.day_number.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def list_all_ordered(self, scope_key: str = "platform") -> list[ReadingPlan]:
        return self.db.query(ReadingPlan).filter(ReadingPlan.scope_key == scope_key, ReadingPlan.deleted_at.is_(None)).order_by(ReadingPlan.day_number.asc()).all()

    def total_days(self, scope_key: str = "platform") -> int:
        return self.db.query(ReadingPlan).filter(ReadingPlan.scope_key == scope_key, ReadingPlan.deleted_at.is_(None)).count()

    def get_passages(self, plan_id: uuid.UUID) -> list[ReadingPlanPassage]:
        return (
            self.db.query(ReadingPlanPassage)
            .filter(ReadingPlanPassage.reading_plan_id == plan_id)
            .order_by(ReadingPlanPassage.sort_order.asc())
            .all()
        )

    def create(self, church_id: uuid.UUID | None = None, fellowship_id: uuid.UUID | None = None, **kwargs) -> ReadingPlan:
        plan = ReadingPlan(church_id=church_id, fellowship_id=fellowship_id, scope_key=compute_scope_key(church_id, fellowship_id), **kwargs)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, plan: ReadingPlan, **kwargs) -> ReadingPlan:
        for key, value in kwargs.items():
            if value is not None:
                setattr(plan, key, value)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete(self, plan: ReadingPlan) -> None:
        self.db.delete(plan)
        self.db.commit()
