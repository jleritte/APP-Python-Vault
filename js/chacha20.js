'use strict'
import { encode, decode, fromHexString, toHexString } from './utils.js'

function getRandomValues(size=24) {
  return crypto.getRandomValues(new Uint8Array(size))
}

function getWord(bytes) {
  return bytes.reduceRight((word, B, i) => {
    return word ^= B << (8 * i)
  }, 0) >>> 0
}

function getBytes(word) {
  return [0, 0, 0, 0].map((_, i) => (word >>> 8 * i) & 0xFF)
}

function rotl(word, shift) {
  return ((word << shift) ^ (word >>> (32 - shift)))
}


const cols = [[0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15]],
      diags = [[0, 5, 10, 15], [1, 6, 11, 12], [2, 7, 8, 13], [3, 4, 9, 14]],
      nulls = [0x00, 0x00, 0x00, 0x00]

class XChaCha20 {
  #consts = encode("expand 32-byte k")
  #keystream = []
  #block = []
  #rounds = 10

  encrypt(key, plaintext="") {
    const iv = getRandomValues(24),
      cipher = this.#xchacha(key, iv, encode(plaintext))
    return `0x${toHexString([...iv, ...cipher])}`
  }
  decrypt(key, ciphertext='0x') {
    const bytes = fromHexString(ciphertext.substr(2)),
      plain = this.#xchacha(key, bytes.subarray(0, 24), bytes.subarray(24))
    return decode(plain)
  }
  #xchacha(key, iv, data) {
    if(!this.#arrayCheck(key) || key.length !== 32) {
      throw new Error('Key should be a 32 byte array!')
    }
    const subKey = this.#hchacha(key, iv.subarray(0, 16))
    this.#createBlock(subKey, new Uint8Array([0, ...nulls, ...iv.subarray(16)]))
    return this.#processData(data)
  }
  #hchacha(key, nonce) {
    this.#createBlock(key, nonce)
    const subKey = this.#keystream.reduce((acc, _, i) => {
      if(i < 16 || i > 47)
      return acc
    },[])
    return new Uint8Array(subKey)
  }
  #createBlock(key,nonce) {
    this.#block.length = 0
    this.#processStateChunk(this.#consts)
    this.#processStateChunk(key)
    this.#processStateChunk(nonce)
    this.#createStream()
  }
  #processStateChunk(chunk) {
    const len = chunk.length
    for(let i = 0; i < len; i += 4) {
      this.#block.push(getWord(chunk.subarray(i, i + 4)))
    }
  }
  #processData(bytes) {
    return bytes.map(B => {
      if(this.#keystream.length === 0) {
        this.#block[12]++
        this.#createStream()
      }
      return B ^ this.#keystream.shift()
    })
  }
  #createStream() {
    this.#keystream.length = 0
    const copy = [...this.#block]

    while(this.#rounds--) {
      this.#doubleRound(copy)
    }
    this.#rounds = 10
    for(let i = 0; i < copy.length; i++) {
      copy[i] += this.#block[i]
      this.#keystream.push(...getBytes(copy[i]))
    }
  }
  #doubleRound(block) {
    for(let col of cols) {
      this.#quarterround(block, ...col)
    }
    for(let diag of diags) {
      this.#quarterround(block, ...diag)
    }
  }
  #quarterround(block, a, b, c, d) {
    block[d] = rotl(block[d] ^ (block[a] += block[b]), 16)
    block[b] = rotl(block[b] ^ (block[c] += block[d]), 12)
    block[d] = rotl(block[d] ^ (block[a] += block[b]), 8)
    block[b] = rotl(block[b] ^ (block[c] += block[d]), 7)

    block[a] >>>= 0
    block[b] >>>= 0
    block[c] >>>= 0
    block[d] >>>= 0
  }
  #arrayCheck(array) {
    return array instanceof Uint8Array
  }
}

let key = encode('abcdefghijklmnopqrstuvwxyz123456')
let chacha = new XChaCha20()
let text = 'test this really long string to make sure you keep making keystream correctly'
let cipher = chacha.encrypt(key, text)
//chacha.encrypt(cipher)
