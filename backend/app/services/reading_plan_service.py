import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.models.reading_plan import compute_scope_key
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.schemas.reading import ReadingPlanCreate, ReadingPlanUpdate
from app.services.passage_parser import sync_passages_for_plan


class ReadingPlanService:
    """church_id/fellowship_id (mutually exclusive) scope every operation to
    that org's own calendar instead of the shared platform one - see
    ReadingPlan.scope_key. Both None (the default) is the platform calendar,
    same behavior as before this scoping existed."""

    def __init__(self, db: Session, church_id: uuid.UUID | None = None, fellowship_id: uuid.UUID | None = None):
        self.db = db
        self.plans = ReadingPlanRepository(db)
        self.church_id = church_id
        self.fellowship_id = fellowship_id
        self.scope_key = compute_scope_key(church_id, fellowship_id)

    def get(self, plan_id: uuid.UUID):
        plan = self.plans.get_by_id(plan_id)
        if not plan or plan.scope_key != self.scope_key:
            raise NotFoundError("Reading plan day not found")
        return plan

    def list(self, search=None, page=1, page_size=30):
        return self.plans.list(self.scope_key, search, page, page_size)

    def create(self, payload: ReadingPlanCreate):
        if self.plans.get_by_day(payload.day_number, self.scope_key):
            raise ConflictError(f"Day {payload.day_number} already exists in this reading plan")
        plan = self.plans.create(church_id=self.church_id, fellowship_id=self.fellowship_id, **payload.model_dump())
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
