# https://diceware.dmuth.org/

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
tran_AAD = 'transmission'.encode()

def uiLogin(scr):
  global connections, l
  connection = {}
  username = scr.update(("name",None,None,None))
  if not username:
    return False
  connection['filename'] = f'../data/{username}.hex'
  password = scr.update(("pass",None,None,None))
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
  connections[cid]['dkey'] = key
  connections[cid]['data'] = data
  return True

def log(mssg,out=False,error=False):
  caret = ">>" if out else "<<"
  caret = "!!" if error else caret
  message = f"{caret} {mssg} [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]"
  # write_log(f'../logs/{date.today().isoformat()}_logs.txt',message)
  print(message)

def updateFile(cid):
  global connections
  user = connections[cid]
  password = user['password']
  key = user['dkey']
  for record in user['data']:
    if len(record['entry']) > 0:
      delete_entry(user['filename'],lock_record(key,password,record))
      unlock_record(key,password,record)
  for record in user['dif']:
    store_entry(user['filename'],lock_record(key,password,record))
    record['entry'] = ba.b2a_hex(record['cipher']).decode()
    unlock_record(key,password,record)
  user['data'] = user['dif']

def wrapResponse(cid,action,success,data=None):
  global connections
  key = connections.get(cid,{'key':None})['key']
  response = {"action":action,"success":success}
  if data:
    response['data'] = data
  return lockMessage(json.dumps(response),key)

def unwrapMessage(cid,message):
  global connections
  user = connections.get(cid,{})
  key = user.get('key',None)
  if not key:
    out = json.loads(message).values()
  else:
    out = json.loads(unlockMessage(message,key)).values()
  return out

def unlockMessage(message,key):
  global ecKeys
  tranKey = get_shared_key(ecKeys,key)
  message = decrypt(tranKey,ba.a2b_hex(message),tran_AAD)
  return message

def lockMessage(message,key):
  global ecKeys
  tranKey = get_shared_key(ecKeys,key)
  message = ba.b2a_hex(encrypt(tranKey,message.encode(),tran_AAD)).decode()
  return message

# TODO define Message Handler for Websocket
async def message_handle(websocket,path):
  global connections
  cid = f"{websocket.remote_address[1]}"
  connection = connections.get(cid,{})
  log(f"{websocket.remote_address[0]} Connected with id {cid}",1)
  connections[cid] = connection
  await websocket.send(json.dumps({"key": export_public_key(ecKeys.public_key())}))
  try:
    async for message in websocket:
      action, data = unwrapMessage(cid,message)
      response = None
      success = False
      log(f'{websocket.remote_address[0]},{cid} said {action}')
      if action == 'key':
        connection['key'] = import_public_key(data)
      if action == 'login':
        connection['password'] = data['password'].encode()
        connection['filename'] = f'../data/{data["username"]}.hex'
        success = login(cid)
        response = wrapResponse(cid,action, success, read_raw(connection['filename'])[0] if success else None)
      if action == 'sync':
        success = len(connection) > 0
        response = wrapResponse(cid,action, success, read_raw(connection['filename'])[1:] if success else None)
      if action == 'update':
        for entry in data:
          entry['plain'] = tuple(entry['plain'])
        success = len(connection) > 0
        if(success):
          connections[cid]['dif'] = data
          updateFile(cid)
        response = wrapResponse(cid,action,success,None)

      if response:
        await websocket.send(response)
        log(f'{websocket.remote_address[0]},{cid} {action} {success}',1)
  except websockets.exceptions.ConnectionClosedError:
    log(f"Error {websocket.remote_address[0]},{cid} {sys.exc_info()[1]}",error=1)
  finally:
    log(f"{websocket.remote_address[0]},{cid} Closed Connection",1)
    connections.pop(cid,None)

def start_ui():
    global connections
    try:
      ch = None
      scr = ui()
      while not uiLogin(scr):
        pass
      while True:
        data = connections[uiUser]['data']
        exit = scr.update(('print', data, ch,connections[uiUser]['password']))
        if exit == None:
          break
        connections[uiUser]['dif'] = exit
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