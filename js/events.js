const listeners = new WeakMap()

export default class EventEmitter {
  constructor() {
    listeners.set(this, {})
  }
  listen(name, cb) {
    listeners.get(this)[name] = cb
  }
  emit(event, ...args) {
    listeners.get(this)[event](...args)
  }
}
