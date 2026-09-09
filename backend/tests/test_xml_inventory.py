import pytest

from app.content.xml_inventory import inspect_xml
from app.content.validation import ContentValidationError


def write_xml(tmp_path, verses):
    path = tmp_path / "synthetic.xml"
    path.write_text(f'<XMLBIBLE biblename="Synthetic"><BIBLEBOOK bnumber="1" bname="Synthetic"><CHAPTER cnumber="1">{verses}</CHAPTER></BIBLEBOOK></XMLBIBLE>')
    return path


def test_metadata_report_does_not_publish_verse_text(tmp_path):
    report = inspect_xml(write_xml(tmp_path, '<VERS vnumber="1">தமிழ் சோதனை</VERS>'))
    assert report["verses_observed"] == 1
    assert report["findings"] == []
    assert report["release_ready"] is False
    assert "தமிழ் சோதனை" not in str(report)


def test_reports_numbering_and_empty_text(tmp_path):
    report = inspect_xml(write_xml(tmp_path, '<VERS vnumber="2"></VERS><VERS vnumber="2">Synthetic</VERS>'))
    issues = [item["issue"] for item in report["findings"]]
    assert "Duplicate vnumber" in issues
    assert "Empty verse" in issues
    assert any("Nonconsecutive" in issue for issue in issues)


def test_rejects_entity_declarations(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text('<!DOCTYPE XMLBIBLE [<!ENTITY sample "example">]><XMLBIBLE/>')
    with pytest.raises(ContentValidationError, match="entity declarations"):
        inspect_xml(path)
