from unittest.mock import MagicMock
from services.declined_events import Declined
from tests.mock_event import mock_event

mock_table = MagicMock()
d = Declined(table=mock_table)


def test_add():
    d.add(event=mock_event)
    mock_table.put_item.assert_called_once()
    item = mock_table.put_item.call_args.kwargs["Item"]

    # Item shape:
    """
    Item={
        "id": unique_id,
        "expiry": expiry,
        **e,
    }
    """

    # Id should be unique UUID
    assert item["id"] != mock_event.id_

    assert mock_event.title in str(item)
