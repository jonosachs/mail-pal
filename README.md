# Life Admin

Filter emails daily for action items and create calendar events for each, with one-click approval via Slack. In progress..

## Infra

```text
- [ ] AWS EventBridge          → triggers RunPipeline every hour
- [ ] AWS Lambda: RunPipeline  → fetches emails, extracts events, requests approval
- [ ] AWS Lambda: SlackHandler → handles approve/deny button clicks
- [ ] AWS API Gateway          → public URL for SlackHandler
- [ ] AWS Secrets Manager      → stores all credentials
```

## Services

```
- [x] Gmail API        → read emails, send summary
- [x] Google Calendar  → create events + send invites
- [x] Claude API       → extract events + action items
- [x] Slack            → approval UI
```

## Code

```
life-admin/
├── .env                      # local secrets (never committed)
├── .gitignore
├── requirements.txt
├── template.yaml             # AWS SAM deployment config
├── services/
│   ├── gmail.py
│   ├── calendar.py
│   ├── claude.py
│   └── slack.py
├── models/
│   └── event.py
├── functions/
│   ├── run_pipeline/
│   │   └── main.py           # EventBridge triggered
│   └── slack_handler/
│       └── main.py           # API Gateway triggered
└── config.py                 # loads secrets from .env or Secrets Manager
```

## Credentials

```
Local dev: .env file → python-dotenv
Production: AWS Secrets Manager → fetched at Lambda startup

Stored secrets:
├── ANTHROPIC_API_KEY
├── GOOGLE_CLIENT_ID
├── GOOGLE_CLIENT_SECRET
├── GOOGLE_REFRESH_TOKEN # obtained once by running gmail_quickstart.py
└── SLACK_WEBHOOK_URL
```

## Requirements

```bash
pip install -r requirements.txt
```

Slack CLI
To install:

```bash
curl -fsSL https://downloads.slack-edge.com/slack-cli/install.sh | bash
```
