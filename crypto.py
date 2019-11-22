# basic crypto functions
import os, hashlib, binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

BE = default_backend()

def derive_key(passphrase, salt = os.urandom(16)):
	dk = hashlib.pbkdf2_hmac("sha256",passphrase,salt,100000)

	return (salt,binascii.hexlify(dk))

def encrypt(key,plaintext,passphrase):
	iv = os.urandom(12)
	encryptor = Cipher(algorithms.AES(key),modes.GCM(iv),BE).encryptor()

	if passphrase:
		encryptor.authenticate_additional_data(passphrase)

	ciphertext = encryptor.update(plaintext) + encryptor.finalize()

	return iv + encryptor.tag + ciphertext

def decrypt(key, passphrase, cipherblock):
	iv = cipherblock[:12]
	ciphertext = cipherblock[28:]
	tag = cipherblock[12:28]

	decryptor = Cipher(algorithms.AES(key),modes.GCM(iv,tag),BE).decryptor()

	if passphrase:
		decryptor.authenticate_additional_data(passphrase)

	plaintext = ""

	try:
		plaintext = decryptor.update(ciphertext) + decryptor.finalize()
	except:
		plaintext = "Invalid Passphrase"

	return plaintext

def read_vault(name):
	vault = open(username+".hex","a+")
	enparms = vault.readlines()
	if len(enparms):
		enparms = enparms[0]
	else:
		enparms = "00"
	vault.close()
	return enparms




# testing code down here
username = raw_input("Who are you? ")
shex = read_vault(username)
print bytearray.fromhex(shex)
passphrase = ''
salt = ''
while True:
	passphrase = raw_input("Enter Passphrase: ")
	if passphrase == 'q':
		break

	generated_salt, derived_key = derive_key(passphrase)
	salt = generated_salt
	key = os.urandom(256/8)
	print salt, key

	key_slice = len(passphrase) % 32
	wrapped_key = encrypt(derived_key[key_slice:key_slice+32],key,passphrase)
	print binascii.hexlify(salt+wrapped_key)
	# print len(wrap_key) + len(iv)
	# print wrap_key
	# print decrypt(derived_key[:32],passphrase,iv,wrap_key,tag)
	# message = raw_input("What to lock: ")

	# print len(message)
	# cipherblock = encrypt(key, message, passphrase)
	# print cipherblock
	# print decrypt(key,passphrase,cipherblock)