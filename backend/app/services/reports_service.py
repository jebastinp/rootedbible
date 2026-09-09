from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.repositories.progress_repository import ProgressRepository
from app.models.misc import AuditLog
from app.models.user import UserStatus
from app.schemas.misc import AdminDashboardOut, MemberReportRow


class ReportsService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.plans = ReadingPlanRepository(db)
        self.progress = ProgressRepository(db)

    def dashboard(self) -> AdminDashboardOut:
        total_members = self.users.count_active()
        todays_readers = self.progress.todays_readers_count(date.today())
        today_plan = self.plans.get_today()
        current_day = today_plan.day_number if today_plan else None

        completion_pct = round((todays_readers / total_members) * 100, 2) if total_members else 0.0

        top = self.progress.top_readers(5)
        top_readers = [
            {
                "user_id": u.user_id,
                "name": u.name,
                "current_streak": s.current_streak,
                "days_completed": s.days_completed,
                "overall_percentage": float(s.overall_percentage),
            }
            for u, s in top
        ]

        avg_streak = 0.0
        if top:
            all_stats = [s.current_streak for _, s in self.progress.leaderboard(1, 10_000)[0]]
            avg_streak = round(sum(all_stats) / len(all_stats), 2) if all_stats else 0.0

        recent = (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(10)
            .all()
        )
        recent_activities = [
            {"action": r.action, "entity_type": r.entity_type, "created_at": r.created_at.isoformat()}
            for r in recent
        ]

        return AdminDashboardOut(
            total_members=total_members,
            todays_readers=todays_readers,
            completion_percentage=completion_pct,
            current_reading_day=current_day,
            average_streak=avg_streak,
            recent_activities=recent_activities,
            top_readers=top_readers,
        )

    def member_report(self) -> list[MemberReportRow]:
        items, _ = self.progress.leaderboard(1, 10_000)
        rows = []
        for user, stats in items:
            rows.append(
                MemberReportRow(
                    user_id=user.user_id,
                    name=user.name,
                    role=user.role.value,
                    status=user.status.value,
                    days_completed=stats.days_completed,
                    overall_percentage=float(stats.overall_percentage),
                    current_streak=stats.current_streak,
                    longest_streak=stats.longest_streak,
                    last_completed_date=stats.last_completed_date,
                )
            )
        return rows

    def inactive_members(self, days_threshold: int = 7) -> list[MemberReportRow]:
        cutoff = date.today() - timedelta(days=days_threshold)
        all_rows = self.member_report()
        return [r for r in all_rows if not r.last_completed_date or r.last_completed_date < cutoff]
