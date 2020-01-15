# file read/write functions
import binascii as ba
from pathlib import Path

def write_to(file,text):
    file.seek(0,0)
    file.write('\n'.join(text))
    file.truncate()

def store_entry(name,record):
  with open(Path(name),'r+') as f:
    text = [line.strip() for line in f.readlines()]
    try:
      i = text.index(record['entry'])
      text[i] = ba.b2a_hex(record['cipher']).decode()
    except ValueError:
      text.append(ba.b2a_hex(record["cipher"]).decode())
    write_to(f,text)

def delete_entry(name,record):
  with open(Path(name),'r+') as f:
    text = [line.strip() for line in f.readlines()]
    i = text.index(record['entry'])
    del text[i]
    write_to(f,text)

def parse_file(name):
  content = []
  with open(Path(name),'a+') as f:
    f.seek(0,0)
    content = [{'entry':line.strip(),'cipher':ba.a2b_hex(line.strip())} for line in f.readlines()]
    if len(content):
      content[0] = {'entry':content[0]['entry'],
                    'salt':content[0]['cipher'][:16],
                    'key':content[0]['cipher'][16:]}
  return content

def write_log(name,log):
  with open(Path(name),'a+') as f:
    write_to(f,[log,""])