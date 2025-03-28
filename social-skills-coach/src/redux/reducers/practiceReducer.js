// Action Types
export const START_PRACTICE_SESSION = 'START_PRACTICE_SESSION';
export const END_PRACTICE_SESSION = 'END_PRACTICE_SESSION';
export const ADD_MESSAGE = 'ADD_MESSAGE';
export const SET_FEEDBACK = 'SET_FEEDBACK';
export const RESET_PRACTICE = 'RESET_PRACTICE';

// Initial State
const initialState = {
  activeSession: false,
  sessionId: null,
  sessionType: null,
  messages: [],
  feedback: null,
  history: [],
  loading: false,
  error: null,
};

// Reducer
const practiceReducer = (state = initialState, action) => {
  switch (action.type) {
    case START_PRACTICE_SESSION:
      return {
        ...state,
        activeSession: true,
        sessionId: action.payload.sessionId,
        sessionType: action.payload.sessionType,
        messages: [
          {
            id: 1,
            text: 'Hi there! I\'m your AI conversation partner. What social scenario would you like to practice today?',
            isUser: false,
            timestamp: new Date().toISOString(),
          },
        ],
        feedback: null,
      };
    
    case END_PRACTICE_SESSION:
      const newHistoryEntry = {
        sessionId: state.sessionId,
        sessionType: state.sessionType,
        messages: state.messages,
        feedback: state.feedback,
        endedAt: new Date().toISOString(),
      };
      
      return {
        ...state,
        activeSession: false,
        history: [newHistoryEntry, ...state.history],
        messages: [],
        feedback: null,
        sessionId: null,
        sessionType: null,
      };
    
    case ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, {
          ...action.payload,
          timestamp: new Date().toISOString(),
        }],
      };
    
    case SET_FEEDBACK:
      return {
        ...state,
        feedback: action.payload,
      };
    
    case RESET_PRACTICE:
      return {
        ...initialState,
        history: state.history, // Keep history
      };
    
    default:
      return state;
  }
};

// Action Creators
export const startPracticeSession = (sessionType) => ({
  type: START_PRACTICE_SESSION,
  payload: {
    sessionId: Date.now().toString(),
    sessionType,
  },
});

export const endPracticeSession = () => ({
  type: END_PRACTICE_SESSION,
});

export const addMessage = (message) => ({
  type: ADD_MESSAGE,
  payload: message,
});

export const setFeedback = (feedback) => ({
  type: SET_FEEDBACK,
  payload: feedback,
});

export const resetPractice = () => ({
  type: RESET_PRACTICE,
});

export default practiceReducer; 