
import time
import curses

i = 0
def test(scr):
	global i
	while i < 1000:
		time.sleep(1)
		scr.addstr(time.time(),curses.A_BOLD)
		i += 1
		scr.refesh()
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()

# test()


scr = curses.initscr()
curses.noecho()
curses.cbreak()
scr.keypad(1)

test(scr)