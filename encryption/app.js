let data, salt,
		ws = connectWS(),
		password = new TextEncoder().encode('test'),
		iterations = 100000


function openFile(e) {
	console.log("File Selected")
	let file = this.files[0]
	if(file){
		let read = new FileReader()
		read.onload = e => {
			data = e.target.result.split(/\r?\n/).map(entry => ({entry,cipher: fromHexString(entry)}))
			salt = data[0].cipher.slice(0,16)
			data[0] = {entry:data[0].entry,key: data[0].cipher.slice(16)}
			unlockKey()
		}
		read.readAsText(file, "UTF-8")
	}
}
document.querySelector('input').addEventListener('change', openFile)

function connectWS() {
	let ws = new WebSocket('ws://127.0.0.1:9002')
	ws.onopen = e => {
		console.log('Connected')
		messageWS(ws)
	}

	ws.onmessage = e => {
		data = e.data
		console.log(data)
		// update()
	}

	ws.onclose = e => {
		if(e.wasClean) {
			console.log(`Connection closed - code:${e.code}  reason:${e.reason}`)
		} else {
			console.log('Connection Died')
		}
	}

	ws.onerror = e => {
		console.log(`Error: ${e.message}`)
	}
	return ws
}

async function unlockKey() {
	let keySeed = await crypto.subtle.importKey('raw', password, {name: 'PBKDF2'}, false,
				['deriveKey']),
			passKey = await crypto.subtle.deriveKey({name: 'PBKDF2', salt, iterations, hash: 'SHA-256'},
				keySeed, {name: 'AES-GCM',length: 256}, true, ['encrypt','decrypt']),
			rawKey = await crypto.subtle.decrypt({name: "AES-GCM", iv: data[0].key.slice(0,12),
				additionalData: password}, passKey, data[0].key.slice(12)),
			key = await crypto.subtle.importKey('raw', new Uint8Array(rawKey),
				{name: 'AES-GCM',length: 256}, false, ['encrypt','decrypt'])
	unlockRecords(key,data.slice(1))
}

async function unlockRecords(key,records) {
	console.log('Records')
	for(let record of records) {
		let plain = new TextDecoder().decode(await crypto.subtle.decrypt(
					{name: "AES-GCM", iv: record.cipher.slice(0,12), additionalData: password},
					key, record.cipher.slice(12)))
		console.log(plain)
	}
}

const fromHexString = hexString =>
	new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));

const toHexString = bytes =>
	bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');
