"""Integration tests (real DB, rolled back per test) for the fire-and-forget
notification helper and NotificationService."""
from app.services.notification_service import notify, NotificationService


def test_notify_is_fire_and_forget_until_caller_commits(db, make_user):
    user = make_user()
    notify(db, user.id, "test_event", "Hello there", message="A message", link="/somewhere")
    db.flush()  # simulate the caller's own transaction reaching a flush point

    svc = NotificationService(db)
    mine = svc.list_mine(user.id)
    assert len(mine) == 1
    assert mine[0].title == "Hello there"
    assert mine[0].is_read is False


def test_unread_count_and_mark_read(db, make_user):
    user = make_user()
    notify(db, user.id, "a", "First")
    notify(db, user.id, "b", "Second")
    db.commit()

    svc = NotificationService(db)
    assert svc.unread_count(user.id) == 2

    first = svc.list_mine(user.id)[-1]  # oldest first when reversed by created_at desc, so last = oldest
    svc.mark_read(user.id, first.id)
    assert svc.unread_count(user.id) == 1


def test_mark_all_read(db, make_user):
    user = make_user()
    notify(db, user.id, "a", "First")
    notify(db, user.id, "b", "Second")
    notify(db, user.id, "c", "Third")
    db.commit()

    svc = NotificationService(db)
    svc.mark_all_read(user.id)
    assert svc.unread_count(user.id) == 0


def test_notifications_are_scoped_per_user(db, make_user):
    user_a = make_user()
    user_b = make_user()
    notify(db, user_a.id, "a", "For A")
    db.commit()

    svc = NotificationService(db)
    assert len(svc.list_mine(user_a.id)) == 1
    assert len(svc.list_mine(user_b.id)) == 0
