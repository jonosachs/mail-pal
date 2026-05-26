from unittest.mock import MagicMock
from services.aws.db import DeclinedEvents
from tests.mock_event import mock_event

mock_table = MagicMock()
d = DeclinedEvents(table=mock_table)


def test_add():
    db_id = d.add(event=mock_event)
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

    # Id should the db UUID key (not event/email id)
    assert item["id"] == db_id

    assert mock_event.title in str(item)
