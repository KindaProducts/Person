import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';

// Initial reducers (will add more as needed)
import userReducer from './reducers/userReducer';
import practiceReducer from './reducers/practiceReducer';

const rootReducer = combineReducers({
  user: userReducer,
  practice: practiceReducer,
});

const store = createStore(rootReducer, applyMiddleware(thunk));

export default store; 