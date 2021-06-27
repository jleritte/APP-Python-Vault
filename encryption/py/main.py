# https://diceware.dmuth.org/

# Main Loop
from crypto import decrypt, encrypt, unlock_record, lock_record
from crypto import generate_key_pair, export_public_key, import_public_key
from crypto import derive_key, get_shared_key
from file_handle import parse_file, write_log, read_raw
from file_handle import store_entry, delete_entry
from ui import ui
from datetime import datetime, date
from generate_password import generate
from os import urandom
import binascii as ba
import traceback
import sys
import asyncio
import websockets
import json

sessions = {}
uiUser = '0000'
tran_AAD = 'transmission'.encode()


def uiLogin(scr):
  user = {}
  username = scr.update(("name", None, None, None))
  if username is None:
    return False
  user['filename'] = f'../data/{username}.hex'
  password = scr.update(("pass", None, None, None))
  if password is None:
    return False
  user['password'] = password.encode()
  sessions[uiUser] = user
  return user if login(user) else False


def login(user):
  password = user['password']
  file = user['filename']

  data = parse_file(file)
  salt, passKey = derive_key(
    password, data[0]['salt'] if len(data) else None)

  if len(data):
    key = decrypt(passKey, data[0]['key'], password)
    if not key:
      return False
    data = [unlock_record(key, password, item) for item in data[1:]]
  else:
    key = urandom(int(256/8))
    entry = {"cipher": salt+encrypt(passKey, key, password), "entry": ''}
    store_entry(file, entry)
  user['dkey'] = key
  user['data'] = data
  return True


def log(mssg, out=False, error=False):
  caret = ">>" if out else "<<"
  caret = "!!" if error else caret
  time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
  message = f"{caret} {mssg} [{time}]"
  write_log(f'../logs/{date.today().isoformat()}_logs.txt', message)
  print(message)


def updateFile(user):
  password = user['password']
  key = user['dkey']
  for record in user['data']:
    if len(record['entry']) > 0:
      delete_entry(user['filename'], lock_record(key, password, record))
      unlock_record(key, password, record)
  for record in user['dif']:
    store_entry(user['filename'], lock_record(key, password, record))
    record['entry'] = ba.b2a_hex(record['cipher']).decode()
    unlock_record(key, password, record)
  user['data'] = user['dif']


def wrapResponse(user, action, success, data=None):
  pub_key = user['key']
  pri_key = user['session_keys']
  response = {"action": action, "success": success}
  if data is not None:
    response['data'] = data
  return lockMessage(json.dumps(response), (pub_key, pri_key))


def unwrapMessage(user, message):
  key = user.get('key', None)
  pri_key = user['session_keys']
  if not key:
    out = json.loads(message).values()
  else:
    out = json.loads(unlockMessage(message, (key, pri_key))).values()
  return out


def unlockMessage(message, keys):
  pub_key, pri_key = keys
  tranKey = get_shared_key(pri_key, pub_key)
  message = decrypt(tranKey, ba.a2b_hex(message), tran_AAD)
  return message


def lockMessage(message, keys):
  pub_key, pri_key = keys
  tranKey = get_shared_key(pri_key, pub_key)
  message = ba.b2a_hex(encrypt(tranKey, message.encode(), tran_AAD)).decode()
  return message


def generate_session_key(session):
  keys = generate_key_pair()
  session['session_keys'] = keys
  return keys.public_key()


async def message_handle(websocket, path):
  global sessions
  sid = f"{websocket.remote_address[1]}"
  session = sessions.get(sid, {})
  log(f"{websocket.remote_address[0]} Connected with id {sid}", 1)
  sessions[sid] = session
  JSON = {"key": export_public_key(generate_session_key(session))}
  log(f"{websocket.remote_address[0]} Session Keys Generated", 1)
  await websocket.send(json.dumps(JSON))
  try:
    async for message in websocket:
      action, data = unwrapMessage(session, message)
      response = None
      success = False
      log(f'{websocket.remote_address[0]},{sid} said {action}')
      if action == 'key':
        session['key'] = import_public_key(data)
      if action == 'login':
        session['password'] = data['password'].encode()
        session['filename'] = f'../data/{data["username"]}.hex'
        success = login(session)
        response = wrapResponse(session, action, success, read_raw(
          session['filename'])[0] if success else None)
      if action == 'sync':
        success = len(session) > 0
        response = wrapResponse(session, action, success, read_raw(
          session['filename'])[1:] if success else None)
      if action == 'update':
        for entry in data:
          entry['plain'] = tuple(entry['plain'])
        success = len(session) > 0
        if(success):
          sessions[sid]['dif'] = data
          updateFile(session)
        response = wrapResponse(session, action, success, None)
      if action == 'password':
        success = True
        response = wrapResponse(session, action, success, generate(int(data)))

      if response:
        await websocket.send(response)
        address = websocket.remote_address[0]
        log(f'{address},{sid} {action} {success}', 1)
  except websockets.exceptions.ConnectionClosedError:
    address = websocket.remote_address[0]
    log(f"Error {address},{sid} {sys.exc_info()[1]}", error=1)
  finally:
    log(f"{websocket.remote_address[0]},{sid} Closed Connection", 1)
    sessions.pop(sid, None)


def start_ui():
  try:
    ch = None
    scr = ui()
    user = None
    while not user:
      user = uiLogin(scr)
      pass
    while True:
      data = user['data']
      exit = scr.update(('print', data, ch, user['password']))
      if exit is None:
        break
      user['dif'] = exit
      updateFile(user)
      ch = scr.stdscr.getch()
  except:
    scr.tearDown()
    traceback.print_exc()
  finally:
    scr.tearDown()


def start_server():
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
