"""Integration tests (real DB, rolled back per test) for Family/Buddy Group
encouragement - previously wrote a row and nothing else, so a recipient had
no notification and no way to see it. Fixed to notify the recipient(s) and
expose a list endpoint the group can actually read."""
import pytest

from app.services.challenge_service import ChallengeService
from app.services.notification_service import NotificationService
from app.schemas.challenge import GroupCreate, EncouragementCreate


@pytest.fixture()
def family_with_two_members(db, make_user):
    owner = make_user()
    member = make_user()
    service = ChallengeService(db)
    group = service.create_group("family", owner.id, GroupCreate(name="Encourage Test Family"), challenge_id=None)
    request = service.invite_to_group("family", owner.id, group.id, member.user_id)
    service.respond_to_group_request("family", member.id, request.id, accept=True)
    return service, group, owner, member


def test_encouragement_to_whole_group_notifies_every_other_member(db, family_with_two_members, make_user):
    service, group, owner, member = family_with_two_members
    bystander = make_user()  # not in the group - must not be notified

    service.send_group_encouragement("family", owner.id, group.id, EncouragementCreate(message="Keep going."))

    notifications = NotificationService(db)
    member_notes = [n for n in notifications.list_mine(member.id) if n.type == "family_encouragement"]
    assert len(member_notes) == 1
    assert member_notes[0].message == "Keep going."

    # the sender doesn't notify themselves
    assert [n for n in notifications.list_mine(owner.id) if n.type == "family_encouragement"] == []

    assert [n for n in notifications.list_mine(bystander.id) if n.type == "family_encouragement"] == []


def test_encouragement_to_one_person_only_notifies_them(db, family_with_two_members, make_user):
    service, group, owner, member = family_with_two_members
    third = make_user()
    request = service.invite_to_group("family", owner.id, group.id, third.user_id)
    service.respond_to_group_request("family", third.id, request.id, accept=True)

    service.send_group_encouragement("family", owner.id, group.id, EncouragementCreate(message="Well done.", to_user_id=member.user_id))

    notifications = NotificationService(db)
    member_encouragements = [n for n in notifications.list_mine(member.id) if n.type == "family_encouragement"]
    assert len(member_encouragements) == 1
    # targeted at member only, third gets nothing
    assert [n for n in notifications.list_mine(third.id) if n.type == "family_encouragement"] == []


def test_encouragement_appears_in_group_feed_for_every_member(db, family_with_two_members):
    service, group, owner, member = family_with_two_members
    service.send_group_encouragement("family", owner.id, group.id, EncouragementCreate(message="Stay rooted."))

    feed = service.list_group_encouragements("family", member.id, group.id)
    assert len(feed) == 1
    assert feed[0]["message"] == "Stay rooted."
    assert feed[0]["from_name"] == owner.name
    assert feed[0]["to_name"] is None


def test_non_member_cannot_read_group_encouragement_feed(db, family_with_two_members, make_user):
    service, group, owner, member = family_with_two_members
    outsider = make_user()
    from app.core.exceptions import ForbiddenError
    with pytest.raises(ForbiddenError):
        service.list_group_encouragements("family", outsider.id, group.id)


def test_invalid_encouragement_message_rejected(db, family_with_two_members):
    service, group, owner, member = family_with_two_members
    from app.core.exceptions import ValidationError
    with pytest.raises(ValidationError):
        service.send_group_encouragement("family", owner.id, group.id, EncouragementCreate(message="This is not a preset message."))
