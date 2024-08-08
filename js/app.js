import CRYPTO from './crypto.js'
import socket from './websocket.js'
import EventEmitter from './events.js'
import {
    Login,
    ErrorDiv,
    RecordList,
    RecordButtons,
    EditRecordForm,
    Sync,
    Modal,
    DeleteConfirm
  } from './ui.js'

const c = new CRYPTO(),
      listeners = new EventEmitter(),
      data = new Map(),
      ws = new socket(listeners),
      approot = document.body

let filterString = "", synced, error, logform, records, buttons, syncbutton, add,
    selected, record, edit, modal

function fuzzyMatchSimple(pattern, str) {
  let patternIdx = 0, strIdx = 0
  const patternLength = pattern.length,
        strLength = str.length

  while (patternIdx != patternLength && strIdx != strLength) {
    const patternChar = pattern.charAt(patternIdx).toLowerCase()
    const strChar = str.charAt(strIdx).toLowerCase()
    if (patternChar == strChar) ++patternIdx
    ++strIdx
  }

  return patternLength != 0 && strLength != 0 && patternIdx == patternLength
    ? true
    : false
}

function login() {
  const username = logform.querySelector('.uname').value,
        password = logform.querySelector('.password').value
  ws.send('login',{username, password})
  listeners.listen('login', async (success, data) => {
    if(success){
      window.onkeydown = undefined
      await c.unlockDataKey(password, data)
      sync()
    } else {
      error = error ?? new ErrorDiv(logform.parentNode, 'Invalid Password')
      animate(logform, 'shake')
    }
  })
}
function clearError() {
  if(error) {
    remove(error, 'fadeOut')
    error = undefined
  }
}
function logout() {
  ws.close()
  window.location.reload()
}
function update() {
  const out = [...data].map(([k, v]) => {return {entry:k, plain:v}})
  ws.send('update',out)
  listeners.listen('update', success => success && sync())
}
function sync() {
  if(syncbutton) syncbutton.classList.toggle('spin')
  ws.send('sync')
  listeners.listen('sync', async (success, raw) => {
    if(syncbutton) syncbutton.classList.toggle('spin')
    if(success){
      data.clear()
      await c.unlockRecords(raw, data)
      remove(logform, 'fadeOut', showRecords)
      synced = new Date().toTimeString().substring(0, 8)
    }
  })
}
function password() {
  const length = edit.querySelector('[type=number]').value
  ws.send('password', length)
  listeners.listen('password', async (success, pass) => {
    if(success) {
      edit.querySelector('.password').value = pass
    }
  })
}
function showRecords() {
  if(syncbutton) remove(syncbutton)
  const shown = new Map([...data].filter(([k,v]) => fuzzyMatchSimple(filterString || v[0], v[0])))
  syncbutton = new Sync(approot, synced, sync)
  buttons = buttons ?? new RecordButtons(approot, newRecord,
              editRecord, promptDelete, logout, updateSearch)
  add = buttons.lastElementChild
  if(records) remove(records, 'fadeOut')
  records = new RecordList(approot, shown, selectRecord, editRecord)
  animate(records, 'fadeIn')
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
  e.target.blur()
  if(!selected) {
    buttonError(e.target)
  } else {
    clearError()
    record = await openRecord(selected)
    openEditFrom(record)
  }
}
function newRecord(e) {
  e.target.blur()
  clearError()
  selected = ''
  record = undefined
  for(let child of records.children) {
    child.classList.remove('highlight')
  }
  openEditFrom()
}
function deleteRecord(e) {
  e.target.blur()
  closeModal()
  closeEditForm()
  data.delete(selected)
  update()
  selected = undefined
  record = undefined
}
function updateSearch(e) {
  closeEditForm()
  filterString = e.target.value || ""
  showRecords()
}
function openEditFrom(record={}) {
  if(edit) closeEditForm(0)
  edit = new EditRecordForm(approot, record,
                saveRecord, closeEditForm, password)
  animate(edit, 'slideInRight')
  window.onkeydown = e => {
    switch(e.code) {
      case 'Enter':
      case 'NumpadEnter': savedRecord(); break;
      case 'Escape': closeEditForm(); break;
    }
  }
}
async function openRecord(id) {
  const content = await c.unlockData(data.get(id))
  return {name: content[0], password:content[1][0], userId: content[1][1]}
}
async function closeRecord([name, pass, uid]) {
  const content = await c.lockData([name, [pass, uid]])
  return content
}
function closeEditForm(replace=true) {
  if(edit) {
    remove(edit, replace ? 'slideOutRight' : 'fadeOut')
    edit = undefined
  }
  window.onkeydown = undefined
}
async function saveRecord() {
  let temp = Array.from(edit.querySelectorAll('input:not([type=number'))
        .reduce((a, v) => {
          a.push(v.value)
          return a
        },[])
  record = await closeRecord(temp)
  data.set(selected, record)
  update()
  closeEditForm()
}
function promptDelete(e) {
  if(!selected) {
    buttonError(e.target)
  } else {
    clearError()
    let temp = data.get(selected)
    openModal()
    new DeleteConfirm(modal, temp[0], deleteRecord, closeModal)
  }
}
function animate(node, clss) {
  node.classList.toggle(clss)
  const duration = +getComputedStyle(node).animationDuration.replace('s', '')
  setTimeout(_ => node.classList.toggle(clss), duration *1000)
}
function buttonError(target) {
  if(data.size < 1) {
    error = error ?? new ErrorDiv(buttons, 'Please Create a Record First')
    animate(add, 'shake')
  } else {
    error = error ?? new ErrorDiv(buttons, 'Please Select a Record')
    animate(target, 'shake')
  }
}
function remove(node, clss, follow) {
  animate(node, clss)
  let duration = +getComputedStyle(node).animationDuration.replace('s', '')
  setTimeout(_ => {
    node.remove()
    follow && follow()
  }, duration * 1000 - 50)
}
function openModal() {
  modal = new Modal(approot)
  animate(modal, 'fadeIn')
}
function closeModal() {
  remove(modal, 'fadeOut')
  modal = undefined
}
function init() {
  logform = new Login(approot, {onclick: login, onkeydown: clearError})
  animate(logform, 'fadeIn')
  window.onkeydown = e => {
    switch(e.code) {
      case 'Enter':
      case 'NumpadEnter': login(); break;
    }
  }
}

init()
