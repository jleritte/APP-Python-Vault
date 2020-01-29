//Crypto Object to make usage of WebCrypto less verbose
import {encode,decode,fromHexString,toBase64,fromBase64} from './utils.js'

const c = crypto,
			s = c.subtle

let ecKey, dataKey, passbytes, serverPubKey, currentPubKey

export default class CRYPTO {
	constructor() {
		this.generateECKeyPair().then(kp => ecKey = kp)
	}

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
		return cipherblock
	}

	async decrypt(data,key = dataKey, aad = passbytes) {
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

	async generateECKeyPair() {
		let keyPair = await s.generateKey({name:"ECDH",namedCurve:"P-256"},true,['deriveKey'])
		return keyPair
	}

	async createExchangeKey(privateKey = ecKey.privateKey,publicKey = serverPubKey) {
		let sharedKey = await s.deriveKey({name: "ECDH", public: publicKey},
			privateKey,
			{name: "AES-GCM", length: 256},
			false,
			['encrypt','decrypt'])
		return sharedKey
	}

	async exportPublicKey(key = ecKey.publicKey ) {
		let keyBytes = await s.exportKey('spki', key)
		return toBase64(keyBytes)
	}

	async importPublicKey(data) {
		data = fromBase64(data)
		let pubKey = await s.importKey('spki',
			pemkey,
			{name:'ECDH',namedCurve:'P-256'},
			false,
			['deriveKey'])
		return pubKey
	}

	async setServerPubKey(key) {
		key = await importPublicKey(key)
		serverPubKey = key
	}

	async updateCurrentPubKey(key) {
		key = await importPublicKey(key)
		currentPubKey = key
	}

	async unlockDataKey(passphrase,data) {
		data = fromHexString(data)
		passbytes = encode(passphrase)
		let passKey = await this.deriveKey(data.slice(0,16)),
			rawKey = await this.decrypt(data.slice(16),passKey)
		dataKey = await s.importKey('raw',
			rawKey,
			{name: 'AES-GCM',length: 256},
			false,
			['encrypt','decrypt'])
	}
}