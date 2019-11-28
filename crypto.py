# crypto functions
import os, hashlib
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

def unlock_data(key,passphrase,data):
	for i,item in enumerate(data):
		item['plain'] = decrypt(key,passphrase,item['cipher'])
		del item['cipher']
		data[i] = item
	return data












# testing code down here
# username = raw_input("Who are you? ")+".hex"
# data = parse_file(username)
# salt = data[0]['salt'] if len(data) else None
# passphrase ss("Enter Passphrase: ",'*')
# key_slice = len(passphrase) % 32
# generated_salt, derived_key = derive_key(passphrase,salt)
# if len(data):
# 	del data[0]['salt']
# 	data[0]['key'] = decrypt(derived_key[key_slice:key_slice+32],passphrase,data[0]['key'])
# 	data = data[:1] + unlock_data(data[0]['key'],passphrase,data[1:])
# else:
# 	print "Generating Key, Please wait"
# 	key = os.urandom(int(256/8))
# 	wrapped_key = encrypt(derived_key[key_slice:key_slice+32],key,passphrase)
# 	store_entry(username,{"cipher":ba.b2a_hex(generated_salt+wrapped_key),'entry':''})
# 	data.append({'key':key,'salt':generated_salt,'entry':ba.b2a_hex(generated_salt+wrapped_key)})

# while True:
# 	for item in data:
# 		if 'plain' in item.keys():
# 			print item['plain']
# 	print
# 	message = raw_input("What to lock: ")
# 	if message == 'q':
# 		break

# 	record = {'plain': message}
# 	record['cipher'] = ba.b2a_hex(encrypt(data[0]['key'], message, passphrase))
# 	record["entry"] = record['cipher']
# 	store_entry(username,record)
# 	del record['cipher']
# 	data.append(record)
