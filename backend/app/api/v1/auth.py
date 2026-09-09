from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import LoginRequest, SupabaseLoginRequest, TokenResponse, RefreshRequest, UserOut
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/supabase", response_model=TokenResponse, summary="Sign in via Supabase Auth (primary auth for all users)")
def login_with_supabase(payload: SupabaseLoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login_with_supabase(payload.access_token)


@router.post("/login", response_model=TokenResponse, summary="Legacy User-ID login (staff/admin fallback only, not shown in the normal app)")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload.user_id)


@router.post("/refresh", response_model=TokenResponse, summary="Exchange a refresh token for a new access token")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=UserOut, summary="Get the currently logged in user")
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", summary="Logout (client should discard tokens)")
def logout():
    # Stateless JWT - logout is handled client-side by discarding tokens.
    return {"message": "Logged out successfully"}
