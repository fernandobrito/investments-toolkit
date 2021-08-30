import pytest

from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject():
    return Asset(Source.Avanza, "1234", "Test Asset")


@pytest.fixture
def subject_as_dict():
    return dict(source="Avanza", source_id="1234", name="Test Asset")


def test_fqn_id(subject):
    assert subject.fqn_id == "AV:1234"


def test_to_dict(subject, subject_as_dict):
    assert subject.to_dict() == subject_as_dict


def test_from_dict(subject, subject_as_dict):
    assert Asset.from_dict(subject_as_dict) == subject


def test_merge_dict(subject):
    subject.merge_dict(dict(source_id="9999", name="A new name"))
    assert subject.source_id == "9999"
    assert subject.name == "A new name"


@pytest.mark.parametrize(
    "fqn_id, expected", [("AV:1234", (Source.Avanza, "1234")), ("CMC:ABCD-X", (Source.CMC, "ABCD-X"))]
)
def test_parse_fqn_id(fqn_id, expected):
    assert Asset.parse_fqn_id(fqn_id) == expected
