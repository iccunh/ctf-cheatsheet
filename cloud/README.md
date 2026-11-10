# Cloud

## Start

1. Identify the provider: metadata endpoint, hostnames, SDK headers, error format, env names.
2. Identify the primitive: SSRF, leaked key, public bucket, web RCE, pod token, CI token.
3. Identify the identity: `sts get-caller-identity`, token claims, service account, managed identity.
4. Find the flag store: object storage, secret manager, parameter store, env, user-data, K8s secret.
5. Escalate: metadata, IAM privesc, role chaining, public resource, confused deputy.
6. Exfiltrate and clean up. Refresh expired credentials when needed.

## Pick The Page

| Symptom | Page |
| --- | --- |
| URL fetcher, preview, webhook, SSRF | [Metadata / IMDS](metadata.md) |
| AWS keys, `arn:aws`, S3, Lambda, ECS | [AWS](aws.md) |
| GCP service account, `gs://`, `googleapis.com` | [GCP](gcp.md) |
| Azure managed identity, `blob.core.windows.net` | [Azure](azure.md) |
| K8s token, pod, service account, `kubectl` | [Kubernetes](kubernetes.md) |
| GitHub Actions, GitLab CI, CodeBuild, runner | [CI/CD](cicd.md) |
| `terraform.tfstate`, provider, `terraform init` | [Terraform](terraform.md) |
| Need tooling | [Tools](tools.md) |

## Provider Fingerprint

| Clue | Provider |
| --- | --- |
| `169.254.169.254/latest/meta-data/`, `arn:aws`, `AKIA` / `ASIA`, `amazonaws.com` | AWS |
| `metadata.google.internal`, `Metadata-Flavor: Google`, `GOOGLE_`, `*.googleapis.com`, `ya29.` | GCP |
| `169.254.169.254/metadata/instance`, `Metadata: true`, `*.blob.core.windows.net`, `AZURE_` | Azure |
| `100.100.100.200`, `aliyun`, `Aliyun` | Alibaba Cloud |
| `/opc/v2/`, `Authorization: Bearer Oracle` | Oracle Cloud |
| `169.254.169.254/metadata/v1/`, `digitalocean` | DigitalOcean |
| `KUBERNETES_SERVICE_HOST`, `serviceaccount/token`, `kubectl` | Kubernetes |

Headers are often the fastest fingerprint:

```text
x-amz-* / x-amz-security-token     AWS
Metadata-Flavor: Google            GCP
Metadata: true                     Azure
Authorization: Bearer Oracle       OCI
```

## Universal Loot Checklist

```text
env
cat /proc/1/environ
cat /proc/self/environ
~/.aws/credentials ~/.aws/config
~/.config/gcloud ~/.azure
~/.docker/config.json
/var/run/secrets/kubernetes.io/serviceaccount/token
/root/.ssh
/tmp /var/tmp /dev/shm
mount
ls -la /
find / -maxdepth 3 -iname '*flag*' 2>/dev/null
```

## Common Chains

```text
SSRF -> IMDS -> instance role -> S3 / Secrets Manager / SSM
SSRF -> ECS task metadata -> task role
Leaked CI token -> cloud API -> role
Public bucket -> object listing -> flag
K8s service account token -> API -> secret -> cloud identity
Web RCE -> env / metadata -> cloud creds -> IAM privesc
Leaked source -> hardcoded key -> cloud API
Leaked CI token -> runner workspace -> env secrets -> cloud role
Writable terraform state -> malicious provider -> cron apply -> RCE
SNS endpoint condition -> webhook -> token -> weak API Gateway -> private bucket
```

## Credential Cheat Sheet

```text
AWS   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
GCP   GOOGLE_APPLICATION_CREDENTIALS=/path/key.json
Azure AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_TENANT_ID
```

Temporary credentials need the session token too. Without it, AWS returns `InvalidClientTokenId`.

## First Commands After Getting Credentials

```bash
# AWS
aws sts get-caller-identity
aws iam get-account-authorization-details > auth.json
aws s3 ls
aws secretsmanager list-secrets
aws ssm describe-parameters
aws lambda list-functions
aws ec2 describe-instances

# GCP
gcloud auth list
gcloud projects list
gcloud storage ls
gcloud secrets list

# Azure
az account show
az resource list
az storage account list
az keyvault list
```

## Policy Error Messages

```text
no identity-based policy allows ...        -> identity policy missing
explicit deny in a resource-based policy   -> bucket / queue / resource policy
AccessDenied ... with an explicit deny     -> check resource policy conditions
not authorized to perform: sts:AssumeRole  -> trust policy or identity policy
```

`explicit deny` is a hint to read the resource policy, not to give up.

## References

* [HackTricks Cloud](https://book.hacktricks.wiki/en/pentesting-cloud/index.html)
* [AWS Documentation](https://docs.aws.amazon.com/)
* [Google Cloud Documentation](https://cloud.google.com/docs)
* [Microsoft Azure Documentation](https://learn.microsoft.com/azure/)
* [Kubernetes Documentation](https://kubernetes.io/docs/)
* [flaws.cloud](http://flaws.cloud/)
* [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat)
