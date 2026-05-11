mock_email = [
    {
        "id": "18e4f2a1b3c9d001",
        "headers": {
            "date": "Mon, 24 Jun 2026 09:00:00 +1100",
            "to": "john@example.com",
            "from": "Jane Smith <jane.smith@example.com>",
            "subject": "Team Standup - Wednesday 26 June",
        },
        "body": "Hi John, just a reminder about our team standup on Wednesday 26 June at 9am. We will be meeting on Zoom at https://zoom.us/j/123456789. Please come prepared to discuss your priorities. Thanks, Jane",
    }
]

mock_followup = [
    {
        "id": "19f5z0c1b3d2p005",
        "headers": {
            "date": "Tue, 25 Jun 2026 09:39:00 +1100",
            "to": "john@example.com",
            "from": "Jane Smith <jane.smith@example.com>",
            "subject": "Team Meeting",
        },
        "body": "Hi John, another reminder about our team meeting tomorrow. Don't forget like last time! Thanks, Jane",
    }
]

payload = {
    "headers": [
        {"name": "Date", "value": "Mon, 24 Jun 2026 09:00:00+1100"},
        {"name": "To", "value": "john@example.com"},
        {"name": "From", "value": "Jane Smith <jane@example.com>"},
        {"name": "Subject", "value": "Team Standup"},
    ],
    "body": {"data": "SGVsbG8gSm9obg=="},
}

mock_gmail_payload = {
    "id": "",
    "threadId": "",
    "labelIds": [""],
    "snippet": "",
    "historyId": "",
    "internalDate": "",
    "payload": payload,
    "sizeEstimate": -1,
    "raw": "",
    "classificationLabelValues": [{}],
}
