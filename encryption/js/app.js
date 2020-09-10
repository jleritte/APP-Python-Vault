import $$ from './dom.js'
import CRYPTO from './crypto.js'
import {encode,decode,fromHexString,toHexString} from './utils.js'

const c = new CRYPTO(),
      tranAad = encode('transmission')

let data = new Map(),
    ws = connectWS(),
    pw = 'test'

function connectWS() {
  const ws = new WebSocket('ws://127.0.0.1:9002')
  ws.onopen = async e => {
    console.log('Connected')
    const key = await c.exportPublicKey()
    ws.send(JSON.stringify({action:"key",data:key}))
  }

  ws.onmessage = async e => {
    let {data} = e
    if(c.pubKeySet){
      return process(await unwrap(data))
    }
    data = JSON.parse(data)
    if(data.key) await c.setServerPubKey(data.key)
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

async function unwrap(data) {
  const tranKey = await c.createExchangeKey()
  data = decode(await c.decrypt(fromHexString(data),tranKey,tranAad))
  return JSON.parse(data)
}

async function sendMessage(message) {
  const tranKey = await c.createExchangeKey()
  message = toHexString(await c.encrypt(message,tranKey,tranAad))
  ws.send(message)
}


async function unlockRecords(records) {
  for(const record of records) {
    let plain = await c.decrypt(fromHexString(record))
    plain = decode(plain).replace(/\(/,'[').replace(/\)/,']').replace(/'/g,'"')
    data.set(record,JSON.parse(plain))
  }

  /*this is test ui*/
  let dom = document.querySelector('.records')
  for(const record of data) {
    const div = document.createElement('div')
    div.textContent = record[1][0]
    div.id = record[0]
    div.onclick = ({target}) => openRecord(target.id)
    dom.appendChild(div)
  }
}

async function openRecord(id) {
  const content = await unlockData(data.get(id))
  alert(`${content[0]}\n${content[1][0]}\n${content[1][1]}`)
}

async function unlockData([name,data]) {
  const key = await c.deriveKey(encode(pw),encode(name))
  data = await c.decrypt(fromHexString(data),key,encode(''))
  data = decode(data).replace(/\(/,'[').replace(/\)/,']').replace(/'/g,'"')
  return [name,JSON.parse(data)]
}

async function lockData([name,data]) {
  const key = await c.deriveKey(encode(pw),encode(name))
  data = JSON.stringify(data).replace(/\[/,'(').replace(/\]/,')').replace(/'/g,'"')
  data = await c.encrypt(encode(data),key,encode(''))
  return [name,toHexString(data)]
}

async function process({action,success,data}) {
  if(action === 'login') {
    if(success){
      await c.unlockDataKey(pw, data)
      sync()
    }
  }
  if(action === 'sync') {
    if(success){
      await unlockRecords(data)
    }
  }
  if(action === 'update') {
    if(success){
      sync()
    }
  }
}

function login(username,password) {
  pw = password
  sendMessage(JSON.stringify({action:'login',data:{username,password}}))
}

function logout() {

}

function update() {
  const out = [...data].map(([k,v]) => {return{entry:k,plain:v}})
  sendMessage(JSON.stringify({action:'update',data:out}))
}

function sync() {
  sendMessage(JSON.stringify({action:'sync',data:''}))
}

window.login = login
window.data = data
window.unlockData = unlockData
window.lockData = lockData
window.update = update
window.sync = sync
