# Network Forensic

## Recon

With Wireshark:

```
Check for objects, filters, etc.

Check for http requests
```

With tshark:

```bash
tshark -r log.pcap -qz io,phs # see protocol hierarchy statistics

tshark -r log.pcap -Y tcp | head # see head of tcp, depends on phs
```

## Tools

* pyshark - python
* tshark
* wireshark
* scapy

## Online Tools

* [https://apackets.com/](https://apackets.com/) - Analyze PCAP

