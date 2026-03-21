from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import Slack
from services.prompt import Event
import datetime
from datetime import tzinfo as TzInfo

gmail = Gmail()
gemini = Gemini()
slack = Slack()

emails = gmail.get_mail()
events = gemini.extract_events(emails)
print(events)

e = slack.build_approval_message(events[0])
slack.send(e)

