const stackStates = {
  RUNNING: {
    label: 'Running',
    classes: 'text-emerald-400 bg-emerald-500/10'
  },
  STOPPED: {
    label: 'Stopped',
    classes: 'text-neutral-400 bg-neutral-400/10'
  },
  RESTARTING: {
    label: 'Restarting',
    classes: 'text-yellow-500 bg-yellow-400/10'
  },
  PAUSED: {
    label: 'Paused',
    classes: 'text-purple-400 bg-purple-400/10'
  }
}

export { stackStates }
