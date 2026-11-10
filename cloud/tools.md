# Tools

## AWS

| Tool | Use |
| --- | --- |
| [awscli](https://aws.amazon.com/cli/) | Primary API client |
| [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) | Scripting, presigned URLs |
| [Pacu](https://github.com/RhinoSecurityLabs/pacu) | AWS exploitation framework |
| [CloudFox](https://github.com/BishopFox/cloudfox) | Enumeration and attack paths |
| [enumerate-iam](https://github.com/andresriancho/enumerate-iam) | Brute force allowed API calls |
| [PMapper](https://github.com/nccgroup/PMapper) | IAM graph and privesc paths |
| [ScoutSuite](https://github.com/nccgroup/ScoutSuite) | Multi-cloud audit |
| [Prowler](https://github.com/prowler-cloud/prowler) | Security assessment |
| [S3Scanner](https://github.com/sa7mon/S3Scanner) | Bucket discovery and permissions |
| [s3recon](https://github.com/aidenwallis/s3recon) | S3 enumeration |

## GCP

| Tool | Use |
| --- | --- |
| [gcloud](https://cloud.google.com/sdk/gcloud) | Primary API client |
| [gsutil](https://cloud.google.com/storage/docs/gsutil) | Cloud Storage |
| [GCPBucketBrute](https://github.com/RhinoSecurityLabs/GCPBucketBrute) | Bucket discovery |
| [gcp_enum](https://github.com/GoogleCloudPlatform/security-analytics) | Enumeration helpers |

## Azure

| Tool | Use |
| --- | --- |
| [az](https://learn.microsoft.com/cli/azure/) | Primary API client |
| [AzureHound](https://github.com/BloodHoundAD/AzureHound) | Entra ID / Azure graph |
| [ROADTools](https://github.com/dirkjanm/ROADtools) | Entra ID enumeration |
| [MicroBurst](https://github.com/NetSPI/MicroBurst) | Azure recon and privesc |
| [ScoutSuite](https://github.com/nccgroup/ScoutSuite) | Multi-cloud audit |

## Kubernetes

| Tool | Use |
| --- | --- |
| [kubectl](https://kubernetes.io/docs/reference/kubectl/) | Primary client |
| [peirates](https://github.com/inguardians/peirates) | Pod escape and enumeration |
| [kubeletctl](https://github.com/cyberark/kubeletctl) | Kubelet API |
| [kube-hunter](https://github.com/aquasecurity/kube-hunter) | Cluster recon |
| [kube-bench](https://github.com/aquasecurity/kube-bench) | CIS benchmark |
| [Trivy](https://github.com/aquasecurity/trivy) | Image and config scanning |

## Generic

| Tool | Use |
| --- | --- |
| [nuclei](https://github.com/projectdiscovery/nuclei) | Templated checks |
| [interactsh](https://github.com/projectdiscovery/interactsh) | OAST / SSRF callbacks |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | Secret scanning |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning |
| [jq](https://jqlang.github.io/jq/) | JSON parsing |
| [curl](https://curl.se/) | Raw HTTP and metadata |

## Quick Installs

```bash
pip install boto3 awscli
pip install scoutsuite prowler

go install github.com/BishopFox/cloudfox@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

git clone https://github.com/RhinoSecurityLabs/pacu
git clone https://github.com/RhinoSecurityLabs/cloudgoat
```

## References

* [HackTricks Cloud](https://book.hacktricks.wiki/en/pentesting-cloud/index.html)
* [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
* [CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat)
* [flaws.cloud](http://flaws.cloud/)
* [AWS IAM privesc](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/)
