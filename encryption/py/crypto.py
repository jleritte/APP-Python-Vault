# crypto functions
import os, hashlib
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from ast import literal_eval
import binascii as ba

BE = default_backend()
p256 = ec.SECP256R1()
ECDH = ec.ECDH()

def generate_key_pair():
  key_pair = ec.generate_private_key(p256, BE)
  return key_pair

def get_shared_key(private,public):
  shared_key = private.exchange(ECDH,public)
  return shared_key

def import_public_key(pem):
  pem = f"-----BEGIN PUBLIC KEY-----\n{pem}\n-----END PUBLIC KEY-----"
  public_key = load_pem_public_key(pem.encode(),BE)
  return public_key

def export_public_key(key):
  key_string = key.public_bytes(encoding = Encoding.PEM,format = PublicFormat.SubjectPublicKeyInfo)
  key_string = "".join([s.decode() for s in key_string.splitlines()[1:-1]])
  return key_string

def derive_key(passphrase, salt):
  salt = salt if salt != None else os.urandom(16)
  dk = hashlib.pbkdf2_hmac("sha256",passphrase,salt,100000)
  return (salt,dk)

def encrypt(key, plaintext, passphrase = ''):
  iv = os.urandom(12)
  encryptor = Cipher(algorithms.AES(key),modes.GCM(iv),BE).encryptor()
  if passphrase:
    encryptor.authenticate_additional_data(passphrase)
  ciphertext = encryptor.update(plaintext) + encryptor.finalize()
  return iv + ciphertext + encryptor.tag

def decrypt(key, cipherblock, passphrase = ''):
  iv = cipherblock[:12]
  ciphertext = cipherblock[12:-16]
  tag = cipherblock[-16:]
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

def unlock_data(record,passphrase):
  salt,key = derive_key(record[0].encode(),passphrase)
  return (record[0],literal_eval(decrypt(key,ba.a2b_hex(record[1])).decode()))

def lock_data(record,passphrase):
  salt,key = derive_key(record[0].encode(),passphrase)
  return (record[0],ba.b2a_hex(encrypt(key,str(record[1]).encode())).decode())