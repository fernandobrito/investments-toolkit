import pytest

from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject():
    return Asset(Source.Avanza, '1234', 'Test Asset')


@pytest.fixture
def subject_as_dict():
    return dict(source='Avanza', source_id='1234', name='Test Asset')


def test_fqn_id(subject):
    assert subject.fqn_id == 'AV:1234'


def test_to_dict(subject, subject_as_dict):
    assert subject.to_dict() == subject_as_dict


def test_from_dict(subject, subject_as_dict):
    assert Asset.from_dict(subject_as_dict) == subject