# Services

## Gmail

Quickstart  
- https://developers.google.com/workspace/gmail/api/quickstart/python

**list** query params:
- https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list

Mail Filters: 
- https://support.google.com/mail/answer/7190

**get**
- https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get

## Google Calendar

**Event** shape:
- https://developers.google.com/workspace/calendar/api/v3/reference/events#resource

**insert** fields:
- https://developers.google.com/workspace/calendar/api/v3/reference/events/insert

**get** response shape:
- https://developers.google.com/workspace/calendar/api/v3/reference/events#resource-representations

**list** 
params:
- https://developers.google.com/workspace/calendar/api/v3/reference/events/list#parameters
response shape:
- https://developers.google.com/workspace/calendar/api/v3/reference/events/list#response

## Slack

**chat.postMessage**:
arguments:
- https://docs.slack.dev/reference/methods/chat.postMessage/#arguments
response:
- https://docs.slack.dev/reference/methods/chat.postMessage/#response

**chat.update**
response shape:
- https://docs.slack.dev/reference/methods/chat.update#response

Verify incoming requests from Slack
- https://docs.slack.dev/authentication/verifying-requests-from-slack

Section-block:
- https://docs.slack.dev/reference/block-kit/blocks/section-block/

Interactive block_actions payload
- https://docs.slack.dev/reference/interaction-payloads/block_actions-payload#examples

## AWS Serverless Application Model (AWS SAM)

SAM policy templates:
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html

## Dynamodb

Code examples:
- https://docs.aws.amazon.com/boto3/latest/guide/quickstart.html
- https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html

CloudFormation DynamoDB table:
- https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-dynamodb-table.html#aws-resource-dynamodb-table-syntax

SAM DynamoDB Policy Templates
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html#serverless-policy-template-table

**put_item**
- https://docs.aws.amazon.com/boto3/latest/reference/services/dynamodb/table/put_item.html

**get_item**
- https://docs.aws.amazon.com/boto3/latest/reference/services/dynamodb/table/get_item.html#DynamoDB.Table.get_item

**scan** - to retrieve all entries
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html
- https://docs.aws.amazon.com/boto3/latest/reference/services/dynamodb/client/scan.html
