from file_handle import read_raw
import random

words = {k: v for k, v in [s.split(' ') for s in read_raw('../wordlist.txt')]}
delims = " !?0123456789"
delim_weights = (50, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
qwerty = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
dvorak = "',.pyfgcrlaoeuidhtn;qjkxbm\"<>PYFGCRLAOEUIDHTN:QJKXBM"


def generate(count):
  password = ''
  for x in range(count):
    key = ''.join([random.choice('123456') for x in range(5)])
    word = words[key]
    if random.choice([True, False]):
      word = word.capitalize()
    password += encode_to_Dvorak(word) + random.choices(delims, weights=delim_weights, k=1)[0]
  return password


def encode_to_Dvorak(word):
  return ''.join([dvorak[qwerty.index(x)] for x in word])
