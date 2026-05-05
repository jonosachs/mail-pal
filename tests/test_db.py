import pytest
from services.db import Declined
from tests.mock_event import mock_event


# Run single test: python -m pytest tests/test_db.py -s
def test_add():
    d = Declined()
    d.add(event=mock_event)
    all = d.get_all()
    print(all)
    assert mock_event.id_ in str(all)
