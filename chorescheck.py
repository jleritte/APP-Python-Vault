# Chores Checklist
import json
from datetime import datetime, date, timedelta
from ast import literal_eval
from functools import reduce

score = ''
today = ''
days = ''
cleared = None
labels = {'1':'Daily','7':'Weekly','30':'Monthly','90':'Three Months','180':'Six Months','360':'Annually'}

def read_file(name = 'chores.json'):
  with open(name) as f:
    return [literal_eval(str(value)) for value in json.load(f)]

def write_file(data,name = 'score.json'):
  with open(name,'w') as f:
    json.dump([str(value) for value in data],f)

def print_sections(chores):
  last = ''
  for section, task, date in chores:
    if last != section:
      last = section
      print('')
      print(labels[str(section)])
      print('******')
    if not len(date):
      print(task)

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
  print('Clear:',task)
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

def clear_score():
  global cleared
  if today == date(today.year,1,1) and not cleared:
    cleared = True
  elif today != date(today.year,1,1):
    cleared = None

def total_score():
  precents = {'Total':0}
  for section,tasks in score:
    label = labels[str(section)]
    precents[label] = [float(task/int(days/section)) for task in tasks]
    precents[label+'total'] = reduce((lambda x, y: x + y),precents[label]) / len(precents[label])
    precents['Total'] = precents['Total'] + precents[label+'total']
  precents['Total'] = precents['Total'] / len(score)
  return precents

def init_connection():
  global score
  global today
  global days
  today = date.today()
  days = (date(today.year,12,31) - date(today.year,1,1)).days + 1
  score = read_file('score.json')

def main():
  print(today,days,score)
  init_connection()
  print(today,days,score)
  chores = clear_tasks(read_file())
  clear_score()
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