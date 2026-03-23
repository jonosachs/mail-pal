from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import Slack

gmail = Gmail()
gemini = Gemini()
slack = Slack()

emails = gmail.get_mail(max_results=5)
cal_events = gemini.extract_events(emails)

for e in cal_events:
  msg = slack.build_approval_message(e)
  slack.send(msg)