# Attack & Defense

## Exploiter Submitter

```python
from subprocess import Popen, PIPE
import time
import re
import sys

names = [
    "AcRtf",
    "anak buah masfir cabang cikarang",
    "bang ini nama kelompoknya diisi apa",
    "CP Enjoyer",
    "CyberPewPew",
    "HCS - GaadaHandleCrypto",
    "HCS - kos0ng Fans Club",
    "HCS - murid mentor",
    "HengkerNgangNgong",
    "is_intern=False",
    "Keito",
    "kessoku no owari",
    "Mas Jossie tolong maju untuk ambil sembako",
    "Minus 1",
    "Peserta",
    "Sembarang Wes",
    "SHA-587",
    "Tiga Hacker Baik dan Rajin Menabung",
    "Tim Pisang Molen",
]
ips = [
    "10.100.101.101",
    "10.100.101.102",
    "10.100.101.103",
    "10.100.101.104",
    "10.100.101.105",
    "10.100.101.106",
    "10.100.101.107",
    "10.100.101.108",
    "10.100.101.109",
    "10.100.101.110",
    "10.100.101.111",
    "10.100.101.112",
    "10.100.101.113",
    "10.100.101.114",
    "10.100.101.115",
    "10.100.101.116",
    "10.100.101.117",
    "10.100.101.118",
    "10.100.101.119",
    "10.100.101.120",
]
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJRCI6ImMwYzY3ZGNmLTViMjUtNDQxNS04MWExLTU3NWJmMmY1M2JhNCIsIlVzZXJuYW1lIjoiTW9haSIsIklzQWRtaW4iOmZhbHNlLCJleHAiOjE2OTQ2Mjg5NDh9.oyTHmnmppkw0DHvIvsRm675JmVqeLVp83DaibmEgWTc"
interval = 60
filename = sys.argv[1]
while True:
    patch = []
    running_procs = []
    for i in range(len(names)):
        print("-----------------------------------------")
        print(i, names[i])
        ip = ips[i]
        proc = Popen(["python3", filename, ip], stdout=PIPE, stderr=PIPE)
        res = proc.stdout.read().decode()
        print(res)
        flag = re.findall(r"GEMASTIK\{.*\}", res)
        if len(flag) > 0:
            for x in range(len(flag)):
                running_procs.append(
                    [
                        names[i],
                        ips[i],
                        flag,
                        Popen(
                            [
                                "curl",
                                "--location",
                                "--request",
                                "POST",
                                "https://siber.gemastik.id/api/flag",
                                "--header",
                                "Authorization: Bearer " + token,
                                "--header",
                                "Content-Type: application/json",
                                "--data-raw",
                                '{"flags": ["' + flag[x] + '"]}',
                            ],
                            stdout=PIPE,
                            stderr=PIPE,
                        ),
                    ]
                )
        else:
            patch.append("can’t get flag for " + str(i) + " " + names[i])

    while running_procs:
        try:
            for j in range(len(running_procs)):
                proc = running_procs[j][3]
                retcode = proc.poll()
                if retcode is not None:
                    dat = running_procs.pop(j)
                    break
                else:
                    time.sleep(0.1)
                    continue

            if retcode is None:
                continue
            if retcode != 0:
                print("ERROR", dat[0], dat[1], dat[2], proc.stderr.read().decode())
            else:
                print(names.index(dat[0]) + 1, dat[0], proc.stdout.read().decode())
            print("----------------")
        except Exception as e:
            print("EXCEPTION", e)
            continue
    for i in patch:
        print(i)
    else:
        print("Routine done")
    print("waiting...")
    time.sleep(interval)

```

## Resources

{% embed url="https://github.com/DestructiveVoice/DestructiveFarm" %}

{% embed url="https://github.com/ICC-UH/icc-farmer" %}
