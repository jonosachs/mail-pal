# Mail PAL

Automated AI mail filter tool that extracts important events and action items from your inbox and creates calendar events for each, with one-click approval via Slack. Built to save time and reduce message fatigue.

## How it works

1. **AWS EventBridge** triggers the `RunPipelineFunction` Lambda daily
2. **RunPipelineFunction** fetches recent Gmail messages, checks existing and recently declined events, asks Gemini to extract new event candidates, and sends each candidate to Slack for review
3. **Slack** presents approve/decline buttons, then sends the user interaction to `SlackHandlerFunction` via API Gateway
4. **SlackHandlerFunction** validates the Slack request, parses the user decision, creates approved calendar events, stores declined events, and updates Slack

## Architecture

```
AWS EventBridge (scheduled cron)
    → AWS Lambda: RunPipelineFunction
        → Gmail API (fetch recent emails)
        → Google Calendar API (fetch existing bot-created events)
        → Gemini API (extract new events, skip duplicates)
        → Slack (send approval messages)

Slack (button click)
    → AWS API Gateway
        → AWS Lambda: SlackHandlerFunction
            → Google Calendar API (create event)
            → DynamoDB (store declined events)
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
│   │   ├── pipeline/
│   │   │   └── handler.py        # EventBridge-triggered Lambda
│   │   └── slack/
│   │       └── handler.py        # API Gateway-triggered Lambda
│   ├── models/
│   │   ├── event.py
│   │   └── slack_action_payload.py
│   └── services/
│       ├── aws/
│       │   └── db.py             # DynamoDB access
│       ├── google/
│       │   ├── credentials.py
│       │   ├── gcal.py
│       │   ├── gemini.py
│       │   └── gmail.py
│       ├── llm/
│       │   ├── llm_base.py
│       │   └── prompt.py
│       ├── slack/
│       │   ├── client.py         # Slack Web API client
│       │   ├── event_review.py   # approve/decline workflow
│       │   ├── msg_builder.py    # Slack Block Kit payloads
│       │   ├── parser.py         # Slack payload parsing
│       │   └── validator.py      # Slack request verification
│       └── http_responses.py
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
| `GOOGLE_REFRESH_TOKEN` | Obtained once via `src/services/google/google_quickstart.py` |
| `GOOGLE_API_KEY`       | Google API key                                    |
| `GEMINI_API_KEY`       | Gemini API key                                    |
| `EMAILS`               | Comma-separated attendee emails                   |
| `MAILBOXES`            | Comma-separated Gmail label names to scan         |
| `SLACK_BOT_USER_TOKEN` | Slack Bot User OAuth token for Web API calls      |
| `SLACK_SIGNING_SECRET` | Slack signing secret for request verification     |

## Requirements

- Python 3.13 for deployed Lambda runtime; project metadata supports Python 3.9+
- AWS CLI configured with credentials for the target account
- AWS SAM CLI for build and deploy
- Google Cloud OAuth credentials with Gmail and Calendar API access
- Gemini API key
- Slack app with bot token, signing secret, and interactivity enabled
- AWS Secrets Manager secret named `life-admin/secrets`
- DynamoDB table named `Declined`

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
