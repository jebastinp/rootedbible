"""Integration tests (real DB, rolled back per test) for bulk quiz CSV
import - matches the "No,Book,Chapter,Q.No,Question,A,B,C,D,Reference,
Correct Option,Correct Answer" template so an admin can upload ~1000
question rows at once instead of one at a time."""
import sqlalchemy as sa

from app.services.csv_import_service import CsvImportService
from app.services.quiz_service import QuizService

SAMPLE_CSV = b"""No,Book,Chapter,Q.No,Question,A,B,C,D,Reference,Correct Option,Correct Answer
1,Matthew,1,1,\"According to Matthew 1, who was the husband of Mary?\",Herod,Peter,David,Joseph,Matthew 1:16,D,Joseph
2,Matthew,1,2,What name was Joseph told to give Mary's son?,Jesus,Herod,Joseph,Peter,Matthew 1:21,A,Jesus
3,Matthew,2,1,Where was Jesus born?,Jordan,Egypt,Bethlehem,Galilee,Matthew 2:1,C,Bethlehem
"""


def _version_code(db):
    return db.execute(sa.text("select code from bible_version where is_active limit 1")).scalar()


def test_preview_validates_every_row_against_real_bible_data(db, make_user):
    admin = make_user(role="admin")
    code = _version_code(db)
    service = CsvImportService(db)

    preview = service.preview("quiz", "quiz.csv", SAMPLE_CSV, version_code=code)

    assert preview.total_rows == 3
    assert preview.valid_rows == 3
    assert preview.invalid_rows == 0


def test_confirm_inserts_questions_into_the_correct_chapter_with_correct_index(db, make_user):
    code = _version_code(db)
    service = CsvImportService(db)
    quiz_service = QuizService(db)

    preview = service.preview("quiz", "quiz.csv", SAMPLE_CSV, version_code=code)
    result = service.confirm(preview.import_token, imported_by=None)

    assert result.inserted_rows == 3
    assert result.failed_rows == 0

    matthew_1 = quiz_service.resolve_chapter_id(code, "Matthew", 1)
    questions = quiz_service.admin_list_questions_for_chapter(matthew_1)
    assert len(questions) == 2
    joseph_q = next(q for q in questions if "husband of Mary" in q.question)
    assert joseph_q.options[joseph_q.correct_index] == "Joseph"

    matthew_2 = quiz_service.resolve_chapter_id(code, "Matthew", 2)
    questions_2 = quiz_service.admin_list_questions_for_chapter(matthew_2)
    assert len(questions_2) == 1
    assert questions_2[0].options[questions_2[0].correct_index] == "Bethlehem"


def test_invalid_book_name_is_flagged_but_does_not_block_other_rows(db):
    code = _version_code(db)
    bad_csv = SAMPLE_CSV + b"4,NotABook,1,1,Bad question?,A,B,C,D,NotABook 1:1,A,A\n"
    service = CsvImportService(db)

    preview = service.preview("quiz", "quiz.csv", bad_csv, version_code=code)

    assert preview.total_rows == 4
    assert preview.valid_rows == 3
    assert preview.invalid_rows == 1
    bad_row = next(r for r in preview.rows if not r.valid)
    assert any("NotABook" in e for e in bad_row.errors)


def test_missing_version_code_is_rejected_for_quiz_import(db):
    from app.core.exceptions import ValidationError
    import pytest
    service = CsvImportService(db)
    with pytest.raises(ValidationError):
        service.preview("quiz", "quiz.csv", SAMPLE_CSV, version_code=None)


def test_quiz_csv_import_can_be_scoped_to_a_church(db, make_user):
    from app.services.community_service import CommunityService
    from app.schemas.community import ChurchCreate

    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))
    code = _version_code(db)
    service = CsvImportService(db)

    preview = service.preview("quiz", "quiz.csv", SAMPLE_CSV, version_code=code, church_id=church.id)
    service.confirm(preview.import_token, imported_by=owner.id)

    church_quiz = QuizService(db, church_id=church.id)
    platform_quiz = QuizService(db)
    matthew_1 = church_quiz.resolve_chapter_id(code, "Matthew", 1)
    assert len(church_quiz.admin_list_questions_for_chapter(matthew_1)) == 2
    assert len(platform_quiz.admin_list_questions_for_chapter(matthew_1)) == 0
