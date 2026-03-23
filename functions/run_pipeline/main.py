from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import Slack

def lambda_handler(_event, _context):                                                                                     
  gmail = Gmail()
  gemini = Gemini()
  slack = Slack()

  emails = gmail.get_mail()
  cal_events = gemini.extract_events(emails)
  
  for e in cal_events:
    msg = slack.build_approval_message(e)
    slack.send(msg)
                                         
  return {"statusCode": 200, "body": "Pipeline complete"}