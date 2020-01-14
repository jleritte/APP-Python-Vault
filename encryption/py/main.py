# Main Loop
from crypto import *
from file_handle import *
from ui import ui
import sys
import asyncio
import websockets

data = []
key = None
password = None
file = None

def uiLogin(scr):
  global data, key, file, password
  username = scr.update(("name",None,None))
  if not username:
    return True
  password = scr.update(("pass",None,None))
  if not password:
    return True
  password = password.encode()
  file = f'..\\data\\{username}.hex'

  data = parse_file(file)
  salt, passKey = derive_key(password,data[0]['salt'] if len(data) else None)

  if len(data):
    key = decrypt(passKey,data[0]['key'],password)
    if not key:
      return False
    data = [unlock_record(key,password,item) for item in data[1:]]
  else:
    key = os.urandom(int(256/8))
    store_entry(file,{"cipher":salt+encrypt(passKey,key,password),"entry":''})

  return True

# TODO define Message Handler for Websocket
def message_handle():
  pass

def main():

  if len(sys.argv) == 1:
    global data
    try:
      ch = None
      scr = ui()
      while not uiLogin(scr):
        pass
      while data:
        exit = scr.update(('print', data, ch))
        if not exit:
          break
        data = exit
        ch = scr.stdscr.getch()
    except:
      scr.tearDown()
    finally:
      scr.tearDown()
  elif sys.argv[1] == '-s':
    print(sys.argv)
  else:
    print(f'{sys.argv[1]} not supported')

main()