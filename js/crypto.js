//Crypto Object to make usage of WebCrypto less verbose
import {
    encode,
    decode,
    toHexString,
    fromHexString,
    toBase64,
    fromBase64,
    toTuple,
    fromTuple
  } from './utils.js'

const c = crypto,
      s = c.subtle,
      tranAad = encode('transmission')

let ecKey, dataKey, passbytes, serverPubKey

export default class CRYPTO {
  constructor() {
    ecKey || this.generateECKeyPair().then(kp => ecKey = kp)
  }

  async generateECKeyPair() {
    let keyPair = await s.generateKey({
        name:"ECDH",
        namedCurve:"P-256"
      },true,['deriveKey'])
    return keyPair
  }

  async unlockDataKey(passphrase, data) {
    data = fromHexString(data)
    passbytes = encode(passphrase)
    const passKey = await deriveKey(data.slice(0, 16)),
      rawKey = await decrypt(data.slice(16), passKey)
    dataKey = await s.importKey('raw',
      rawKey,
      {name: 'AES-GCM', length: 256},
      false,
      ['encrypt', 'decrypt']
    )
  }

  async unlockRecords(data, records) {
    for(const record of data) {
      let plain = await decrypt(fromHexString(record))
      plain = fromTuple(decode(plain))
      records.set(record, JSON.parse(plain))
    }
  }

  async unlockData([name, data]) {
    const key = await deriveKey(passbytes, encode(name))
    data = await decrypt(fromHexString(data), key, encode(''))
    data = fromTuple(decode(data))
    return [name, JSON.parse(data)]
  }

  async lockData([name, data]) {
    const key = await deriveKey(passbytes, encode(name))
    data = toTuple(JSON.stringify(data))
    data = await encrypt(encode(data), key, encode(''))
    return [name, toHexString(data)]
  }
}

function random(size = 1) {
  return c.getRandomValues(new Uint8Array(size))
}

async function encrypt(data, key=dataKey, aad=passbytes) {
  if(typeof data === 'string') data = encode(data)
  const iv = random(12),
    ciphertext = await s.encrypt({
      name: 'AES-GCM',
      iv,
      additionalData: aad
    }, key, data)
  return [...iv, ...new Uint8Array(ciphertext)]
}

async function decrypt(data, key=dataKey, aad=passbytes) {
  const iv = data.slice(0, 12)
  return await s.decrypt({
      name: 'AES-GCM',
      iv,
      additionalData: aad
    }, key, data.slice(12)
  )
}

async function deriveKey(salt, pass=passbytes) {
  const iterations = 100000,
    keySeed = await s.importKey('raw',
      pass,
      {name: 'PBKDF2'},
      false,
      ['deriveKey']
    )
  return await s.deriveKey({
      name: 'PBKDF2',
      salt,
      iterations,
      hash: 'SHA-256'
    }, keySeed, {name: 'AES-GCM', length: 256},
    false, ['encrypt', 'decrypt']
  )
}

async function deriveSharedKey(priKey=ecKey.privateKey, pubKey=serverPubKey) {
  return await s.deriveKey({name: "ECDH", public: pubKey},
    priKey,
    {name: "AES-GCM", length: 256},
    false,
    ['encrypt','decrypt']
  )
}

async function importPublicKey(data) {
  const pemkey = fromBase64(data)
  return await s.importKey('spki',
    pemkey,
    {name:'ECDH', namedCurve:'P-256'},
    false,
    ['deriveKey'])
}

export async function exportPublicKey(key=ecKey.publicKey ) {
  return toBase64(await s.exportKey('spki', key))
}

export async function setServerPubKey(key) {
  serverPubKey = await importPublicKey(key)
}

export async function wrap(message) {
  if(serverPubKey) {
    const tranKey = await deriveSharedKey()
    message = toHexString(await encrypt(message, tranKey, tranAad))
  }
  return message
}

export async function unwrap(data) {
  if(serverPubKey) {
    const tranKey = await deriveSharedKey()
    data = decode(await decrypt(fromHexString(data), tranKey, tranAad))
  }
  return data
}
