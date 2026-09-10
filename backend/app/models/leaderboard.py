"""Configurable ranking rules per Church Challenge - never hardcoded in the
UI. `scope` is either "individual", "family", or a Rooted Group name
(Sunday/Blazer/Youth/Men/Women/...). `ranking_limit` is how many top
entries are shown for that scope (default: Family=1, everything else=3,
per product rule, but always overridable per challenge)."""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class LeaderboardConfig(Base):
    __tablename__ = "leaderboard_config"
    __table_args__ = (
        UniqueConstraint("challenge_id", "scope", name="uq_leaderboard_config_scope"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False)
    scope: Mapped[str] = mapped_column(String(40), nullable=False)
    ranking_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
