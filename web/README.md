# Web

Authors: myself, ziru

## Start

1. Run locally and read the source.
2. Find where the flag can be read: file, DB, admin page, internal service, bot cookie.
3. Map all inputs: query/body params, JSON, headers, cookies, path, redirects, uploaded files.
4. Check parser gaps: duplicate params, mixed GET/POST, content type, URL parsing, encoding.
5. If a WAF/proxy exists, prove the bug against the origin first, then compare origin vs WAF parsing.
6. Read dependency docs only after finding a suspicious sink or version.

## Pick The Page

| Symptom | Page |
| --- | --- |
| Query string reaches SQL | [SQL Injection](sql-injection.md) |
| Mongo / JSON query reaches DB | [NoSQL Injection](nosql.md) |
| `/graphql`, graph API, typed queries | [GraphQL](graphql.md) |
| Login, JWT, signed cookie, role check | [Auth](auth.md) |
| IDOR, mass assignment, reset flow, race | [API / Logic](api-logic.md) |
| Duplicate params, nested query, raw forward | [Request Parsing](request-parsing.md) |
| Proxy path/header mismatch | [Proxy](proxy.md) |
| WAF block, signature bypass, origin/proxy parser mismatch | [WAF / Filter Bypass](waf.md) |
| CL/TE mismatch, poisoned next request | [Desync](desync.md) |
| URL fetcher / preview / webhook | [SSRF](ssrf.md) |
| Cache hit on private/dynamic response | [Cache](cache.md) |
| WebSocket / Socket.IO messages | [WebSocket](websocket.md) |
| File upload / image upload / write path | [Upload](upload.md) |
| File path / download / template include | [LFI](lfi.md) |
| Reflected/stored HTML shown to browser bot | [XSS](xss.md) |
| `{{7*7}}`, `${7*7}`, template render | [SSTI](ssti.md) |
| Serialized cookie / object / session | [Deserialization](deserialization.md) |
| `__proto__`, polluted config, EJS gadget | [Prototype Pollution](prototype-pollution.md) |
| Java EL / Spring params / Tomcat internals | [Java / Spring](java-spring.md) |
| React Server Components / Next.js App Router | [React / Next.js](react.md) |
| CORS, postMessage, opener, SameSite | [Browser Security](browser-security.md) |
| Debug mode, actuator, `.env`, default secrets | [Framework Misconfig](framework-misconfig.md) |
| Gremlin / graph traversal eval | [Graph Query](graph-query.md) |
| PHP wrappers, webshells, filter chains | [PHP](php.md) |
| XML parser / SOAP / SVG upload | [XXE](xxe.md) |
| Shell command or tool wrapper | [Command Injection](../linux/command-injection.md) |

## Try

```text
' OR '1'='1'-- -
' ORDER BY 1-- -
http://internal.:5001/
http://127.0.0.1/
../../../../flag.txt
php://filter/convert.base64-encode/resource=index.php
{{7*7}}
<svg/onload=alert(1)>
;id
?id=1&id=2
<!DOCTYPE root [ <!ENTITY xxe SYSTEM "file:///flag.txt"> ]>
```

## Parser Tricks

```text
duplicate params: ?id=1&id=2
mixed source: GET id + POST id + Cookie id
content types: json/form/xml/plain
encoding: %2e%2e%2f, double encoding, unicode case
hostnames: localhost., internal., 127.0.0.1.
headers: Host, X-Forwarded-Host, X-Original-URL, Referer
WAF diff: test same payload at origin and proxy, then mutate one blocked token at a time
```

## References

* [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
* [HackTricks Web](https://book.hacktricks.wiki/en/pentesting-web/index.html)
* [PortSwigger Web Security Academy](https://portswigger.net/web-security)
