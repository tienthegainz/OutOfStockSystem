import { combineReducers } from 'redux';
import currentUser from './userReducer';
import notification from './notiReducer';

const rootReducer = combineReducers({
  currentUser,
  notification,
})

export default rootReducer;