# UI layer
# encoding=UTF-8
from crypto import *
from file_handle import *
import curses
import traceback

addToQuit ='↑↓: Select Record-←→: Select Action-'
quitText = 'Enter: Confirm-Esc: Exit'
controlstr =  'Enter: Confirm-Esc: Cancel'
welcomeText = 'Welcome Please Create a Record'
menuText = ['New Record','Edit Record','Delete Record']
selected = (0,1)
# size = None
# col = None

def init():
  global size
  global col
  stdscr = curses.initscr()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)
  size = stdscr.getmaxyx()
  col = int(size[1] / 5)
  paintBorder(stdscr)
  return stdscr

def paintBorder(scr):
  scr.border(0)
  scr.addstr(size[0]-1, int(size[1]/2 - len(quitText)/2), quitText)

def printPrompt(scr, pos, step, prompts = ['Who are you? ','Enter passphrase: ']):
  scr.addstr(pos[0],pos[1],prompts[step],curses.A_BOLD)
  return (pos[0],pos[1]+len(prompts[step]))

def fillRecord(old):
  old = old['plain'] if old else ('',)
  curses.curs_set(1)
  pop = curses.newwin(5,40,int(size[0]/2-3),int(size[1]/2-20))
  pop.border(0)
  prompts = ['Record Name: ','Password: ','Username: ']

  if len(old) == 1:
    title = "New Record"
    old = ('','','')
  else:
    title = "Edit %s" % old[0]

  popsize = pop.getmaxyx()
  pop.addstr(0, int(popsize[1]/2 - len(title)/2), title)
  pop.addstr(popsize[0]-1, int(popsize[1]/2 - len(controlstr)/2),controlstr)

  name = textEntry(pop,printPrompt(pop,(1,1),0,prompts),old[0])
  if not name:
    return
  pword = textEntry(pop,printPrompt(pop,(2,1),1,prompts),old[1],"*")
  if not pword:
    return
  uname = textEntry(pop,printPrompt(pop,(3,1),2,prompts),old[2])
  if not uname:
    return

  return (name, pword, uname)

def deleteRecord(username,record):
  curses.curs_set(1)
  pop = curses.newwin(5,40,int(size[0]/2-3),int(size[1]/2-20))
  pop.border(0)
  title = "Delete %s" % record['plain'][0]
  prompt = "Are you sure?"
  popsize = pop.getmaxyx()
  pop.addstr(0, int(popsize[1]/2 - len(title)/2), title)
  pop.addstr(popsize[0]-1, int(popsize[1]/2 - len(controlstr)/2),controlstr)
  pop.addstr(int(popsize[0]/2), int(popsize[1]/2 - len(prompt)/2),prompt)

  ch = pop.getch()
  if ch == 10:
    delete_entry(username,record)
    return True

def textEntry(scr, pos, text = '', mask = None):
  strng = [char for char in text]
  while 1:
    if mask:
      text = ''.join([mask]*len(strng))
    else:
      text = ''.join(strng)
    scr.addstr(pos[0] ,pos[1], text)
    ch = scr.getch()
    if ch == 10:
      break
    elif ch == 27:
      strng = []
      break
    elif ch == 263 or ch == 127 or ch == 8:
      if len(strng):
        strng.pop()
        scr.addstr(pos[0] ,pos[1]+len(strng) ,' ')
      else:
        curses.flash()
    elif ch < 256:
      strng.append(chr(ch))
  return ''.join(strng) if len(strng) else None

def printMenu(scr, pos):
  x = pos[1]
  for i, item in enumerate(menuText):
    if i == selected[0]:
      attr = curses.A_BOLD | curses.A_REVERSE
    else:
      attr = curses.A_BOLD
    scr.addstr(pos[0],x,item,attr)
    x = x + 2 + len(item)

