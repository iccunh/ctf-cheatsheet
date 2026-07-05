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
