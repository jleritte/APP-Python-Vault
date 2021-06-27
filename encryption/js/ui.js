class Element {
  constructor(parent, type, options) {
    const ele = document.createElement(type)
    for(const key in options) {
      ele[key] = options[key]
    }
    parent.appendChild(ele)
    return ele
  }
}

class Div extends Element{
  constructor(parent,options = {}) {
    return super(parent,'div',options)
  }
}

class Button extends Element {
  constructor(parent,options = {}) {
    const {onclick,textContent} = options,
        button = super(parent,'button',options)

    if(!onclick) button.onclick = _ => console.log('No Click Handler Set.',this)
    if(!textContent) button.textContent = "Click Me"

    return button
  }
}

class Input extends Element {
  constructor(parent,options = {}) {
    return super(parent,'input',options)
  }
}

class Password extends Input {
  constructor(parent,options = {}) {
    options.type = 'password'
    const pass = super(parent,options)
    pass.ondblclick = copyText
    return pass
  }
}

async function copyText(e) {
  e.target.type = 'input'
  e.target.select()
  document.execCommand('copy')
  e.target.type = 'password'
}

export class Login extends Div {
  constructor(parent, {onclick, onkeydown}) {
    const contain = super(parent, {className: 'logForm standardSize'}),
        inputOptions = {onkeydown, value:''}
    inputOptions.className = 'uname'
    inputOptions.placeholder = 'Username'
    new Input(contain, inputOptions)
    inputOptions.className = 'password'
    inputOptions.placeholder = 'Password'
    new Password(contain, inputOptions)
    new Button(contain,{onclick, textContent: "Login"})

    return contain
  }
}

export class ErrorDiv extends Div {
  constructor(parent,error) {
    return super(parent,{className: 'error', textContent: error})
  }
}

export class RecordButtons extends Div {
  constructor(parent,add,edit,deleteR,logout) {
    const buttons = super(parent,{className: 'buttons'})
    new Button(buttons,{onclick: logout,textContent: 'Logout'})
    new Button(buttons,{onclick: deleteR,textContent: 'Delete Record'})
    new Button(buttons,{onclick: edit,textContent: 'Edit Record'})
    new Button(buttons,{onclick: add,textContent: 'Add Record'})

    return buttons
  }
}

export class RecordList extends Div {
  constructor(parent,data,onclick,ondblclick) {
    const list = super(parent,{className: 'records'})

    for (const record of data) {
      new RecordHTML(list,record,onclick,ondblclick)
    }
    return list
  }
}

class RecordHTML extends Div {
  constructor(parent,data,onclick,ondblclick) {
    const options = {
        className: 'record standardSize',
        textContent: data[1][0],
        onclick, ondblclick
      },
      record = super(parent, options)
    record.dataset.rid = data[0]
    return record
  }
}

export class EditRecordForm extends Div {
  constructor(parent,{name,userId,password},save,cancel,pass) {
    const edit = super(parent,{className: 'editForm'})
    new Div(edit,{textContent: 'Record Name',title: "Required"})
    new Input(edit,{value: name || '', placeholder: 'Name',className: 'name'})
    new Div(edit,{textContent: 'Password',title: "Required"})
    new Password(edit,{value: password || '', placeholder: 'Password',className: 'password'})
    const random = new Div(edit,{className:'random'})
    new Div(random,{textContent:"Generate Password"})
    new Input(random,{type:"number",value:4})
    new Button(random,{textContent:"⚀",onclick:pass})
    new Div(edit,{textContent: 'Username',title: "Optional"})
    new Input(edit,{value: userId || '', placeholder: 'Username',className: 'userId'})
    new Button(edit,{className: 'alt',onclick: cancel,textContent: 'Cancel'})
    new Button(edit,{onclick: save,textContent: 'Save'})

    return edit
  }
}

export class Sync extends Div {
  constructor(parent,time,onclick) {
    return super(parent,{
      className: 'sync',
      textContent: `Last synced ${time}`,
      onclick
    })
  }
}

export class Modal extends Div {
  constructor(parent) {
    return super(parent,{className: 'modal'})
  }
}

export class DeleteConfirm extends Div {
  constructor(parent,name,confirm,cancel) {
    const prompt = super(parent,{className: 'deletePrompt'})
    new Div(prompt,{textContent: `Are you sure you want to delete ${name}?`})
    new Button(prompt,{className: 'alt',onclick: cancel,textContent: 'Cancel'})
    new Button(prompt,{onclick: confirm,textContent: 'Delete'})

    return prompt
  }
}
