# Main Loop
from crypto import *
from file_handle import *
from ui import ui
from datetime import datetime, date
from logger import logger
import binascii as ba
import traceback
import sys
import asyncio
import websockets
import json

ecKeys = None
connections = {}
uiUser = '0000'
l = logger()

def uiLogin(scr):
  global connections, l
  connection = {}
  username = scr.update(("name",None,None))
  if not username:
    return False
  connection['filename'] = f'../data/{username}.hex'
  password = scr.update(("pass",None,None))
  if not password:
    return False
  connection['password'] = password.encode()
  connections[uiUser] = connection
  return login(uiUser)

def login(cid):
  global connections
  password = connections[cid]['password']
  file = connections[cid]['filename']

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
  connections[cid]['key'] = key
  connections[cid]['data'] = data
  return True

def log(mssg,out=False,error=False):
  caret = ">>" if out else "<<"
  caret = "!!" if error else caret
  message = f"{caret} {mssg} [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]"
  write_log(f'../logs/{date.today().isoformat()}_logs.txt',message)
  print(message)

def updateFile(cid):
  global connections
  user = connections[cid]
  password = user['password']
  key = user['key']
  for record in user['data']:
    store_entry(user['filename'],lock_record(key,password,record))
    record['entry'] = ba.b2a_hex(record['cipher']).decode()
    unlock_record(key,password,record)

def wrapResponse(action,success,data=None):
  response = {"action":action,"success":success}
  if data:
    response['data'] = data
  return json.dumps(response)

def unwrapMessage():
  pass

# TODO define Message Handler for Websocket
async def message_handle(websocket,path):
  print(websocket.remote_address)
  global connections
  cid = f"{websocket.remote_address[1]}"
  connection = connections.get(cid,{})
  log(f"{websocket.remote_address} Connected",1)
  connections[cid] = connection
  await websocket.send(json.dumps({"key": export_public_key(ecKeys.public_key())}))
  try:
    async for message in websocket:
      action, data = json.loads(message).values()
      response = None
      success = False
      log(f'{websocket.remote_address[0]} said {action}')
      if action == 'login':
        connection['password'] = data['password'].encode()
        connection['filename'] = f'../data/{data["username"]}.hex'

        success = login(cid)
        print(connection,connections)
        response = wrapResponse(action, success, connection['data'] if success else None)
      if action == 'update':
        pass

      if response:
        await websocket.send(response)
        log(f'{websocket.remote_address[0]} {action} {success}',1)
  except websockets.exceptions.ConnectionClosedError:
    log(f"Error {websocket.remote_address[0]} {sys.exc_info()[1]}",error=1)
  finally:
    log(f"{websocket.remote_address} Closed Connection",1)
    connections.pop(cid,None)

def start_ui():
    global connections
    try:
      ch = None
      scr = ui()
      while not uiLogin(scr):
        pass
      data = connections[uiUser]['data']
      while True:
        exit = scr.update(('print', data, ch))
        if exit == None:
          break
        data = exit
        updateFile(uiUser)
        ch = scr.stdscr.getch()
    except:
      scr.tearDown()
      traceback.print_exc()
    finally:
      scr.tearDown()

def start_server():
  global ecKeys
  ecKeys = generate_key_pair()
  print('Server Keys Generated')
  server = websockets.serve(message_handle, "localhost", 9002)
  # server = websockets.serve(message_handle, "192.168.51.111", 9002)
  print('Starting Server')
  asyncio.get_event_loop().run_until_complete(server)
  asyncio.get_event_loop().run_forever()

def main():
  if len(sys.argv) == 1:
    start_ui()
  elif sys.argv[1] == '-s':
    start_server()
  else:
    print(f'{sys.argv[1]} not supported')

main()