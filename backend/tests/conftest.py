"""Shared fixtures for tests that need a real database.

Each test runs inside its own transaction (with a savepoint restarted
after every flush/commit the code under test performs) and everything is
rolled back at the end - nothing written by these tests is ever
persisted to the dev database.
"""
import uuid

import pytest
from sqlalchemy import event

from app.db.session import engine, SessionLocal
from app.models.user import User, UserRole, UserStatus


@pytest.fixture()
def db():
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture()
def make_user(db):
    """Factory fixture: make_user() -> a flushed, unique test User."""
    def _make(role: UserRole = UserRole.member, **overrides) -> User:
        suffix = uuid.uuid4().hex[:10]
        user = User(
            user_id=f"TEST{suffix[:6].upper()}",
            name=overrides.pop("name", f"Test User {suffix}"),
            email=overrides.pop("email", f"test-{suffix}@example.com"),
            role=role,
            status=UserStatus.active,
            **overrides,
        )
        db.add(user)
        db.flush()
        return user
    return _make
