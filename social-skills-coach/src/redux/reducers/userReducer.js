// Action Types
export const SET_USER = 'SET_USER';
export const CLEAR_USER = 'CLEAR_USER';
export const UPDATE_USER_SETTINGS = 'UPDATE_USER_SETTINGS';

// Initial State
const initialState = {
  isAuthenticated: false,
  userData: null,
  settings: {
    notifications: true,
    dailyReminders: true,
    feedbackDetail: 'medium',
  },
  loading: false,
  error: null,
};

// Reducer
const userReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_USER:
      return {
        ...state,
        isAuthenticated: true,
        userData: action.payload,
        error: null,
      };
    
    case CLEAR_USER:
      return {
        ...state,
        isAuthenticated: false,
        userData: null,
      };
    
    case UPDATE_USER_SETTINGS:
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload,
        },
      };
    
    default:
      return state;
  }
};

// Action Creators
export const setUser = (userData) => ({
  type: SET_USER,
  payload: userData,
});

export const clearUser = () => ({
  type: CLEAR_USER,
});

export const updateUserSettings = (settings) => ({
  type: UPDATE_USER_SETTINGS,
  payload: settings,
});

export default userReducer; 