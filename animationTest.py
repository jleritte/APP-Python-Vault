# UI layer
from crypto import *
from file_handle import *
import curses
import traceback


quitText = 'Press "ESC" to close this screen'
welcomeText = 'Welcome Please Create a Record'
menuText = ['New Record','Edit Record','Delete Record']
# prompts =
selected = (0,1)
size = None
col = None
step = 0

def init():
  global size
  global col
  stdscr = curses.initscr()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)
  size = stdscr.getmaxyx()
  col = size[1] / 4
  paintBorder(stdscr)
  return stdscr

def paintBorder(scr):
  scr.border(0)
  scr.addstr(size[0]-1, size[1]/2 - len(quitText)/2, quitText)

def printPrompt(scr, pos, step, prompts = ['Who are you? ','Enter passphrase: ']):
  prompt = prompts[step]
  scr.addstr(pos[0],pos[1],prompt,curses.A_BOLD)
  return (pos[0],pos[1]+len(prompt))

def fillRecord(old = ('',)):
  controlstr =  "Enter: Confirm - Esc: Cancel"
  curses.curs_set(1)
  pop = curses.newwin(5,40,size[0]/2-3,size[1]/2-20)
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

def textEntry(scr, pos, text = '', mask = None):
  strng = [char for char in text]
  while 1:
    if mask:
      text = ''.join([mask]*len(strng))
    else:
      text = ''.join(strng)
    scr.addstr(pos[0] ,pos[1], text)
    ch = scr.getch()
    # scr.addstr(1,scr.getmaxyx()[1]-1-len(str(ch)),str(ch),curses.A_STANDOUT)
    if ch == 10:
      break
    elif ch == 27:
      strng = []
      break
    elif ch == 263 or ch == 127:
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
  if len(data) == 1:
    scr.addstr(pos[0],pos[1],welcomeText,curses.A_BOLD)
  else:
    for i,item in enumerate(data):
      if 'plain' in item.keys():
        y = (pos[0] + i) % (size[0] - 1)
        x = ((pos[0] + i) / (size[0] - 1)) * col + 1
        if x > 1:
          y = y + 2
        if i == selected[1]:
          attr = curses.A_REVERSE
        else:
          attr = 0
        scr.addnstr(y,x,str(item['plain'][0]),col,attr)
    curses.curs_set(0)

# TODO def quit method

def main():
  global selected
  # UI Variables
  exit = 1
  pos = (1,1)
  data = []

  try:
    stdscr = init()
    while exit:
      if not len(data):
        username = textEntry(stdscr,printPrompt(stdscr,pos, 0),'jokersadface')
        if username == None:
          break
        data = parse_file(username + '.hex')
        salt = data[0]['salt'] if len(data) else None
        passphrase = textEntry(stdscr,printPrompt(stdscr,(pos[0]+1,pos[1]), 1),'test','*')
        if passphrase == None:
          break
        key_slice = len(passphrase) % 32
        generated_salt, derived_key = derive_key(passphrase,salt)
        if len(data):
          del data[0]['salt']
          data[0]['key'] = decrypt(derived_key[key_slice:key_slice+32],passphrase,data[0]['key'])
          data = data[:1] + unlock_data(data[0]['key'],passphrase,data[1:])
        else:
          key = os.urandom(int(256/8))
          wrapped_key = encrypt(derived_key[key_slice:key_slice+32],key,passphrase)
          store_entry(username,{"cipher":ba.b2a_hex(generated_salt+wrapped_key),'entry':''})
          data = [{'key':key,'salt':generated_salt,'entry':ba.b2a_hex(generated_salt+wrapped_key)}]

      stdscr.clear()
      paintBorder(stdscr)
      printMenu(stdscr,pos)
      printData(stdscr,pos,data)
      ch = stdscr.getch()

      if ch == 10:
        if selected[0] == 0:
          new = fillRecord()
          if new:
            data.append({'plain': new})
        elif selected[0] == 1:
          new = fillRecord(data[selected[1]]['plain'])
          if new:
            data[selected[1]]['plain'] = new

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
      # stdscr.getch()

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