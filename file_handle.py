# file read/write functions
import binascii as ba

def store_entry(name,record):
	found = 0
	text = 0
	with open(name,'r') as f:
		text = f.readlines()
		for i,line in enumerate(text):
			line = line.strip()
			if line == record["entry"]:
				line = record["cipher"]
				found = 1
			text[i] = line
		if not found:
			text.append(record["cipher"])

	with open(name,'w') as f:
		f.write('\n'.join(text))

def parse_file(name):
	content = []
	with open(name,'a+') as f:
		f.seek(0,0)
		for i,line in enumerate(f.readlines()):
			temp = {'entry': line.strip()}
			line = ba.a2b_hex(temp["entry"])
			if i < 1:
				temp['salt'] = line[:16]
				temp['key'] = line[16:]
			else:
				temp['cipher'] = line
			content.append(temp)
	return content