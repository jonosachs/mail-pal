# Event Miner 📅

Automated AI mail filter tool that mines your inbox for important events daily and creates calendar events for each, with one-click approval via Slack. 

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

## Credentials

Local dev uses a `.env` file. Production secrets are stored in AWS Secrets Manager under `life-admin/secrets`.

| Secret                      | Description                                                   |
| --------------------------- | ------------------------------------------------------------ |
| `GOOGLE_CLIENT_ID`          | Google OAuth client ID                                       |
| `GOOGLE_CLIENT_SECRET`      | Google OAuth client secret                                   |
| `GOOGLE_REFRESH_TOKEN`      | Obtained once via `src/services/google/google_quickstart.py` |
| `GEMINI_API_KEY`            | Gemini API key                                              |
| `EXTRACT_EVENTS_FROM_EMAILS`| Comma-separated Gmail addresses to scan for events          |
| `EVENT_ATTENDEES_EMAILS`    | Comma-separated attendee emails for created events          |
| `USER_SPECIFIC_PROMPT`      | Extra prompt context personalising event extraction         |
| `SLACK_BOT_USER_TOKEN`      | Slack Bot User OAuth token for Web API calls                |
| `SLACK_SIGNING_SECRET`      | Slack signing secret for request verification               |
| `SLACK_WEBHOOK_URL`         | Slack incoming webhook for approval messages                |

## Requirements

- [uv](https://docs.astral.sh/uv/) — manages the virtualenv, the lockfile and Python itself
- Python 3.13 (installed by uv; pinned in `.python-version` to match the Lambda runtime)
- AWS CLI configured with credentials for the target account
- AWS SAM CLI for build and deploy
- Google Cloud OAuth credentials with Gmail and Calendar API access
- Gemini API key
- Slack app with bot token, signing secret, and interactivity enabled
- AWS Secrets Manager secret named `life-admin/secrets` (override with the `SecretName` template parameter)

The DynamoDB table is created by the stack — no manual setup needed.

## Setup

```bash
make install          # create .venv from uv.lock
```

Populate `.env` with the secrets listed above for local runs.

### Commands

| Command                 | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `make install`          | Create/refresh the local virtualenv from `uv.lock`       |
| `make run`              | Run the pipeline locally against live Gmail/Gemini/Slack |
| `make test`             | Run unit tests (integration tests deselected)            |
| `make test-integration` | Run tests that hit live Slack, Google and Gemini         |
| `make lint`             | Ruff lint and format check                               |
| `make format`           | Apply Ruff formatting                                    |
| `make validate`         | Lint `template.yaml` with cfn-lint                       |
| `make deploy`           | Validate, build and deploy via SAM                       |
| `make deps`             | Regenerate `uv.lock` and the layer's `requirements.txt`  |

### Dependencies

`pyproject.toml` is the only file to edit by hand. After changing it, run `make deps` to regenerate
`uv.lock` and `layers/dependencies/requirements.txt`, then commit both. Runtime dependencies ship in
the Lambda layer; the `dev` group (pytest, ruff, cfn-lint, boto3) does not.

### CI

`.github/workflows/ci.yml` runs lint, template validation and unit tests on every push to `main` and
on pull requests. Integration tests are excluded — they need live credentials.

### Deploy

```bash
make deploy
```

If `sam deploy` hangs, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
