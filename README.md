# Mail PAL 📬

Automated AI mail filter tool that extracts important events and action items from your inbox and creates calendar events for each, with one-click approval via Slack. Built to save time and reduce message fatigue.

## How it works

1. **AWS EventBridge** triggers the `RunPipelineFunction` Lambda daily
2. **RunPipelineFunction** fetches recent Gmail messages, checks existing calendar events and recently seen events, asks Gemini to extract new event candidates, stores each candidate in DynamoDB, and sends each to Slack for review
3. **Slack** presents approve/decline buttons, then sends the user interaction to `SlackHandlerFunction` via API Gateway
4. **SlackHandlerFunction** validates the Slack request and returns a `200 OK` within Slack's 3-second window, then asynchronously invokes `SlackWorkerFunction` to do the slow work
5. **SlackWorkerFunction** parses the user decision and creates the approved calendar event, or on decline updates Slack with an undo option

## Architecture

```
AWS EventBridge (scheduled cron)
    → AWS Lambda: RunPipelineFunction
        → Gmail API (fetch recent emails)
        → Google Calendar API (fetch existing bot-created events)
        → DynamoDB (fetch recently seen events)
        → Gemini API (extract new events, skip duplicates)
        → DynamoDB (store proposed events)
        → Slack (send approval messages)

Slack (button click)
    → AWS API Gateway
        → AWS Lambda: SlackHandlerFunction (validate + ack 200 OK)
            → AWS Lambda: SlackWorkerFunction (async, InvocationType="Event")
                → Google Calendar API (create event on approve)
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
│   │       ├── handler.py        # API Gateway-triggered Lambda (validate + ack)
│   │       └── worker.py         # async Lambda that fulfils the user decision
│   ├── models/
│   │   ├── event.py
│   │   └── slack_action_payload.py
│   └── services/
│       ├── aws/
│       │   └── db.py             # DynamoDB access
│       ├── google/
│       │   ├── credentials.py
│       │   ├── gcal.py
│       │   ├── gmail.py
│       │   └── google_quickstart.py  # one-off OAuth refresh-token helper
│       ├── llm/
│       │   ├── gemini.py         # Gemini event extraction
│       │   ├── llm_base.py       # LLM abstract base class
│       │   └── prompt.py
│       ├── slack/
│       │   ├── client.py         # Slack Web API client
│       │   ├── event_review.py   # approve/decline workflow
│       │   ├── msg_builder.py    # Slack Block Kit payloads
│       │   ├── parser.py         # Slack payload parsing
│       │   └── validator.py      # Slack request verification
│       └── http_responses.py
└── tests/
    ├── test_db.py
    ├── test_gcal.py
    ├── test_gemini.py
    ├── test_gmail.py
    ├── test_slack_client.py
    └── test_slack_handler.py
```

## Credentials

Local dev uses a `.env` file. Production secrets are stored in AWS Secrets Manager under `life-admin/secrets`.

| Secret                      | Description                                                   |
| --------------------------- | ------------------------------------------------------------ |
| `GOOGLE_CLIENT_ID`          | Google OAuth client ID                                       |
| `GOOGLE_CLIENT_SECRET`      | Google OAuth client secret                                   |
| `GOOGLE_REFRESH_TOKEN`      | Obtained once via `src/services/google/google_quickstart.py` |
| `GEMINI_API_KEY`            | Gemini API key                                              |
| `EXTRACT_EVENTS_FROM_EMAILS`| Comma-separated Gmail addresses to scan for events          |
| `SEND_EVENTS_TO_EMAILS`     | Comma-separated attendee emails for created events          |
| `USER_SPECIFIC_PROMPT`      | Extra prompt context personalising event extraction         |
| `SLACK_BOT_USER_TOKEN`      | Slack Bot User OAuth token for Web API calls                |
| `SLACK_SIGNING_SECRET`      | Slack signing secret for request verification               |
| `SLACK_WEBHOOK_URL`         | Slack incoming webhook for approval messages                |

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
