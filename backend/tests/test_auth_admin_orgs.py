"""Integration tests (real DB, rolled back per test) for the admin_orgs
field on the sign-in response: lets the frontend route a Church/Fellowship
admin straight to their org's own admin page. Becoming an org admin DOES
change the user's global role to 'admin' (see AdminOrganizationAssignment) -
it just never grants any platform-wide capability."""
from app.services.auth_service import AuthService
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate


def test_plain_member_has_no_admin_orgs(db, make_user):
    user = make_user()
    response = AuthService(db).login(user.user_id)
    assert response.admin_orgs == []


def test_church_owner_sees_their_church_in_admin_orgs(db, make_user):
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))

    response = AuthService(db).login(owner.user_id)

    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].kind == "church"
    assert response.admin_orgs[0].org_id == church.id
    assert response.admin_orgs[0].name == "Grace Chapel"
    # org admin is real (role=admin), but never platform-wide staff access
    assert response.user.role.value == "admin"


def test_plain_church_member_not_admin_has_no_admin_orgs(db, make_user):
    owner = make_user()
    member = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    request = community.request_join_church(member.id, church_id=church.id)
    community.respond_to_church_request(owner.id, request.id, approve=True)

    response = AuthService(db).login(member.user_id)
    assert response.admin_orgs == []


def test_fellowship_admin_sees_their_fellowship_in_admin_orgs(db, make_user):
    owner = make_user()
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(owner.id, FellowshipCreate(name="Youth Fellowship", privacy="public", admin_email=owner.email))

    response = AuthService(db).login(owner.user_id)

    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].kind == "fellowship"
    assert response.admin_orgs[0].org_id == fellowship.id


def test_admin_orgs_also_present_on_token_refresh(db, make_user):
    """A returning session (token refresh, not a fresh login) must still
    carry admin_orgs - otherwise a persisted frontend session would never
    learn that its user administers an org until they explicitly log out
    and back in."""
    from app.core.security import create_refresh_token

    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))

    refresh_token = create_refresh_token(subject=str(owner.id))
    response = AuthService(db).refresh(refresh_token)

    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].org_id == church.id
