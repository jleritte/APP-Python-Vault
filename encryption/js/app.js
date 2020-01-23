import $$ from './dom.js'
import CRYPTO from './crypto.js'
import {decode} from './utils.js'

const c = new CRYPTO()

let data,
		// ws = connectWS(),
		password = 'test'

function openFile(e) {
	console.log("File Selected")
	let file = this.files[0]
	if(file){
		let read = new FileReader()
		read.onload = e => {
			data = e.target.result.split(/\r?\n/)
			c.unlockDataKey(password,data[0]).then(_ => {
				data.splice(0,1)
				unlockRecords(data)
			})
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

	ws.onmessage = async e => {
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

async function unlockRecords(records) {
	console.log('Records')
	for(let record of records) {
		let plain = await c.decrypt(record)
		plain = decode(plain).replace(/\(/,'[').replace(/\)/,']').replace(/'/g,'"')
		console.log(JSON.parse(plain))
	}
}