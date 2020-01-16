//Crypto Object to make usage of WebCrypto less verbose
import {encode,decode,toHexString,fromHexString} from './utils.js'

const c = crypto,
			s = c.subtle

let dataKey, passbytes, serverPubKey, initialized = false

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
			plaintext = await s.decrypt({
				name: 'AES-GCM',
				iv,
				additionalData: aad
			},key,data.slice(12))
		return plaintext
	}

	async deriveKey(salt) {
		let iterations = 100000,
		keySeed = await s.importKey('raw',
			passbytes,
			{name: 'PBKDF2'},
			false,
			['deriveKey']),
		passKey = await s.deriveKey({
				name: 'PBKDF2',
				salt,
				iterations,
				hash: 'SHA-256'
			}, keySeed, {name: 'AES-GCM',length: 256},
			false, ['encrypt','decrypt'])
		return passKey
	}

	async importPublicKey(data) {
		data = fromHexString(data)
		let pubKey = s.importKey()
	}

	async unlockDataKey(passphrase,data) {
		data = fromHexString(data)
		passbytes = encode(passphrase)
		let passKey = await this.deriveKey(data.slice(0,16)),
			rawKey = await this.decrypt(toHexString(data.slice(16)),passKey)
		dataKey = await s.importKey('raw',
			rawKey,
			{name: 'AES-GCM',length: 256},
			false,
			['encrypt','decrypt'])
		initialized = true
	}
}