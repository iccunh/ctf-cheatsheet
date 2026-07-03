# Dump

## Parse Evtx

```python
from Evtx.Evtx import Evtx

def parse_evtx_file(file_path):
    """
    Parse a Windows EVTX file and return a list of XML strings,
    one for each record in the log.
    
    Parameters:
      file_path (str): The path to the EVTX file.
    
    Returns:
      list of str: A list containing the XML representation of each record.
    """
    xml_records = []
    try:
        with Evtx(file_path) as log:
            for record in log.records():
                xml_records.append(record.xml())
    except FileNotFoundError:
        print("Error: File not found. Please check the file path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return xml_records

if __name__ == "__main__":
    file_path = input("Enter the path to the EVTX file: ").strip()
    records = parse_evtx_file(file_path)
    for rec in records:
        print(rec)
```

<br>
