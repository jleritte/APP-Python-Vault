# Chores Checklist
import json
from datetime import datetime, date, timedelta
from ast import literal_eval
from functools import reduce

score = ''
today = date.today()
maxs = {"Daily": float((date(today.year,12,31)-date(today.year,1,1)).days),"Weekly":52.,"Monthly":12.,"Three Months":4.,"Six Months":2.,"Annually":1.}

def read_file(name = 'chores.json'):
  with open(name) as f:
    return {key: [literal_eval(str(value)) for value in values] for (key,values) in json.load(f).items()}

def write_file(data,name = 'score.json'):
  with open(name,'w') as f:
    json.dump({key: [str(value) for value in values] for (key,values) in data},f)

def print_section(chores):
  for section,tasks in chores.items():
    print(section)
    print('******')
    for task in tasks:
      if len(task) < 2:
        print(task[0])
    print("")

def print_scores(scores):
  for key,value in scores.items():
    print(key)
    print('----')
    print(value)
    print('')

def score_task(section,index):
  task_score = score[section][index]
  print(section, task_score)
  return task_score + 1

def stamp_task(task):
  return (task[0],date.today().isoformat())

def clear_task(task):
  print(task)
  return (task[0],)

def clear_tasks(tasks):
  tasks["Daily"] = [clear_task(task)  if check(task,today) else task for task in tasks["Daily"]]
  tasks["Weekly"] = [clear_task(task) if check(task,today - timedelta(days=today.weekday())) else task for task in tasks["Weekly"]]
  tasks["Monthly"] = [clear_task(task) if check(task,today - timedelta(days=today.day-1)) else task for task in tasks["Monthly"]]

def check(task,date_to):
  return len(task) > 1 and datetime.strptime(task[1],'%Y-%m-%d').date() < date_to

def total_score():
  precents = {'Total':0}
  for section,tasks in score.items():
    precents[section] = [task/maxs[section] for task in tasks]
    precents[section+'total'] = reduce((lambda x, y: x + y),precents[section]) / len(precents[section])
    precents['Total'] = precents['Total'] + precents[section+'total']
  precents['Total'] = precents['Total'] / len(score)
  return precents




def main():
  global score
  chores = read_file()
  score = read_file('score.json')
  clear_tasks(chores)
  # print('***********************************')
  # print(print_scores(total_score()))
  # print('***********************************')
  print_section(chores)
  check = raw_input('Check: ')
  if len(check):
    section, index = literal_eval(check)
    score[section][index] = score_task(section, index)
    chores[section][index] = str(stamp_task(chores[section][index]))
    write_file(score)
    write_file(chores,'chores.json')



main()