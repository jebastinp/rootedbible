import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token, TokenError
from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_uuid = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_uuid), User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status != UserStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    return user


def require_roles(*roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
        return current_user
    return dependency



# Platform-wide administrative capabilities (creating Churches/Fellowships,
# managing the platform Bible calendar/quiz bank, viewing every member,
# CSV import, reports, audit logs, ...) belong to Super Admin ALONE.
# `admin` is always scoped to exactly one Church or Fellowship (see
# AdminOrganizationAssignment) and must never reach these endpoints -
# there is deliberately no "require_admin" that includes the `admin` role.
require_super_admin = require_roles(UserRole.super_admin)
