const notification = (state = {
  trigger: false,
  title: '',
  message: '',
}, action) => {
  switch (action.type) {
    case "NOTIFY":
      return {
        trigger: true,
        title: action.payload.title,
        message: action.payload.message,
      }
    case "CANCEL":
      return {
        trigger: false,
        title: '',
        message: '',
      }
    default:
      return state
  }
}

export default notification;