# crypto functions
import os, hashlib
import binascii as ba
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from ast import literal_eval

BE = default_backend()

def derive_key(passphrase, salt):
  salt = salt if salt != None else os.urandom(16)
  dk = hashlib.pbkdf2_hmac("sha256",passphrase,salt,100000)
  return (salt,ba.b2a_hex(dk))

def encrypt(key, plaintext, passphrase = ''):
  iv = os.urandom(12)
  encryptor = Cipher(algorithms.AES(key),modes.GCM(iv),BE).encryptor()
  if passphrase:
    encryptor.authenticate_additional_data(passphrase)
  ciphertext = encryptor.update(plaintext) + encryptor.finalize()
  return iv + encryptor.tag + ciphertext

def decrypt(key, cipherblock, passphrase = ''):
  iv = cipherblock[:12]
  ciphertext = cipherblock[28:]
  tag = cipherblock[12:28]
  decryptor = Cipher(algorithms.AES(key),modes.GCM(iv,tag),BE).decryptor()
  if passphrase:
    decryptor.authenticate_additional_data(passphrase)
  try:
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
  except:
    plaintext = None
  return plaintext

def unlock_record(key, passphrase, record):
  record['plain'] = literal_eval(decrypt(key,record['cipher'],passphrase).decode())
  del record['cipher']
  return record

def lock_record(key, passphrase, record):
  record['cipher'] = encrypt(key,str(record['plain']).encode(),passphrase)
  del record['plain']
  return record