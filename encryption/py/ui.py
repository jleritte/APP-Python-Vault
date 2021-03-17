# UI class to handle curses
import curses
from crypto import unlock_data, lock_data

char = "none"
pw = None
defaultPrompts = ['Who are you? ', 'Enter passphrase: ']


class ui:
    stdscr = None
    __addToQuit = '↑↓: Select Record-←→: Select Action-'
    __quitText = 'Enter: Confirm-Esc: Exit'
    __controlstr = 'Enter: Confirm-Esc: Cancel'
    __welcomeText = 'Welcome Please Create a Record'
    __menuText = ['New Record', 'Edit Record', 'Delete Record']
    __selected = (0, 0)

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.size = self.stdscr.getmaxyx()
        self.col = int(self.size[1] / 5)
        self.__paintBorder(self.stdscr)

    def update(self, message):
        global pw
        pos = (1, 1)
        action, data, ch, pword = message
        if pw is None:
            pw = pword

        username = 'jokersadface'

        if action == 'name':
            return self.__textEntry(self.stdscr,
                                    self.__printPrompt(self.stdscr, pos, 0),
                                    username)
        elif action == 'pass':
            return self.__textEntry(self.stdscr,
                                    self.__printPrompt(self.stdscr,
                                                       (pos[0]+1, pos[1]), 1),
                                    'test', '*')
        elif action == 'print':
            if ch is None:
                self.__quitText = ''.join([self.__addToQuit, self.__quitText])
                self.__printScreen(data, pos)
            else:
                data = self.__checkChar(ch, data)
                if data:
                    self.__printScreen(data, pos)
                else:
                    return
            return data

    def tearDown(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def __paintBorder(self, scr):
        scr.border(0)
        scr.addstr(self.size[0]-1, int(self.size[1]/2 -
                   len(self.__quitText)/2), self.__quitText)

    def __printPrompt(self, scr, pos, step, prompts=defaultPrompts):
        scr.addstr(pos[0], pos[1], prompts[step], curses.A_BOLD)
        return (pos[0], pos[1]+len(prompts[step]))

    def __fillRecord(self, old):
        old = old['plain'] if old else ('',)
        curses.curs_set(1)
        pop = curses.newwin(5, 40, int(
            self.size[0]/2-3), int(self.size[1]/2-20))
        pop.border(0)
        prompts = ['Record Name: ', 'Password: ', 'Username: ']

        if len(old) == 1:
            title = "New Record"
            old = ('', ('', ''))
        else:
            title = "Edit %s" % old[0]
            old = unlock_data(old, pw)

        popsize = pop.getmaxyx()
        pop.addstr(0, int(popsize[1]/2 - len(title)/2), title)
        pop.addstr(popsize[0]-1, int(popsize[1]/2 -
                   len(self.__controlstr)/2), self.__controlstr)

        name = self.__textEntry(pop, self.__printPrompt(
            pop, (1, 1), 0, prompts), old[0])
        if not name:
            return
        pword = self.__textEntry(pop, self.__printPrompt(
            pop, (2, 1), 1, prompts), old[1][0], "*")
        if not pword:
            return
        uname = self.__textEntry(pop, self.__printPrompt(
            pop, (3, 1), 2, prompts), old[1][1])
        if not uname:
            return

        return lock_data((name, (pword, uname)), pw)

    def __deleteRecord(self, record):
        curses.curs_set(1)
        pop = curses.newwin(5, 40, int(
            self.size[0]/2-3), int(self.size[1]/2-20))
        pop.border(0)
        title = f"Delete {record['plain'][0]}"
        prompt = "Are you sure?"
        popsize = pop.getmaxyx()
        pop.addstr(0, int(popsize[1]/2 - len(title)/2), title)
        pop.addstr(popsize[0]-1, int(popsize[1]/2 -
                   len(self.__controlstr)/2), self.__controlstr)
        pop.addstr(int(popsize[0]/2),
                   int(popsize[1]/2 - len(prompt)/2), prompt)

        ch = pop.getch()
        if ch == 10:
            return True

    def __textEntry(self, scr, pos, text='', mask=None):
        strng = [char for char in text]
        while 1:
            if mask:
                text = ''.join([mask]*len(strng))
            else:
                text = ''.join(strng)
            scr.addstr(pos[0], pos[1], text)
            ch = scr.getch()
            if ch == 10:
                break
            elif ch == 27:
                strng = []
                break
            elif ch == 263 or ch == 127 or ch == 8:
                if len(strng):
                    strng.pop()
                    scr.addstr(pos[0], pos[1]+len(strng), ' ')
                else:
                    curses.flash()
            elif ch < 256:
                strng.append(chr(ch))
        return ''.join(strng) if len(strng) else None

    def __printMenu(self, scr, pos):
        x = pos[1]
        for i, item in enumerate(self.__menuText):
            if i == self.__selected[0]:
                attr = curses.A_BOLD | curses.A_REVERSE
            else:
                attr = curses.A_BOLD
            scr.addstr(pos[0], x, item, attr)
            x = x + 2 + len(item)

    def __printData(self, scr, pos, data):
        if len(data) == 0:
            scr.addstr(2, pos[1], self.__welcomeText, curses.A_BOLD)
        else:
            for i, item in enumerate(data):
                if 'plain' in item.keys():
                    y = (i % (self.size[0] - 3)) + 2
                    x = int(i / (self.size[0] - 3)) * self.col + 1
                    # scr.addstr(y,self.size[1]-self.col,str((y,x,self.col,i,self.size[0])))
                    # scr.addstr(1,self.size[1]-len(char)-1,char)
                    if i == self.__selected[1]:
                        attr = curses.A_REVERSE
                    else:
                        attr = 0
                    scr.addnstr(y, x, item['plain'][0], self.col, attr)
        curses.curs_set(0)

    def __checkChar(self, ch, data):
        global char
        char = str(ch)
        action, record = self.__selected
        x, y = self.__size
        lgth = len(data)
        if ch == 27:  # Esc
            return 0
        if ch == 10:  # Enter
            if action == 0 or action == 1:
                record = data[record] if action else None
                new = self.__fillRecord(record)
                if new:
                    if record:
                        record['plain'] = new
                    else:
                        data.append({'plain': new, 'entry': ''})
            else:
                if self.__deleteRecord(data[record]):
                    del data[record]

        if ch == 258:  # DOWN
            select = record + 1 if record + 1 < lgth else lgth - 1
            self.__selected = (action, select)
        if ch == 259:  # UP
            select = record - 1 if record - 1 > -1 else 0
            self.__selected = (action, select)
        if ch == 260:  # LEFT
            select = action - 1 if action - 1 > 0 else 0
            self.__selected = (select, record)
        if ch == 261:  # RIGHT
            select = action + 1 if action + 1 < 2 else 2
            self.__selected = (select, record)
        if ch == 338:  # PGDWN
            select = record + (x - 3) if record + (x - 3) < lgth else lgth - 1
            self.__selected = (action, select)
        if ch == 339:  # PGUP
            select = record - (x - 3) if record - (x - 3) > -1 else 0
            self.__selected = (action, select)
        return data

    def __printScreen(self, data, pos):
        self.stdscr.clear()
        self.__paintBorder(self.stdscr)
        self.__printMenu(self.stdscr, pos)
        self.__printData(self.stdscr, pos, data)
