from file_handle import read_raw
import random

words = {k: v for k, v in [s.split(' ') for s in read_raw('../wordlist.txt')]}
delims = " .!?0123456789"
delim_weights = (52, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)


def generate(count):
  password = ''
  for x in range(count):
    key = ''.join([random.choice('123456') for x in range(5)])
    word = words[key]
    if random.choice([True, False]):
      word = word.capitalize()
    password += word + \
      random.choices(delims, weights=delim_weights, k=1)[0]
  return password
