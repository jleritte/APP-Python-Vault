const c = crypto,
			s = c.subtle

let passKey, salt, dataKey, passPhrase

export default class CRYPTO {
	random(size = 1) {
		return c.getRandomValues(new Uint8Array(size))
	}

	async encrypt(data,key = dataKey,aad = passPhrase) {
		if(typeof data === 'string') data = encode(data)
		let iv = this.random(12),
				ciphertext = await s.encrypt({
					name: 'AES-GCM',
					iv
				},key,data)
		const cipherblock = [...iv,...new Uint8Array(ciphertext)]
		return toHexString(cipherblock)
	}

	async decrypt(data,key = dataKey, add = passPhrase) {
		data = fromHexString(data)
		let plain
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
