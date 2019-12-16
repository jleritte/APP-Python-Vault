# Chores Checklist
import json
from datetime import datetime, date
from ast import literal_eval

score = ''

def read_file(name = 'chores.json'):
  with open(name) as f:
    return json.load(f)

def write_file(data,name = 'score.json'):
  with open(name,'w') as f:
    json.dump(data,f)

def print_section(chores,section = 'Daily'):
  print(section)
  tasks = [literal_eval(task) for task in chores[section]]
  for task in tasks:
    print(task[0])
    score_task(task)

def score_task(task):


def main():
  global score
  chores = read_file()
  score = read_file('score.json')
  today = date.today()
  startofyear = date(today.year,1,1)
  days = (today - startofyear).days
  print('***********************************')
  print(days)
  print(score)
  print('***********************************')
  ly,lm,ld = literal_eval(score['Last'])
  last = date(ly,lm,ld)
  # today = last
  print_section(chores)
  if today.isoweekday() is 1:
    print_section(chores,'Weekly')
  if today.day is 1:
    print_section(chores,'Monthly')
    if today.month is 1 or today.month is 4 or today.month is 7 or today.month is 10:
      print_section(chores,"Three Months")
    if today.month is 1 or today.month is 7:
      print_section(chores,"Six Months")
    if today.month is 1:
      print_section(chores,"Annually")
  score['check'] = input('Check: ')
  write_file(score)



main()