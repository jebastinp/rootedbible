"""Integration tests (real DB, rolled back per test) for Super Admin's
edit/deactivate/reactivate/delete controls over any Church or Fellowship,
and for pending_admin_email being visible to admins (and hidden from
regular members)."""
import pytest

from app.core.exceptions import NotFoundError
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate, ChurchUpdate, FellowshipUpdate


def test_super_admin_can_edit_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    updated = community.admin_update_church(super_admin.id, church.id, ChurchUpdate(name="New Name", privacy="private"))

    assert updated.name == "New Name"
    assert updated.privacy == "private"


def test_super_admin_can_deactivate_and_reactivate_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    suspended = community.admin_set_church_status(super_admin.id, church.id, "suspended")
    assert suspended.status == "suspended"

    reactivated = community.admin_set_church_status(super_admin.id, church.id, "active")
    assert reactivated.status == "active"


def test_super_admin_can_delete_a_church(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    community.admin_delete_church(super_admin.id, church.id)

    with pytest.raises(NotFoundError):
        community._get_church(church.id)


def test_super_admin_can_edit_deactivate_delete_a_fellowship(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(creator.id, FellowshipCreate(name="Youth Fellowship", privacy="public"))

    updated = community.admin_update_fellowship(super_admin.id, fellowship.id, FellowshipUpdate(name="Renamed Fellowship"))
    assert updated.name == "Renamed Fellowship"

    suspended = community.admin_set_fellowship_status(super_admin.id, fellowship.id, "suspended")
    assert suspended.status == "suspended"

    community.admin_delete_fellowship(super_admin.id, fellowship.id)
    with pytest.raises(NotFoundError):
        community._get_fellowship(fellowship.id)


def test_pending_admin_email_visible_to_org_admin_and_super_admin_but_not_regular_member(db, make_user):
    owner = make_user()
    member = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="future.admin@example.com"))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    owner_view = community.get_church_detail(owner.id, church.id)
    assert owner_view.pending_admin_email == "future.admin@example.com"

    member_view = community.get_church_detail(member.id, church.id)
    assert member_view.pending_admin_email is None

    platform_list = community.admin_list_all_churches()
    listed = next(c for c in platform_list if c.id == church.id)
    assert listed.pending_admin_email == "future.admin@example.com"


def test_super_admin_can_correct_a_mistyped_pending_admin_email(db, make_user):
    """The actual bug report: a typo in the admin_email at creation time
    (e.g. 'fewllowship' instead of 'fellowship') left the invite pending
    for an email nobody will ever sign up with. Super Admin must be able
    to fix the email afterward without recreating the whole org."""
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(
        creator.id, FellowshipCreate(name="Cousins Prayer Fellowship", privacy="private", admin_email="cousinsprayerfewllowship@example.com")
    )
    assert fellowship.pending_admin_email == "cousinsprayerfewllowship@example.com"

    corrected = community.admin_update_fellowship(super_admin.id, fellowship.id, FellowshipUpdate(admin_email="cousinsprayerfellowship@example.com"))
    assert corrected.pending_admin_email == "cousinsprayerfellowship@example.com"

    # now the correctly-spelled email resolves normally on signup
    from app.repositories.user_repository import UserRepository
    new_admin = UserRepository(db).create_with_unique_id("Cousins", name="Cousins Prayer Admin", email="cousinsprayerfellowship@example.com")
    db.refresh(fellowship)
    assert fellowship.owner_id == new_admin.id
    assert fellowship.pending_admin_email is None


def test_correcting_admin_email_to_an_existing_account_resolves_ownership_immediately(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    existing_user = make_user(email="already.signed.up@example.com")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="typo@example.com"))

    community.admin_update_church(super_admin.id, church.id, ChurchUpdate(admin_email="already.signed.up@example.com"))

    db.refresh(church)
    assert church.owner_id == existing_user.id
    assert church.pending_admin_email is None
    assert community._my_role("church", church.id, existing_user.id) == "owner"


def test_admin_email_is_untouched_when_not_included_in_the_update_payload(db, make_user):
    creator = make_user()
    super_admin = make_user(role="super_admin")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="pending@example.com"))

    community.admin_update_church(super_admin.id, church.id, ChurchUpdate(name="Renamed Church"))

    db.refresh(church)
    assert church.pending_admin_email == "pending@example.com"
