# UI layer
from crypto import *
from file_handle import *
import curses
import traceback


quitText = 'Press "ESC" to close this screen'
welcomeText = 'Welcome Please Create a Record'
menuText = ['New Record','Edit Record','Delete Record']
prompts = ['Who are you? ','Enter passphrase: ']
selected = (0,1)
size = None
step = 0

def init():
  global size
  stdscr = curses.initscr()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)
  size = stdscr.getmaxyx()
  paintBorder(stdscr)
  return stdscr

def paintBorder(scr):
  scr.border(0)
  scr.addstr(size[0]-1, size[1]/2 - len(quitText)/2, quitText)


def printPrompt(scr, pos):
  global step
  prompt = prompts[step]
  scr.addstr(pos[0],pos[1],prompt,curses.A_BOLD)
  step += 1
  return (pos[0],pos[1]+len(prompt))

def textEntry(scr, pos, mask=None):
  strng = []
  while 1:
    ch = scr.getch()
    if ch == 10:
      break
    elif ch == 27:
      strng = []
      break
    elif ch == 263:
      if len(strng):
        strng.pop()
        scr.addstr(pos[0] ,pos[1]+len(strng) ,' ')
      else:
        curses.flash()
    elif ch < 256:
      strng.append(chr(ch))
    if mask:
      scr.addstr(pos[0] ,pos[1], ''.join([mask]*len(strng)))
    else:
      scr.addstr(pos[0] ,pos[1], ''.join(strng))
  return ''.join(strng) if len(strng) else None

def printData(scr, pos, data):
  if len(data) == 1:
    scr.addstr(pos[0],pos[1],welcomeText,curses.A_BOLD)
  else:
    for i,item in enumerate(data):
      if 'plain' in item.keys():
        if i == selected[1]:
          scr.addstr(pos[0]+i,pos[1],item['plain'],curses.A_STANDOUT)
        else:
          scr.addstr(pos[0]+i,pos[1],item['plain'])
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
        username = textEntry(stdscr,printPrompt(stdscr,pos))
        if username == None:
          break
        data = parse_file(username + '.hex')
        salt = data[0]['salt'] if len(data) else None
        passphrase = textEntry(stdscr,printPrompt(stdscr,(pos[0]+1,pos[1])),'*')
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
      stdscr.addstr(1,1,"  ".join( menuText) , curses.A_BOLD)
      printData(stdscr,pos,data)
      ch = stdscr.getch()

      stdscr.addstr(1,size[1]-1-len(str(ch)),str(ch),curses.A_STANDOUT)


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
    #   elif ch == 260: #LEFT
    #     x -= 1
    #     stdscr.move(y,x)
    #   elif ch == 261: #RIGHT
    #     x += 1
    #     stdscr.move(y,x)
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