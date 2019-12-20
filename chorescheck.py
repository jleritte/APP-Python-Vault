# Chores Checklist
import sys
import json
import asyncio
import websockets
from datetime import datetime, date, timedelta
from ast import literal_eval
from itertools import groupby
from functools import reduce

score = ''
today = ''
days = ''
cleared = None
labels = {'1':'Daily','7':'Weekly','30':'Monthly','90':'Three Months','180':'Six Months','360':'Annually'}

def read_file(name = 'chores.json'):
  with open(name) as f:
    data = [literal_eval(value) for value in json.load(f)]
    data.sort(key=sort_on)
    return data

def write_file(data,name = 'score.json'):
  with open(name,'w') as f:
    json.dump([str(value) for value in data],f,indent=2)

def print_sections(chores):
  for section, tasks in groupby(chores,key=sort_on):
    print(labels[str(section)])
    print('******')
    for i,task,complete in tasks:
      if not len(complete):
        print(task)
    print('')

def print_scores(scores):
  for key,value in scores.items():
    print(key)
    print('----')
    print(value)
    print('')

def score_task(index):
  section, value = score[index]
  return (section,value + 1)

def stamp_task(task):
  section, task, datestr = task
  return (section, task, today.isoformat())

def clear_task(task):
  section, task, datestr = task
  return (section, task,'')

def clear_tasks(tasks):
  return [clear_task(task) if check(task) else task for task in tasks]

def check(task):
  sect, name, date_from = task
  dif = timedelta(days=0)
  if sect == 7:
    dif = timedelta(days=today.weekday())
  elif sect == 30:
    dif = timedelta(days=today.day - 1)
  elif sect == 90:
    dif = today - date(today.year,today.month-((today.month+2) % 3),1)
  elif sect == 180:
    dif = today - date(today.year,today.month-((today.month+5) % 6),1)
  elif sect == 360:
    dif = today - date(today.year,1,1)
  return len(date_from) and datetime.strptime(task[2],'%Y-%m-%d').date() < today - dif

def clear_score(chores):
  global cleared
  global score
  if today == date(today.year,1,1) and not cleared:
    score = [(section,0) for section,x,y in chores]
    cleared = True
  elif today != date(today.year,1,1):
    cleared = None

def total_score():
  percents = {'Total':0}
  for section, tasks in groupby(score,key=sort_on):
    label = labels[str(section)]
    percents[label] = [float(task/int(days/section)) for i,task in tasks]
    percents[label+' total'] = reduce(lambda a,b: a+b,percents[label]) / len(percents[label])
    percents['Total'] = percents['Total'] + percents[label+' total']
  percents['Total'] = percents['Total'] / len(score)
  return percents

def init_connection():
  global score
  global today
  global days
  today = date.today()
  days = (date(today.year,12,31) - date(today.year,1,1)).days + 1
  score = read_file('score.json')
  chores = clear_tasks(read_file())
  clear_score(chores)

  return chores

def sort_on(x):
  return x[0]

def sort_on_zip(x):
  return x[0][0]

def save_data(chores):
  write_file(score)
  write_file(chores,'chores.json')

def wrap_message(chores):
  return json.dumps({"chores":chores,"score":score})

def log(mssg,out=False):
  caret = ">>" if out else "<"
  message = f"{caret} {mssg} @{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')}"
  print(message)

async def message_handle(websocket, path):
  global score
  chores = init_connection()
  try:
    async for message in websocket:
      action,task = json.loads(message).values()
      log(f"{action} {task}")

      if action == 'check':
        chores[task] = stamp_task(chores[task])
        log(f"Chore {chores[task][1]} Checked Off",True)
        score[task] = score_task(task)
        save_data(chores=chores)
        log(f"Updated Files",True)

      response = wrap_message(chores)
      await websocket.send(response)
      log(f"Updated Client",True)

  except websockets.exceptions.ConnectionClosedError:
    log(f"!Error {sys.exc_info()[1]}",True)
  finally:
    log(f"Closed",True)

def main():
  start_server = websockets.serve(message_handle, "localhost", 9001)

  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()

main()