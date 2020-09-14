import CRYPTO, {unlockRecords,unlockData} from './crypto.js'
import socket from './websocket.js'
import EventEmitter from './events.js'
import {
    Login,
    ErrorDiv,
    RecordHTML,
    RecordList,
    RecordButtons,
    EditRecordForm,
    Modal,
    DeleteConfirm
  } from './ui.js'

const c = new CRYPTO(),
      listeners = new EventEmitter(),
      data = new Map(),
      ws = new socket(listeners),
      approot = document.body

let error, logform, records, buttons, add, selected, record, edit

function login() {
  const password = logform.querySelector('.password').value
  ws.send('login',{username:'jokersadface',password})
  listeners.listen('login',async (success,data) => {
    if(success){
      await c.unlockDataKey(password, data)
      sync()
    } else {
      error = error || new ErrorDiv(logform.parentNode,'Invalid Password')
      animate(logform,'shake')
    }
  })
}

function clearError() {
  if(error) {
    remove(error,'fadeOut')
    error = undefined
  }
}

function logout() {

}

function update() {
  const out = [...data].map(([k,v]) => {return{entry:k,plain:v}})
  ws.send('update',out)
  listeners.listen('update',async (success,data) => {
    if(success){
      sync()
    }
  })
}

function sync() {
  ws.send('sync')
  listeners.listen('sync',async (success,raw) => {
    if(success){
      await unlockRecords(raw,data)
      remove(logform,'fadeOut',showRecords)
    }
  })
}

function showRecords() {
  records = new RecordList(approot,data,selectRecord)
  buttons = new RecordButtons(approot,newRecord,editRecord,promptDelete)
  add = buttons.lastElementChild
  animate(records,'fadeIn')
}

function selectRecord(e) {
  const record = e.target
  clearError()
  for(const child of records.children) {
    child.classList.remove('highlight')
  }

  selected = record.dataset.rid
  record.classList.add('highlight')
}

async function editRecord(e) {
  if(!selected) {
    buttonError(e.target)
  } else {
    clearError()
    record = await openRecord(selected)
    openEditFrom(record)
  }
}

function newRecord() {
  clearError()
  selected = undefined
  record = undefined
  for(let child of records.children) {
    child.classList.remove('highlight')
  }
  openEditFrom()
}

function openEditFrom(record = {}) {
  if(edit) closeEditForm(0)
  edit = new EditRecordForm(approot,record,saveRecord,closeEditForm)
  animate(edit,'slideInRight')
}

async function openRecord(id) {
  const content = await unlockData(data.get(id))
  console.log(content)
  return {name: content[0],password:content[1][0],userId: content[1][1]}
}


function closeEditForm(replace = true) {
  if(edit) {
    remove(edit,replace ? 'slideOutRight' : 'fadeOut')
    edit = undefined
  }
}

async function saveRecord() {
  let temp = Array.from(edit.querySelectorAll('input')).reduce((a,v) => {
              a[v.className] = v.value
              return a
            },{}),
      isNew = !record
  record = !record ? new Record(temp.name) : record
  record.name = temp.name
  record.userId = temp.userId
  record.password = temp.password
  await vault.addRecord(record)
  vault.sync()
  if(isNew){
    temp = new ui.RecordHTML(records,record,selectRecord)
    animate(temp,'fadeIn')
  }
  closeEditForm()
}

async function promptDelete(e) {
  if(!selected) {
    buttonError(e.target)
  } else {
    clearError()
    let temp = await vault.retrieveRecord(selected)
    openModal()
    new DeleteConfirm(modal,temp.name,deleteRecord,closeModal)
  }
}

function animate(node,clss) {
  node.classList.toggle(clss)
  const duration = +getComputedStyle(node).animationDuration.replace('s','') * 1000
  setTimeout(_=> node.classList.toggle(clss),duration)
}

function buttonError(target) {
  if(data.size < 1) {
    error = error ? error : new ErrorDiv(buttons, 'Please Create a Record First')
    animate(add,'shake')
  } else {
    error = error ? error : new ErrorDiv(buttons,'Please Select a Record')
    animate(target,'shake')
  }
}

function remove(node,clss,follow) {
  animate(node,clss)
  let duration = +getComputedStyle(node).animationDuration.replace('s','') * 1000
  setTimeout(_=>{
    node.remove()
    follow && follow()
  },duration - 50)
}

function init() {
  logform = new Login(approot,{onclick: login,onkeydown: clearError})
  animate(logform,'fadeIn')
  window.onkeydown = e => {
    switch(e.code) {
      case 'Enter':
      case 'NumpadEnter': login(); break;
    }
  }
}


init()