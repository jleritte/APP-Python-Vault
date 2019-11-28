# UI layer
from crypto import *
from file_handle import *
import curses
import traceback

# UI Variables
quitText = 'Type exit to close this screen'
exit = 1
props = ['Who are you? ','Enter passphrase: ']
prop = 0
y = 1
x = 1
curs = 0


# Data Variables
username = ''
data = ''
salt = None
passphrase = ''
key_slice = ''
generated_salt = ''
derived_key = ''

try:
  # -- Initialize --
  stdscr = curses.initscr()   # initialize curses screen
  curses.noecho()             # turn off auto echoing of keypress on to screen
  curses.cbreak()             # enter break mode where pressing Enter key
                              #  after keystroke is not required for it to register
  stdscr.keypad(1)            # enable special Key values such as curses.KEY_LEFT etc
  curses.curs_set(curs)

  size = stdscr.getmaxyx()

  # -- Perform an action with Screen --
  stdscr.border(0)
  stdscr.addstr(size[0]-1, size[1]/2 - len(quitText)/2, quitText, curses.A_NORMAL)
  stdscr.addstr(y, x, props[prop], curses.A_BOLD)

  strng = []
  while exit:
    ch = stdscr.getch()
    stdscr.addstr(1,size[1]-1-len(str(ch)),str(ch),curses.A_STANDOUT)
    if ch == 10:
      if ''.join(strng) == 'exit':
        exit = 0
      else:
        if prop == 0:
          username = ''.join(strng) + '.hex'
          data = parse_file(username)
          salt = data[0]['salt'] if len(data) else None
        elif prop == 1:
          passphrase = ''.join(strng)
          key_slice = len(passphrase) % 32
          generated_salt, derived_key = derive_key(passphrase,salt)
          if len(data):
            del data[0]['salt']
            data[0]['key'] = decrypt(derived_key[key_slice:key_slice+32],passphrase,data[0]['key'])
            data = data[:1] + unlock_data(data[0]['key'],passphrase,data[1:])
        strng = []
        y += 1
        prop += 1
        if prop < len(props):
          stdscr.addstr(y,1,props[prop],curses.A_BOLD)
          x = len(props[prop])+1
          continue
    elif ch == 263:
      stdscr.addstr(y ,x ,''.join([' ']*len(strng)))
      if len(strng):
        strng.pop()
      else:
        curses.flash()
    elif ch == 9:
      curs = curs + 1 % 3
      stdscr.addstr(str(curs))
      curses.curs_set(curs)
    elif ch == 258:
      y += 1
      stdscr.move(y,x)
    elif ch == 259:
      y -= 1
      stdscr.move(y,x)
    elif ch == 260:
      x -= 1
      stdscr.move(y,x)
    elif ch == 261:
      x += 1
      stdscr.move(y,x)
    elif ch < 256:
      strng.append(chr(ch))
    if prop == 1:
      stdscr.addstr(y, x, ''.join(['*']*len(strng)))
    elif len(data):
      for i,l in enumerate(data):
        if 'plain' in l.keys():
          stdscr.addstr(y+i,1,l['plain'])
          stdscr.move(1,1)
    else:
      stdscr.addstr(y, x, ''.join(strng))

  # -- End of user code --

except:
  stdscr.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.endwin()
  traceback.print_exc()     # print trace back log of the error

finally:
  # --- Cleanup on exit ---
  stdscr.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.endwin()