# Web

## Start

1. Run locally and read the source.
2. Find where the flag can be read: file, DB, admin page, internal service, bot cookie.
3. Map all inputs: query/body params, JSON, headers, cookies, path, redirects, uploaded files.
4. Check parser gaps: duplicate params, mixed GET/POST, content type, URL parsing, encoding.
5. Read dependency docs only after finding a suspicious sink or version.

## Pick The Page

| Symptom | Page |
| --- | --- |
| Query string reaches SQL | [SQL Injection](sql-injection.md) |
| Mongo / JSON query reaches DB | [NoSQL Injection](nosql.md) |
| Login, JWT, signed cookie, role check | [Auth](auth.md) |
| Duplicate params, nested query, raw forward | [Request Parsing](request-parsing.md) |
| URL fetcher / preview / webhook | [SSRF](ssrf.md) |
| File upload / image upload / write path | [Upload](upload.md) |
| File path / download / template include | [LFI](lfi.md) |
| Reflected/stored HTML shown to browser bot | [XSS](xss.md) |
| `{{7*7}}`, `${7*7}`, template render | [SSTI](ssti.md) |
| Serialized cookie / object / session | [Deserialization](deserialization.md) |
| `__proto__`, polluted config, EJS gadget | [Prototype Pollution](prototype-pollution.md) |
| Java EL / Spring params / Tomcat internals | [Java / Spring](java-spring.md) |
| Gremlin / graph traversal eval | [Graph Query](graph-query.md) |
| PHP wrappers, webshells, filter chains | [PHP](php.md) |
| XML parser / SOAP / SVG upload | [XXE](xxe.md) |
| Shell command or tool wrapper | [Command Injection](../linux/command-injection.md) |

## Try

```text
' OR '1'='1'-- -
http://internal.:5001/
../../../../flag.txt
{{7*7}}
<svg/onload=alert(1)>
;id
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
```

## References

* [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
* [HackTricks Web](https://book.hacktricks.wiki/en/pentesting-web/index.html)
* [PortSwigger Web Security Academy](https://portswigger.net/web-security)
