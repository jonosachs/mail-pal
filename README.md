# Life Admin

Scans emails daily for action items, extracts calendar events using Gemini AI, and sends one-click approve/deny notifications via Slack. On approval, creates the event in Google Calendar.

## Infra

```text
- [x] AWS EventBridge          → triggers RunPipeline daily
- [x] AWS Lambda: RunPipeline  → fetches emails, extracts events, requests approval
- [x] AWS Lambda: SlackHandler → handles approve/deny button clicks
- [x] AWS API Gateway          → public URL for SlackHandler
- [x] AWS Secrets Manager      → stores all credentials
```

## Services

```
- [x] Gmail API        → read emails from configured mailboxes
- [x] Google Calendar  → create events + send invites
- [x] Gemini API       → extract events from emails (structured output)
- [x] Slack            → approval UI with interactive buttons
```

## Code

```
life-admin/
├── .gitignore
├── pyproject.toml                # dependencies
├── template.yaml                 # AWS SAM deployment config
├── samconfig.toml                # SAM deploy settings
├── conftest.py                   # pytest configuration
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

```
Local dev: .env file → python-dotenv
Production: AWS Secrets Manager (life-admin/secrets) → fetched at Lambda startup

Stored secrets:
├── GOOGLE_CLIENT_ID
├── GOOGLE_CLIENT_SECRET
├── GOOGLE_REFRESH_TOKEN    # obtained once by running services/google_quickstart.py
├── GOOGLE_API_KEY
├── GEMINI_API_KEY
├── EMAILS                  # comma-separated list of attendee emails
├── MAILBOXES               # comma-separated Gmail label names to scan
├── SLACK_WEBHOOK_URL
└── SLACK_SIGNING_SECRET
```

## Setup

```bash
pip install -e .
```

### Deploy

```bash
sam build
sam deploy
```