def printData(scr, pos, data):
  # TODO: Fix the column split
  if len(data) == 1:
    scr.addstr(2,pos[1],welcomeText,curses.A_BOLD)
  else:
    for i,item in enumerate(data[1:]):
      if 'plain' in item.keys():
        y = (i+1) % (size[0] - 2)
        x = int(i / (size[0] - 1)) * col + 1
        if x > 1:
          y = y + 2
        scr.addstr(y,size[1]-col,str((y,x,col,i,size[0])))
        if i == selected[1]:
          attr = curses.A_REVERSE
        else:
          attr = 0
        scr.addnstr(y,x,item['plain'][0],col,attr)
    curses.curs_set(0)

# TODO def quit method

def main():
  global selected
  global quitText
  # UI Variables
  exit = 1
  pos = (1,1)
  data = []
  username = 'jokersadface'

  try:
    stdscr = init()
    while exit:
      if not len(data):
        username = textEntry(stdscr,printPrompt(stdscr,pos, 0),username)
        if username == None:
          break
        username = username + '.hex'
        data = parse_file(username)
        salt = data[0]['salt'] if len(data) else None
        passphrase = textEntry(stdscr,printPrompt(stdscr,(pos[0]+1,pos[1]), 1),'test','*')
        if passphrase == None:
          break
        key_slice = len(passphrase) % 32
        passphrase = passphrase.encode()
        generated_salt, derived_key = derive_key(passphrase,salt)
        if len(data):
          del data[0]['salt']
          key = decrypt(derived_key[key_slice:key_slice+32],data[0]['key'],passphrase)
          if key:
            data[0]['key'] = key
            data = data[:1] + [unlock_record(data[0]['key'],passphrase,item) for item in data[1:]]
          else:
            data = []
            username = username[:-4]
            continue
        else:
          key = os.urandom(int(256/8))
          wrapped_key = encrypt(derived_key[key_slice:key_slice+32],key,passphrase)
          store_entry(username,{"cipher":generated_salt+wrapped_key,'entry':''})
          data = [{'key':key,'salt':generated_salt,'entry':ba.b2a_hex(generated_salt+wrapped_key)}]
        quitText = ''.join([addToQuit,quitText])

      stdscr.clear()
      paintBorder(stdscr)
      printMenu(stdscr,pos)
      printData(stdscr,pos,data)
      ch = stdscr.getch()

      if ch == 10:
        if selected[0] == 0 or selected[0] == 1:
          # Clean this up later
          record = data[selected[1]] if selected[0] else None
          new = fillRecord(record)
          if new:
            if record:
              record['plain'] = new
            else:
              data.append({'plain': new,'entry': ''})
            record = record if record else data[-1]
            record = lock_record(data[0]['key'],passphrase,record)
            store_entry(username,record)
            record['entry'] = ba.b2a_hex(record['cipher']).decode()
            record = unlock_record(data[0]['key'],passphrase,record)
            if selected[0]:
              data[selected[1]] = record
            else:
              data[-1] = record
        else:
          if deleteRecord(username,data[selected[1]]):
            del data[selected[1]]
            selected = (selected[0],1)

      if ch == 27:
        # pop = curses.newwin(3,40,size[0]/2-1,size[1]/2-20)
        # pop.border(0)
        # pop.addstr(1,1,"Are you sure you want to quit?(y or n)")
        # curses.curs_set(0)
        # ch = pop.getch()
        # if ch == ord('y'):
        exit = 0
        # else:
        #   stdscr.redrawwin()
        #   stdscr.move(pos[0],pos[1])
        #   curses.curs_set(1)
        # continue

      if ch == 258: #DOWN
        select = selected[1] + 1 if selected[1] + 1 < len(data)  else len(data) - 1
        selected = (selected[0],select)
      elif ch == 259: #UP
        select = selected[1] - 1 if selected[1] - 1 > 1  else 1
        selected = (selected[0],select)
      elif ch == 260: #LEFT
        select = selected[0] - 1 if selected[0] - 1 > 0  else 0
        selected = (select,selected[1])
      elif ch == 261: #RIGHT
        select = selected[0] + 1 if selected[0] + 1 < 2  else 2
        selected = (select,selected[1])

  except:
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    traceback.print_exc()

  finally:
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()


main()