# Mail PAL

Automated AI mail filter tool that extracts important events and action items from your inbox and creates calendar events for each, with one-click approval via Slack. Built to save time and reduce message fatigue.

## How it works

1. **AWS EventBridge** triggers the `RunPipeline` Lambda daily at 9am UTC (8pm AEDT)
2. **AWS Lambda: RunPipeline** fetches recent emails from configured Gmail labels, queries existing bot-created calendar events and recently declined events, uses Gemini to extract new events (skipping duplicates), and sends an approval message to Slack for each
3. **Slack** presents approve/decline buttons — clicking approve triggers the `SlackHandler` Lambda via AWS API Gateway
4. **AWS Lambda: SlackHandler** validates the request, creates the Google Calendar event, and updates the Slack message

## Architecture

```
AWS EventBridge (daily cron, UTC)
    → AWS Lambda: RunPipeline
        → Gmail API (fetch recent emails)
        → Google Calendar API (fetch existing bot-created events)
        → Gemini API (extract new events, skip duplicates)
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
├── layers/
│   └── dependencies/
│       └── requirements.txt      # shared Lambda dependencies
├── src/                          # application source code packaged into Lambda
│   ├── main.py                   # local entry point
│   ├── config.py                 # loads secrets from .env or Secrets Manager
│   ├── functions/
│   │   ├── run_pipeline/
│   │   │   └── pipeline.py       # EventBridge triggered Lambda
│   │   └── slack_handler/
│   │       └── handler.py        # API Gateway triggered Lambda
│   ├── models/
│   │   └── event.py
│   └── services/
│       ├── credentials.py
│       ├── declined_events.py
│       ├── gcal.py
│       ├── gemini.py
│       ├── gmail.py
│       ├── prompt.py
│       └── slack_client.py       # Slack Web API client
└── tests/
    ├── test_declined_events.py
    ├── test_gcal.py
    ├── test_gemini.py
    ├── test_gmail.py
    ├── test_slack_client.py
    └── test_slack_handler.py
```

## Credentials

Local dev uses a `.env` file. Production secrets are stored in AWS Secrets Manager under `life-admin/secrets`.

| Secret                 | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID                            |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret                        |
| `GOOGLE_REFRESH_TOKEN` | Obtained once via `src/services/google_quickstart.py` |
| `GOOGLE_API_KEY`       | Google API key                                    |
| `GEMINI_API_KEY`       | Gemini API key                                    |
| `EMAILS`               | Comma-separated attendee emails                   |
| `MAILBOXES`            | Comma-separated Gmail label names to scan         |
| `SLACK_BOT_USER_TOKEN` | Slack Bot User OAuth token for Web API calls      |
| `SLACK_SIGNING_SECRET` | Slack signing secret for request verification     |

## Setup

```bash
pip install -e .
```

### Testing

```bash
pip install -e ".[dev]"
PYTHONPATH=src pytest
```

### Deploy

```bash
sam build
sam deploy
```

If `sam deploy` hangs, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
