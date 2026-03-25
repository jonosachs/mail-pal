# Life Admin

Scans emails daily for action items, extracts calendar events using Gemini AI, and sends one-click approve/deny notifications via Slack. On approval, creates the event in Google Calendar.

## How it works

1. **AWS EventBridge** triggers the `RunPipeline` Lambda daily at 9am UTC (8pm AEDT)
2. **AWS Lambda: RunPipeline** fetches emails from configured Gmail labels, uses Gemini to extract calendar events, and sends an approval message to Slack for each event
3. **Slack** presents approve/deny buttons — clicking approve triggers the `SlackHandler` Lambda via AWS API Gateway
4. **AWS Lambda: SlackHandler** validates the request, creates the Google Calendar event, and updates the Slack message

## Architecture

```
AWS EventBridge (daily cron, UTC)
    → AWS Lambda: RunPipeline
        → Gmail API (fetch emails)
        → Gemini API (extract events)
        → Slack (send approval messages)

Slack (button click)
    → AWS API Gateway
        → AWS Lambda: SlackHandler
            → Google Calendar API (create event)
            → Slack (update message)
```

Secrets are stored in AWS Secrets Manager for production and a `.env` file for local development.

## Code

```
life-admin/
├── pyproject.toml                # dependencies
├── template.yaml                 # AWS SAM deployment config
├── samconfig.toml                # SAM deploy settings
├── main.py                       # local entry point
├── config.py                     # loads secrets from .env or Secrets Manager
├── functions/
│   ├── run_pipeline/
│   │   └── pipeline.py           # EventBridge triggered Lambda
│   └── slack_handler/
│       └── handler.py            # API Gateway triggered Lambda
├── layers/
│   └── dependencies/
│       └── requirements.txt      # shared Lambda dependencies
├── services/
│   ├── gmail.py
│   ├── gcal.py
│   ├── gemini.py
│   ├── slack.py
│   ├── credentials.py
│   └── prompt.py
├── models/
│   └── event.py
└── tests/
    ├── test_gcal.py
    ├── test_gemini.py
    ├── test_gmail.py
    └── test_slack.py
```

## Credentials

Local dev uses a `.env` file. Production secrets are stored in AWS Secrets Manager under `life-admin/secrets`.

| Secret                 | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID                            |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret                        |
| `GOOGLE_REFRESH_TOKEN` | Obtained once via `services/google_quickstart.py` |
| `GOOGLE_API_KEY`       | Google API key                                    |
| `GEMINI_API_KEY`       | Gemini API key                                    |
| `EMAILS`               | Comma-separated attendee emails                   |
| `MAILBOXES`            | Comma-separated Gmail label names to scan         |
| `SLACK_WEBHOOK_URL`    | Slack incoming webhook URL                        |
| `SLACK_SIGNING_SECRET` | Slack signing secret for request verification     |

## Setup

```bash
pip install -e .
```

### Testing

```bash
pip install -e ".[dev]"
pytest
```

### Deploy

```bash
sam build
sam deploy
```
