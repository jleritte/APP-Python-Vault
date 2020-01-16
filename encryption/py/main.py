# Main Loop
from crypto import *
from file_handle import *
from ui import ui
from datetime import datetime, date
import traceback
import sys
import asyncio
import websockets
import json

data = []
key = None
password = None
file = None

def uiLogin(scr):
  global password
  username = scr.update(("name",None,None))
  if not username:
    return True
  password = scr.update(("pass",None,None))
  if not password:
    return True

  return login(username)

def login(username):
  global data, key, file, password
  password = password.encode()
  file = f'../data/{username}.hex'

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

def log(mssg,out=False,error=False):
  caret = ">>" if out else "<<"
  caret = "!!" if error else caret
  message = f"{caret} {mssg} [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]"
  write_log(f'../logs/{date.today().isoformat()}_logs.txt',message)
  print(message)

def updateFile():
  for record in data:
    store_entry(file,lock_record(key,password,record))
    unlock_record(key,password,record)


# TODO define Message Handler for Websocket
async def message_handle(websocket,path):
  log(f"{websocket.remote_address[0]} Connected",1)
  try:
    async for message in websocket:
      action, data = json.loads(message).values()
      log(f'{websocket.remote_address[0]} said {action}')
      if action == 'login':
        pass
      if action == 'update':
        pass
      # await websocket.send(f"Echo {message}")
      # log(f'{websocket.remote_address[0]} Echoed',1)
  except websockets.exceptions.ConnectionClosedError:
    log(f"Error {websocket.remote_address[0]} {sys.exc_info()[1]}",1,1)
  finally:
    log(f"{websocket.remote_address[0]} Closed Connection",1)

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
        updateFile()
        ch = scr.stdscr.getch()
    except:
      scr.tearDown()
      traceback.print_exc()
    finally:
      scr.tearDown()
  elif sys.argv[1] == '-s':
    print('Server Started')
    # start_server = websockets.serve(message_handle, "localhost", 9002)
    start_server = websockets.serve(message_handle, "192.168.51.48", 9002)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
  else:
    print(f'{sys.argv[1]} not supported')

main()