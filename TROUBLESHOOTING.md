# Troubleshooting

## `sam deploy` hangs

Use these fallbacks when `sam deploy` hangs during package upload.

### Function code only

If only function code changed, update the two Lambda functions directly:

```bash
sam build

SLACK_FUNCTION=$(aws cloudformation describe-stack-resource \
  --stack-name life-admin \
  --logical-resource-id SlackHandlerFunction \
  --region ap-southeast-2 \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

RUN_PIPELINE_FUNCTION=$(aws cloudformation describe-stack-resource \
  --stack-name life-admin \
  --logical-resource-id RunPipelineFunction \
  --region ap-southeast-2 \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

cd .aws-sam/build/SlackHandlerFunction
zip -qr /tmp/slack-handler.zip .

cd ../RunPipelineFunction
zip -qr /tmp/run-pipeline.zip .

aws lambda update-function-code \
  --function-name "$SLACK_FUNCTION" \
  --zip-file fileb:///tmp/slack-handler.zip \
  --region ap-southeast-2

aws lambda update-function-code \
  --function-name "$RUN_PIPELINE_FUNCTION" \
  --zip-file fileb:///tmp/run-pipeline.zip \
  --region ap-southeast-2
```

Direct function upload does not update infrastructure, environment variables, IAM permissions, API Gateway, EventBridge, or the Lambda layer.

### Function code and `template.yaml` config

If `template.yaml` config changed, update Lambda code directly, then apply a CloudFormation change set from a manually packaged template. This reuses the existing deployed Lambda layer, so only use it when layer dependencies have not changed.

```bash
sam build

SLACK_FUNCTION=$(aws cloudformation describe-stack-resource \
  --stack-name life-admin \
  --logical-resource-id SlackHandlerFunction \
  --region ap-southeast-2 \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

RUN_PIPELINE_FUNCTION=$(aws cloudformation describe-stack-resource \
  --stack-name life-admin \
  --logical-resource-id RunPipelineFunction \
  --region ap-southeast-2 \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

cd .aws-sam/build/SlackHandlerFunction
zip -qr /tmp/slack-handler.zip .

cd ../RunPipelineFunction
zip -qr /tmp/run-pipeline.zip .

aws lambda update-function-code \
  --function-name "$SLACK_FUNCTION" \
  --zip-file fileb:///tmp/slack-handler.zip \
  --region ap-southeast-2

aws lambda update-function-code \
  --function-name "$RUN_PIPELINE_FUNCTION" \
  --zip-file fileb:///tmp/run-pipeline.zip \
  --region ap-southeast-2

aws lambda wait function-updated \
  --function-name "$SLACK_FUNCTION" \
  --region ap-southeast-2

aws lambda wait function-updated \
  --function-name "$RUN_PIPELINE_FUNCTION" \
  --region ap-southeast-2
```

Upload the small function zips to the existing SAM S3 bucket:

```bash
BUCKET=aws-sam-cli-managed-default-samclisourcebucket-sjhwnc6pcoxa
SLACK_HASH=$(shasum -a 256 /tmp/slack-handler.zip | awk '{print $1}')
RUN_PIPELINE_HASH=$(shasum -a 256 /tmp/run-pipeline.zip | awk '{print $1}')

aws s3api put-object \
  --bucket "$BUCKET" \
  --key "life-admin/manual/$SLACK_HASH-slack-handler.zip" \
  --body /tmp/slack-handler.zip \
  --region ap-southeast-2

aws s3api put-object \
  --bucket "$BUCKET" \
  --key "life-admin/manual/$RUN_PIPELINE_HASH-run-pipeline.zip" \
  --body /tmp/run-pipeline.zip \
  --region ap-southeast-2
```

Create a packaged template from the currently deployed template, then edit it to match the local `template.yaml` config changes:

```bash
aws cloudformation get-template \
  --stack-name life-admin \
  --region ap-southeast-2 \
  --template-stage Original \
  --query TemplateBody \
  --output text > /tmp/life-admin-packaged-template.yaml
```

In `/tmp/life-admin-packaged-template.yaml`:

- keep `DependenciesLayer.Properties.ContentUri` pointing at the existing deployed S3 object
- set `SlackHandlerFunction.Properties.CodeUri` to `s3://$BUCKET/life-admin/manual/$SLACK_HASH-slack-handler.zip`
- set `RunPipelineFunction.Properties.CodeUri` to `s3://$BUCKET/life-admin/manual/$RUN_PIPELINE_HASH-run-pipeline.zip`
- apply the same config/IAM/resource edits made in local `template.yaml`

Validate and deploy the packaged template with a change set:

```bash
sam validate --template-file /tmp/life-admin-packaged-template.yaml --lint

CHANGE_SET="life-admin-manual-$(date -u +%Y%m%d-%H%M%S)"

aws cloudformation create-change-set \
  --stack-name life-admin \
  --change-set-name "$CHANGE_SET" \
  --template-body file:///tmp/life-admin-packaged-template.yaml \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --region ap-southeast-2

aws cloudformation wait change-set-create-complete \
  --stack-name life-admin \
  --change-set-name "$CHANGE_SET" \
  --region ap-southeast-2

aws cloudformation describe-change-set \
  --stack-name life-admin \
  --change-set-name "$CHANGE_SET" \
  --region ap-southeast-2

aws cloudformation execute-change-set \
  --stack-name life-admin \
  --change-set-name "$CHANGE_SET" \
  --region ap-southeast-2

aws cloudformation wait stack-update-complete \
  --stack-name life-admin \
  --region ap-southeast-2
```
