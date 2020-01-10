export function encode(string = "") {
	return new TextEncoder().encode(string)
}

export function decode(uint8array = new Uint8Array()) {
	return new TextDecoder().decode(uint8array)
}

export function fromHexString(hexString){
	return new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))
}

export function toHexString(bytes){
	return bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '')
}
