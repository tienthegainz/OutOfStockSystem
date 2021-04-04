const notify = (data) => {
  return {
    type: "NOTIFY",
    payload: data
  }
}

const cancel = () => {
  return {
    type: "CANCEL",
  }
}

export default { notify, cancel }