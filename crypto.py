# crypto functions
import os, hashlib, fileinput
import binascii as ba
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

BE = default_backend()

def derive_key(passphrase, salt):
	salt = salt if salt != None else os.urandom(16)
	dk = hashlib.pbkdf2_hmac("sha256",passphrase,salt,100000)

	return (salt,ba.b2a_hex(dk))

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



# file read/write functions
def read_stored_key(name):
	with fileinput.input(name,True,'.bak') as f:
		for line in f:
			print(line)
	# vault = open(name,"a+")
	# vault.seek(0,0)

	# enparms = vault.readlines()
	# enparms = enparms[0].strip() if len(enparms) else "00"
	# vault.close()
	return '00'#enparms

def store_key(name,key):
	vault = open(name,"w")
	vault.write(str(ba.b2a_hex(key))[2:-1]+'\n')
	vault.close()

def store_record(name,record):
	with open(name) as f:
		text = '\n'.join(f.readlines()[lambda line: line.strip() if line.strip() != record.entry else record.cipher])

	with open(name,'w') as f:
		f.write(text)

def parse_records(name):
	with open(name) as f:
		print(f.read())









# testing code down here
username = input("Who are you? ")+".hex"
shex = ba.a2b_hex(read_stored_key(username))
passphrase = ''
salt = shex[:16] if shex != b'\x00' else None
key_slice = len(passphrase) % 32
while True:
	passphrase = bytes(input("Enter Passphrase: "),'utf-8')
	if passphrase == b'q':
		break

	generated_salt, derived_key = derive_key(passphrase,salt)
	salt = generated_salt
	if shex != b'\x00':
		print("UnWrapping Key, Please wait")
		key = decrypt(derived_key[key_slice:key_slice+32],passphrase,shex[16:])
		if key == "Invalid Passphrase":
			print(key)
			continue
	else:
		print("Generating Key, Please wait")
		key = os.urandom(int(256/8))
		wrapped_key = encrypt(derived_key[key_slice:key_slice+32],key,passphrase)
		store_key(username,salt+wrapped_key)
		print(salt, wrapped_key)
		print(ba.b2a_hex(salt+wrapped_key))


	print("Welcome Ready to Encrypt")
	message = bytes(input("What to lock: "),'utf-8')
	if message == b'q':
		break

	# print len(message)
	cipherblock = encrypt(key, message, passphrase)
	print(cipherblock)
	record = {"cipher": cipherblock,"entry": ""}
	# print decrypt(key,passphrase,cipherblock)