const c = crypto,
			s = c.subtle

let passKey, salt, dataKey, passbytes, initialized = false, iterations = 100000

export default class CRYPTO {
	random(size = 1) {
		return c.getRandomValues(new Uint8Array(size))
	}

	async encrypt(data,key = dataKey,aad = passbytes) {
		if(typeof data === 'string') data = encode(data)
		let iv = this.random(12),
				ciphertext = await s.encrypt({
					name: 'AES-GCM',
					iv,
					additionalData: aad
				},key,data)
		const cipherblock = [...iv,...new Uint8Array(ciphertext)]
		return toHexString(cipherblock)
	}

	async decrypt(data,key = dataKey, aad = passbytes) {
		data = fromHexString(data)
		let iv = data.slice(0,12),
				plaintext = decode(await s.decrypt({
					name: 'AES-GCM',
					iv,
					additionalData: aad
				},key,data.slice(12)))
		return plaintext
	}

	async deriveKey() {
		let keySeed = await s.importKey('raw',
					passbytes,
					{name: 'PBKDF2'},
					false,
					['deriveKey']
				)
		passKey = await s.deriveKey({
				name: 'PBKDF2',
				salt,
				iterations,
				hash:
				'SHA-256'
			}, keySeed, {name: 'AES-GCM',length: 256},
			true, ['encrypt','decrypt'])
	}

	async unlockDataKey(passphrase,data) {
		passbytes = encode(passphrase)
		salt = 'yes'
		dataKey = "pttttttt"
		initialized = true
	}
}

function encode(string = "") {
	return new TextEncoder().encode(string)
}

function decode(uint8array = new Uint8Array()) {
	return new TextDecoder().decode(uint8array)
}

function fromHexString(hexString){
	return new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))
}

function toHexString(bytes){
	return bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '')
}
