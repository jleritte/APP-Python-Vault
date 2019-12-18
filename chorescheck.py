# Chores Checklist
import json
from datetime import datetime, date, timedelta
from ast import literal_eval
from itertools import groupby
from functools import reduce
from socket import *

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

def score_task(section,index):
  section, scores = score[section]
  scores[index] = scores[index] + 1
  return (section,scores)

def get_tasks(chores,section):
  return [task for task in chores if task[0] == score[section][0]]

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

def sort_on(x):
  return x[0]

def main():
  sock = socket(AF_INET,SOCK_STREAM)
  sock.bind(('localhost',9001))
  sock.listen(5)
  print('listening on: ','localhost',9001)
  while True:
    connect, addrss = sock.accept()
    try:
        print('connected: ',addrss)
        while True:
          data = connect.recv(200)
          if data:
            print(data)
            connect.sendall(data)
          else:
            break
    finally:
      print('connection closed')
      connect.close()
  # init_connection()
  # chores = clear_tasks(read_file())
  # clear_score(chores)
  # print('***********************************')
  # print_scores(total_score())
  # print('***********************************')
  # print_sections(chores)
  # if len(ch):
  #   section, index = literal_eval(ch)
  #   score[section] = score_task(section, index)
  #   task = get_tasks(chores,section)[index]
  #   chores[chores.index(task)] = stamp_task(task)
  # write_file(score)
  # write_file(chores,'chores.json')



main()