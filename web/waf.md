# WAF / Filter Bypass

## Workflow

```text
1. Run the backend without the WAF and prove the bug directly.
2. Send the same payload through the WAF and record the exact block reason/status/header.
3. Read or infer WAF normalization: URL decode, JSON escapes, charset, multipart, compression, size limits.
4. Compare WAF parsing with backend parsing.
5. Mutate one blocked token at a time while preserving backend meaning.
6. Leak through a normal application response path: redirect header, error text, rendered HTML, cache key, callback.
```

Do not start with random payload lists. First identify the semantic contract the backend accepts, then find encodings or syntax variants the WAF does not canonicalize.

## Disable Locally

Use this to test the real bug before fighting the filter.

```bash
# If compose has app + waf services, call the app service directly by exposing its port.
docker compose up -d app
docker compose port app 3000

# Run the app service directly with a host port, without starting the waf service.
docker compose run --rm -p 3000:3000 app

# Or temporarily publish the app port in docker-compose.yml:
# services:
#   app:
#     ports:
#       - "3000:3000"

# Or run the origin by hand with the same env.
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

For reverse proxies, another option is to start the WAF with `BACKEND=http://127.0.0.1:3000` and compare:

```text
origin: http://127.0.0.1:3000/
waf:    http://127.0.0.1:8080/
```

## Parser Differential Table

Write this table while solving.

| Payload Feature | Backend Meaning | WAF View |
| --- | --- | --- |
| Duplicate parameter | first value / last value / array | different value selected |
| Duplicate multipart boundary | one parser uses first boundary | other parser uses last boundary |
| UTF-16LE field | backend decodes text | WAF scans raw bytes |
| `+` in numeric grammar | backend parses as number | regex expects digits only |
| Hex number | backend accepts base 16 | WAF expects decimal |
| JSON escapes | backend unescapes once | WAF unescapes zero/two times |
| Percent encoding | backend decodes after routing | WAF decodes before routing |
| Compression | backend decompresses | WAF rejects or skips body |

## Common Normalization Gaps

```text
%2f vs /, double encoding, mixed-case hex
\u0061 JSON escapes, invalid escapes, overlong unicode assumptions
UTF-8 vs latin1 vs UTF-16LE form fields
multipart duplicate boundary params
duplicate Content-Type / charset params
duplicate query/body keys
GET param + POST param with same name
path normalization before/after proxy forwarding
HTTP/2 pseudo-header to HTTP/1 downgrade
case-sensitive signatures vs case-insensitive backend
numeric grammar: 0, +0, -0, 00, 0x0, hex IDs
```

## Multipart Checks

```http
Content-Type: multipart/form-data; boundary=REAL; boundary=FAKE
```

Test which boundary each parser uses. Make `FAKE` harmless for the WAF and put the real payload under `REAL`.

```text
--FAKE
Content-Disposition: form-data; name="safe"

hello
--FAKE--
--REAL
Content-Disposition: form-data; name="payload"
Content-Type: text/plain; charset=utf-16le

<utf16le bytes>
--REAL--
```

Other multipart levers:

```text
part Content-Type charset
part filename vs field handling
Content-Disposition name* RFC5987 encoding
extra CRLF before/after final boundary
empty part before malicious part
same field name repeated
```

## Response Leak Ideas

When code execution works but the HTTP body does not show command output:

```text
throw framework redirect with secret in Location / framework redirect header
write secret into cacheable route then fetch it
set response cookie/header if framework exposes it
trigger error whose digest/message includes controlled text
request outbound webhook if egress is allowed
write under public/static directory then GET it
```

## Discipline

```text
Prove origin bug first.
Keep a harmless baseline request.
Change one encoding or token per request.
Log WAF status, headers, and response body.
Prefer parser source code over assumptions.
When bypassing signatures, preserve backend semantics first and aesthetics last.
```
