from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserWithStats, UserUpdate
from app.schemas.community import CalendarOptionOut, ActiveCalendarUpdate
from app.services.user_service import UserService
from app.services.community_service import CommunityService

router = APIRouter(prefix="/profile", tags=["Profile (Member)"])


@router.get("/calendar-options", response_model=list[CalendarOptionOut], summary="Churches/Fellowships I belong to that run their own reading calendar")
def calendar_options(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_calendar_options(current_user.id)


@router.patch("/active-calendar", summary="Choose which org's reading calendar/quiz bank to follow (omit both fields for the platform default)")
def set_active_calendar(payload: ActiveCalendarUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).set_active_calendar(current_user.id, payload.kind, payload.org_id)
    return {"success": True}


@router.get("/me", response_model=UserWithStats, summary="Get my profile with stats")
def my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user, stats = UserService(db).get_with_stats(current_user.id)
    return UserWithStats(
        **{
            "id": user.id,
            "user_id": user.user_id,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "status": user.status,
            "photo_url": user.photo_url,
            "joined_date": user.joined_date,
            "date_of_birth": user.date_of_birth,
            "created_at": user.created_at,
            "house_no": user.house_no,
            "street_name": user.street_name,
            "city_name": user.city_name,
            "state_name": user.state_name,
            "postcode": user.postcode,
            "country": user.country,
            "active_calendar_church_id": user.active_calendar_church_id,
            "active_calendar_fellowship_id": user.active_calendar_fellowship_id,
            "current_streak": stats.current_streak if stats else 0,
            "longest_streak": stats.longest_streak if stats else 0,
            "days_completed": stats.days_completed if stats else 0,
            "overall_percentage": float(stats.overall_percentage) if stats else 0,
        }
    )


@router.patch("/me", summary="Update my own profile (name, phone, photo, DOB, address)")
def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Members may only update their own contact/display fields, not role/status.
    payload.role = None
    payload.status = None
    return UserService(db).update(current_user.id, payload)
