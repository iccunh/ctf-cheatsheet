# Framework Misconfig

## Flask

```text
/console
/werkzeug/console
/?__debugger__=yes&cmd=pinauth&pin=PIN&s=SECRET
```

Look for:

```text
SECRET_KEY
FLASK_DEBUG=1
Werkzeug debugger active
```

## Django

```text
/admin/
/debug/
/__debug__/
/static/../settings.py
```

Leaks to use:

```text
SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=['*']
DATABASES
```

## Laravel

```text
/.env
/storage/logs/laravel.log
```

Interesting:

```text
APP_KEY=
APP_DEBUG=true
DB_PASSWORD=
```

## Rails

```text
/rails/info/routes
/assets/../../config/master.key
/config/master.key
```

Interesting:

```text
secret_key_base
RAILS_MASTER_KEY
credentials.yml.enc
```

## Express

```text
trust proxy enabled
default session secret
debug routes
error stack trace
```

```http
X-Forwarded-For: 127.0.0.1
X-Forwarded-Host: localhost
X-Forwarded-Proto: https
```

## Spring

```text
/actuator
/actuator/env
/actuator/heapdump
/actuator/mappings
/actuator/beans
/actuator/configprops
```

