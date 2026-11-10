# Quartz v4 Static Site & OCI Deployment (`citsit`)

This directory contains the configuration and preprocessor that build the [Quartz v4](https://github.com/jackyzha0/quartz) site for `citsit.168-138-184-104.sslip.io` while keeping the root repository 100% compatible with GitBook (`README.md` + `SUMMARY.md`).

## How It Works

1. **`prepare_content.py`**:
   - Reads `SUMMARY.md` to preserve exact section titles and sidebar ordering.
   - Copies all Markdown files into Quartz's `content/` directory, mapping `<folder>/README.md` to `<folder>/index.md` and rewriting relative Markdown links outside fenced code blocks.
   - Converts GitBook `{% embed url="..." %}` tags and `<figure><img src=".../.gitbook/assets/...">` blocks into standard Markdown links and images under `content/assets/`.
   - Injects the `SUMMARY.md` ordering map into `quartz.layout.ts`.
2. **`quartz.config.ts` & `quartz.layout.ts`**:
   - Configures Quartz v4 with instant client-side SPA routing, hover popovers, full-text FlexSearch (`Ctrl+K`), KaTeX math rendering, Graph View, and `SUMMARY.md`-ordered Explorer navigation.
3. **`Dockerfile` & `nginx.conf`**:
   - Multi-stage build using pinned Quartz v4 commit `d25a6eabf96751ffca56f8a8139272def7a65041` and rootless `nginxinc/nginx-unprivileged:1.27-alpine` (`UID 101:101`, `read_only: true` rootfs, `/health` endpoint on port `8080`).

## Local Validation

```bash
python3 -m unittest discover -s deploy/quartz -p 'test_*.py' -v
```
