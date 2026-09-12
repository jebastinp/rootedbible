"""Integration tests (real DB, rolled back per test) for Super Admin's
edit/deactivate/reactivate/delete controls over any Church or Fellowship,
and for correcting a Church/Fellowship's assigned admin via the same
Edit action - the final architecture has no "pending invite" state, so
correcting a typo means reassigning to the right (already-existing)
member immediately."""
import pytest

from app.core.exceptions import NotFoundError
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate, ChurchUpdate, FellowshipUpdate


def test_super_admin_can_edit_a_church(db, make_user):
    creator = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    updated = community.admin_update_church(creator.id, church.id, ChurchUpdate(name="New Name", privacy="private"))

    assert updated.name == "New Name"
    assert updated.privacy == "private"


def test_super_admin_can_deactivate_and_reactivate_a_church(db, make_user):
    creator = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    suspended = community.admin_set_church_status(creator.id, church.id, "suspended")
    assert suspended.status == "suspended"

    reactivated = community.admin_set_church_status(creator.id, church.id, "active")
    assert reactivated.status == "active"


def test_super_admin_can_delete_a_church(db, make_user):
    creator = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    community.admin_delete_church(creator.id, church.id)

    with pytest.raises(NotFoundError):
        community._get_church(church.id)


def test_super_admin_can_edit_deactivate_delete_a_fellowship(db, make_user):
    creator = make_user(role="super_admin")
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(creator.id, FellowshipCreate(name="Youth Fellowship", privacy="public"))

    updated = community.admin_update_fellowship(creator.id, fellowship.id, FellowshipUpdate(name="Renamed Fellowship"))
    assert updated.name == "Renamed Fellowship"

    suspended = community.admin_set_fellowship_status(creator.id, fellowship.id, "suspended")
    assert suspended.status == "suspended"

    community.admin_delete_fellowship(creator.id, fellowship.id)
    with pytest.raises(NotFoundError):
        community._get_fellowship(fellowship.id)


def test_assigned_admin_visible_to_org_admin_and_super_admin_but_not_regular_member(db, make_user):
    creator = make_user(role="super_admin")
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    owner_view = community.get_church_detail(owner.id, church.id)
    assert owner_view.admin.user_id == owner.user_id

    member_view = community.get_church_detail(member.id, church.id)
    assert member_view.admin is None

    platform_list = community.admin_list_all_churches()
    listed = next(c for c in platform_list if c.id == church.id)
    assert listed.admin.user_id == owner.user_id


def test_super_admin_can_correct_a_mistyped_admin_email(db, make_user):
    """The actual bug report: a typo in the admin_email at creation time
    (e.g. 'fewllowship' instead of 'fellowship') assigned the wrong
    person. Under the final architecture this must be resolved
    immediately by reassigning to the correctly-spelled, ALREADY
    REGISTERED email - never a silent pending state."""
    creator = make_user(role="super_admin")
    correct_admin = make_user(email="cousinsprayerfellowship@example.com")
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(
        creator.id, FellowshipCreate(name="Cousins Prayer Fellowship", privacy="private", admin_email="cousinsprayerfellowship@example.com")
    )
    assert fellowship.owner_id == correct_admin.id

    # Super Admin corrects to a different (also already-registered) email
    another_member = make_user(email="actual.leader@example.com")
    community.admin_update_fellowship(creator.id, fellowship.id, FellowshipUpdate(admin_email="actual.leader@example.com"))

    db.refresh(fellowship)
    assert fellowship.owner_id == another_member.id
    assert community._is_org_admin("fellowship", fellowship.id, another_member.id)
    assert not community._is_org_admin("fellowship", fellowship.id, correct_admin.id)


def test_admin_email_correction_to_an_unregistered_email_fails_clearly(db, make_user):
    creator = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    with pytest.raises(NotFoundError):
        community.admin_update_church(creator.id, church.id, ChurchUpdate(admin_email="nobody.registered@example.com"))


def test_admin_email_untouched_when_not_included_in_the_update_payload(db, make_user):
    creator = make_user(role="super_admin")
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))

    community.admin_update_church(creator.id, church.id, ChurchUpdate(name="Renamed Church"))

    assert community._is_org_admin("church", church.id, owner.id)


def test_admin_email_cleared_with_empty_string_demotes_admin_to_member(db, make_user):
    creator = make_user(role="super_admin")
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))

    community.admin_update_church(creator.id, church.id, ChurchUpdate(admin_email=""))

    db.refresh(owner)
    assert owner.role.value == "member"
    assert not community._is_org_admin("church", church.id, owner.id)
