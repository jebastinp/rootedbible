import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.schemas.reading import ReadingPlanCreate, ReadingPlanUpdate
from app.services.passage_parser import sync_passages_for_plan


class ReadingPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plans = ReadingPlanRepository(db)

    def get(self, plan_id: uuid.UUID):
        plan = self.plans.get_by_id(plan_id)
        if not plan:
            raise NotFoundError("Reading plan day not found")
        return plan

    def list(self, search=None, page=1, page_size=30):
        return self.plans.list(search, page, page_size)

    def create(self, payload: ReadingPlanCreate):
        if self.plans.get_by_day(payload.day_number):
            raise ConflictError(f"Day {payload.day_number} already exists in the reading plan")
        plan = self.plans.create(**payload.model_dump())
        sync_passages_for_plan(self.db, plan)
        return plan

    def update(self, plan_id: uuid.UUID, payload: ReadingPlanUpdate):
        plan = self.get(plan_id)
        plan = self.plans.update(plan, **payload.model_dump(exclude_unset=True))
        sync_passages_for_plan(self.db, plan)
        return plan

    def delete(self, plan_id: uuid.UUID):
        plan = self.get(plan_id)
        self.plans.delete(plan)
