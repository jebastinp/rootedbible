"""Integration tests (real DB, rolled back per test) for leaderboard
ranking rules (Rule 10): Family shows Top 1, every other scope
(Individual, Buddy Group, each Rooted Group) shows Top 3 by default,
overridable per Church Challenge by an admin."""
import pytest

from app.services.challenge_service import ChallengeService
from app.schemas.challenge import ChallengeCreate, LeaderboardConfigUpdate
from app.models.challenge import ChallengeMember, ChallengeMemberStatus
from app.models.group import RootedGroup, UserGroupMembership


@pytest.fixture()
def challenge(db, make_user):
    admin = make_user(role="admin")
    service = ChallengeService(db)
    ch = service.admin_create_challenge(admin.id, ChallengeCreate(name="LB Test", church_name="Test Church", status="active"))
    return ch, service, admin


def test_default_ranking_limits_family_is_one_others_are_three(challenge, db):
    ch, service, _ = challenge
    config = {c.scope: c.ranking_limit for c in service.admin_list_leaderboard_config(ch.id)}

    assert config["family"] == 1
    assert config["individual"] == 3
    assert config["buddy"] == 3
    for rooted_group_name in ("Sunday School", "Blazer", "Youth", "Men", "Women"):
        assert config[rooted_group_name] == 3


def test_admin_can_override_ranking_limit(challenge, db):
    ch, service, admin = challenge
    updated = service.admin_set_leaderboard_config(admin.id, ch.id, "individual", LeaderboardConfigUpdate(ranking_limit=10))
    assert updated.ranking_limit == 10

    config = {c.scope: c.ranking_limit for c in service.admin_list_leaderboard_config(ch.id)}
    assert config["individual"] == 10
    assert config["family"] == 1  # untouched scopes keep their default


def test_individual_leaderboard_ranks_by_progress_and_respects_limit(challenge, db, make_user):
    ch, service, admin = challenge
    service.admin_set_leaderboard_config(admin.id, ch.id, "individual", LeaderboardConfigUpdate(ranking_limit=2))

    users = [make_user() for _ in range(4)]
    for u in users:
        db.add(ChallengeMember(challenge_id=ch.id, user_id=u.id, status=ChallengeMemberStatus.active.value))
    db.commit()

    board = service.get_leaderboard(ch.id, "individual")
    assert board.ranking_limit == 2
    assert len(board.entries) == 2  # truncated to the configured limit
    assert [e.rank for e in board.entries] == [1, 2]


def test_rooted_group_leaderboard_only_includes_members_of_that_group(challenge, db, make_user):
    ch, service, _ = challenge
    in_group = make_user()
    not_in_group = make_user()
    for u in (in_group, not_in_group):
        db.add(ChallengeMember(challenge_id=ch.id, user_id=u.id, status=ChallengeMemberStatus.active.value))

    sunday = db.query(RootedGroup).filter(RootedGroup.name == "Sunday School").first()
    assert sunday is not None
    db.add(UserGroupMembership(user_id=in_group.id, group_id=sunday.id))
    db.commit()

    board = service.get_leaderboard(ch.id, "Sunday School")
    names = {e.entry_id for e in board.entries}
    assert in_group.user_id in names
    assert not_in_group.user_id not in names


def test_unknown_scope_raises_not_found(challenge):
    ch, service, _ = challenge
    from app.core.exceptions import NotFoundError
    with pytest.raises(NotFoundError):
        service.get_leaderboard(ch.id, "not-a-real-scope")
