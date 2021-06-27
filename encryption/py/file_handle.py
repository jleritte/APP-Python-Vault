# file read/write functions
from binascii import a2b_hex as fromHex, b2a_hex as toHex
from pathlib import Path as p


def write_to(file, text):
  file.seek(0, 0)
  file.write('\n'.join(text))
  file.truncate()


def store_entry(name, record):
  with open(p(name), 'r+') as f:
    text = [line.strip() for line in f.readlines()]
    try:
      i = text.index(record['entry'])
      text[i] = toHex(record['cipher']).decode()
    except ValueError:
      text.append(toHex(record["cipher"]).decode())
    write_to(f, text)


def delete_entry(name, record):
  with open(p(name), 'r+') as f:
    text = [line.strip() for line in f.readlines()]
    i = text.index(record['entry'])
    del text[i]
    write_to(f, text)


def read_raw(name):
  content = []
  with open(p(name), 'r+') as f:
    f.seek(0, 0)
    content = [line.strip() for line in f.readlines()]
  return content


def parse_file(name):
  content = []
  with open(p(name), 'a+') as f:
    f.seek(0, 0)
    content = [create_entry(line) for line in f.readlines()]
    if len(content):
      content[0] = {'entry': content[0]['entry'],
              'salt': content[0]['cipher'][:16],
              'key': content[0]['cipher'][16:]}
  return content


def create_entry(line):
  return {'entry': line.strip(), 'cipher': fromHex(line.strip())}


def write_log(name, log):
  with open(p(name), 'a+') as f:
    write_to(f, [log, ""])
