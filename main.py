from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import Slack

gmail = Gmail()
gemini = Gemini()
slack = Slack()

emails = gmail.get_mail()
events = gemini.extract_events(emails)
print(events)

e = slack.build_approval_message(events[0])
slack.send(e)

