import { combineReducers } from 'redux';
import currentUser from './userReducer';

const rootReducer = combineReducers({
  currentUser,
})

export default rootReducer;