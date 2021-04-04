const login = (data) => {
  return {
    type: "LOGIN",
    payload: data
  }
}

const logout = () => {
  return {
    type: "LOGOUT",
  }
}

export default { login, logout }