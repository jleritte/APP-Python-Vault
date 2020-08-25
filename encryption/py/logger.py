out = []

class logger:
  __instance = None
  def __init__(self):
    if logger.__instance == None:
      logger.__instance = self

  def write(self,text):
    global out
    out.append(text)

  def out(self):
    global out
    print('\n'.join(out))