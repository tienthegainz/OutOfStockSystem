const currentUser = (state = {
  token: null,
  isLoggedIn: false,
  user: {
    username: null,
    admin: false
  }
}, action) => {
  switch (action.type) {
    case "LOGIN":
      return {
        ...state,
        token: action.payload.token,
        isLoggedIn: true,
        user: action.payload.user
      }
    case "LOGOUT":
      return {
        ...state,
        token: null,
        isLoggedIn: false,
        user: {
          username: null,
          admin: false
        }
      }
    default:
      return state
  }
}

export default currentUser;