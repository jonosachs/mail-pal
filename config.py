from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import ClientError
import json

load_dotenv(override=True)

KEYS = [
  'GOOGLE_CLIENT_ID',
  'GOOGLE_CLIENT_SECRET', 
  'GOOGLE_API_KEY',       
  'GOOGLE_REFRESH_TOKEN', 
  'MAILBOXES',            
  'GEMINI_API_KEY',
  'EMAILS',
  'SLACK_APP_ID',
  'SLACK_CLIENT_ID',
  'SLACK_CLIENT_SECRET',
  'SLACK_SIGNING_SECRET',
  'SLACK_VERIFICATION_TOKEN',
  'SLACK_WEBHOOK_URL'
]

# Only runs once when the module is first imported
_secrets = None

def load_secrets():
  '''Try obtain secrets from cache else get from AWS or locally if not running in Lambda'''  
  
  global _secrets
  
  if not _secrets:  
    if os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
      _secrets = get_secrets_fromAWS()
    else:
      _secrets = get_secrets_locally() 
  return _secrets
  
def get_secrets_locally():
  secrets = {}
  for key in KEYS:
    secrets[key] = os.getenv(key)
  
  for key, value in secrets.items():
    if not value:
      print(f"{key}: {'MISSING'}")
  
  return secrets 

def get_secrets_fromAWS():
  '''Get secrets from AWS Secret Manager'''
  
  secret_name = "life-admin/secrets"
  region_name = "ap-southeast-2"

  # Create a Secrets Manager client
  session = boto3.session.Session()
  client = session.client(
      service_name='secretsmanager',
      region_name=region_name
  )

  try:
      get_secret_value_response = client.get_secret_value(
          SecretId=secret_name
      )
  except ClientError as e:
      # For a list of exceptions thrown, see
      # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
      raise e

  secrets_AWS = json.loads(get_secret_value_response['SecretString'])
  
  secrets_local = {}
  for key in KEYS:  
    secrets_local[key] = secrets_AWS[key]
  
  for key, value in secrets_local.items():
    if not value:
      print(f"{key}: {'MISSING'}")
      
  return secrets_local