import pytest
from services.gmail import Gmail
import logging

logger = logging.getLogger(__name__)

"""
msg_format = {
  "id": msg["id"],
  "headers": {
    "date": headers.get("Date"),
    "to": headers.get("To"),
    "from": headers.get("From"),
    "subject": headers.get("Subject")
  },
  "body": body
}
"""

# Run single test: python -m pytest tests/test_gmail.py -s
# Use -s flag to show logs


def test_get_mail():
    gmail = Gmail()

    mail_list = gmail.get_mail(max_results=1)  # -> list
    mail = mail_list[0]

    assert len(mail["headers"]["subject"]) > 0
    assert mail["body"] != None
