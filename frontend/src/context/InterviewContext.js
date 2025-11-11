import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import toast from 'react-hot-toast';

// Create context
const InterviewContext = createContext();

// Initial state
const initialState = {
  // Session data
  sessionId: null,
  candidateName: '',
  questions: [],
  currentQuestionIndex: 0,
  
  // Interview status
  isInterviewActive: false,
  isInterviewCompleted: false,
  
  // Real-time metrics
  metrics: {
    eyeContactPercentage: 0,
    confidenceScore: 0,
    speechClarity: 0,
    emotionScores: {},
    warnings: []
  },
  
  // Media streams
  videoStream: null,
  audioStream: null,
  
  // UI state
  isLoading: false,
  error: null,
  
  // Results
  finalResults: null,
  
  // Socket connection
  socket: null,
  isConnected: false
};

// Action types
const ACTIONS = {
  SET_SESSION_ID: 'SET_SESSION_ID',
  SET_CANDIDATE_NAME: 'SET_CANDIDATE_NAME',
  SET_QUESTIONS: 'SET_QUESTIONS',
  SET_CURRENT_QUESTION: 'SET_CURRENT_QUESTION',
  SET_INTERVIEW_ACTIVE: 'SET_INTERVIEW_ACTIVE',
  SET_INTERVIEW_COMPLETED: 'SET_INTERVIEW_COMPLETED',
  UPDATE_METRICS: 'UPDATE_METRICS',
  SET_VIDEO_STREAM: 'SET_VIDEO_STREAM',
  SET_AUDIO_STREAM: 'SET_AUDIO_STREAM',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_FINAL_RESULTS: 'SET_FINAL_RESULTS',
  SET_SOCKET: 'SET_SOCKET',
  SET_CONNECTED: 'SET_CONNECTED',
  RESET_STATE: 'RESET_STATE'
};

// Reducer function
function interviewReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_SESSION_ID:
      return { ...state, sessionId: action.payload };
    
    case ACTIONS.SET_CANDIDATE_NAME:
      return { ...state, candidateName: action.payload };
    
    case ACTIONS.SET_QUESTIONS:
      return { ...state, questions: action.payload };
    
    case ACTIONS.SET_CURRENT_QUESTION:
      return { ...state, currentQuestionIndex: action.payload };
    
    case ACTIONS.SET_INTERVIEW_ACTIVE:
      return { ...state, isInterviewActive: action.payload };
    
    case ACTIONS.SET_INTERVIEW_COMPLETED:
      return { ...state, isInterviewCompleted: action.payload };
    
    case ACTIONS.UPDATE_METRICS:
      return { 
        ...state, 
        metrics: { ...state.metrics, ...action.payload }
      };
    
    case ACTIONS.SET_VIDEO_STREAM:
      return { ...state, videoStream: action.payload };
    
    case ACTIONS.SET_AUDIO_STREAM:
      return { ...state, audioStream: action.payload };
    
    case ACTIONS.SET_LOADING:
      return { ...state, isLoading: action.payload };
    
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload };
    
    case ACTIONS.SET_FINAL_RESULTS:
      return { ...state, finalResults: action.payload };
    
    case ACTIONS.SET_SOCKET:
      return { ...state, socket: action.payload };
    
    case ACTIONS.SET_CONNECTED:
      return { ...state, isConnected: action.payload };
    
    case ACTIONS.RESET_STATE:
      return initialState;
    
    default:
      return state;
  }
}

// Provider component
export function InterviewProvider({ children }) {
  const [state, dispatch] = useReducer(interviewReducer, initialState);

  // Initialize socket connection
  useEffect(() => {
    const socket = io('http://localhost:5000', {
      transports: ['websocket'],
      autoConnect: false
    });

    socket.on('connect', () => {
      dispatch({ type: ACTIONS.SET_CONNECTED, payload: true });
      console.log('Connected to server');
    });

    socket.on('disconnect', () => {
      dispatch({ type: ACTIONS.SET_CONNECTED, payload: false });
      console.log('Disconnected from server');
    });

    socket.on('metrics_update', (data) => {
      dispatch({ type: ACTIONS.UPDATE_METRICS, payload: data.metrics });
    });

    socket.on('error', (error) => {
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Connection error: ' + error.message);
    });

    dispatch({ type: ACTIONS.SET_SOCKET, payload: socket });

    return () => {
      socket.disconnect();
    };
  }, []);

  // API functions
  const api = {
    // Health check
    checkHealth: async () => {
      try {
        const response = await axios.get('/api/health');
        return response.data;
      } catch (error) {
        console.error('Health check failed:', error);
        throw error;
      }
    },

    // Authentication
    login: async (username, password) => {
      try {
        const response = await axios.post('/api/auth/login', {
          username,
          password
        }, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },

    register: async (username, email, password) => {
      try {
        const response = await axios.post('/api/auth/register', {
          username,
          email,
          password
        }, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Registration failed:', error);
        throw error;
      }
    },

    logout: async () => {
      try {
        const response = await axios.post('/api/auth/logout', {}, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Logout failed:', error);
        throw error;
      }
    },

    getCurrentUser: async () => {
      try {
        const response = await axios.get('/api/auth/me', {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Get user failed:', error);
        throw error;
      }
    },

    // Upload resume
    uploadResume: async (file) => {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      try {
        const formData = new FormData();
        formData.append('resume', file);

        const response = await axios.post('/api/upload-resume', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        return response.data;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to upload resume: ' + error.message);
        throw error;
      }
    },

    // Start interview
    startInterview: async (candidateName, questions) => {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      try {
        const response = await axios.post('/api/start-interview', {
          candidate_name: candidateName,
          questions: questions
        });

        const { session_id } = response.data;
        dispatch({ type: ACTIONS.SET_SESSION_ID, payload: session_id });
        dispatch({ type: ACTIONS.SET_CANDIDATE_NAME, payload: candidateName });
        dispatch({ type: ACTIONS.SET_QUESTIONS, payload: questions });
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });

        // Join socket room
        if (state.socket) {
          state.socket.emit('join_session', { session_id });
        }

        toast.success('Interview session started!');
        return response.data;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to start interview: ' + error.message);
        throw error;
      }
    },

    // Process video frame
    processFrame: async (frameData) => {
      if (!state.sessionId) return;

      try {
        const response = await axios.post('/api/process-frame', {
          session_id: state.sessionId,
          frame_data: frameData
        });

        return response.data;
      } catch (error) {
        console.error('Frame processing error:', error);
        // Don't show toast for frame processing errors as they're frequent
      }
    },

    // Process audio
    processAudio: async (audioData) => {
      if (!state.sessionId) return;

      try {
        const response = await axios.post('/api/process-audio', {
          session_id: state.sessionId,
          audio_data: audioData
        });

        return response.data;
      } catch (error) {
        console.error('Audio processing error:', error);
      }
    },

    // End interview
    endInterview: async () => {
      if (!state.sessionId) return;

      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      try {
        const response = await axios.post(`/api/end-interview/${state.sessionId}`);
        
        dispatch({ type: ACTIONS.SET_FINAL_RESULTS, payload: response.data.final_report });
        dispatch({ type: ACTIONS.SET_INTERVIEW_COMPLETED, payload: true });
        dispatch({ type: ACTIONS.SET_INTERVIEW_ACTIVE, payload: false });
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });

        toast.success('Interview completed successfully!');
        return response.data;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to end interview: ' + error.message);
        throw error;
      }
    },

    // Get session details
    getSessionDetails: async (sessionId) => {
      try {
        const response = await axios.get(`/api/sessions/${sessionId}`);
        return response.data;
      } catch (error) {
        console.error('Failed to get session details:', error);
        throw error;
      }
    },

    // Get all sessions
    getAllSessions: async () => {
      try {
        const response = await axios.get('/api/sessions');
        return response.data;
      } catch (error) {
        console.error('Failed to get sessions:', error);
        throw error;
      }
    }
  };

  // Utility functions
  const utils = {
    // Get current question
    getCurrentQuestion: () => {
      return state.questions[state.currentQuestionIndex] || null;
    },

    // Move to next question
    nextQuestion: () => {
      if (state.currentQuestionIndex < state.questions.length - 1) {
        dispatch({ 
          type: ACTIONS.SET_CURRENT_QUESTION, 
          payload: state.currentQuestionIndex + 1 
        });
        return true;
      }
      return false;
    },

    // Move to previous question
    previousQuestion: () => {
      if (state.currentQuestionIndex > 0) {
        dispatch({ 
          type: ACTIONS.SET_CURRENT_QUESTION, 
          payload: state.currentQuestionIndex - 1 
        });
        return true;
      }
      return false;
    },

    // Reset state
    resetState: () => {
      dispatch({ type: ACTIONS.RESET_STATE });
    },

    // Connect socket
    connectSocket: () => {
      if (state.socket && !state.isConnected) {
        state.socket.connect();
      }
    },

    // Disconnect socket
    disconnectSocket: () => {
      if (state.socket && state.isConnected) {
        state.socket.disconnect();
      }
    }
  };

  const value = {
    ...state,
    api,
    utils,
    dispatch
  };

  return (
    <InterviewContext.Provider value={value}>
      {children}
    </InterviewContext.Provider>
  );
}

// Custom hook to use the context
export function useInterview() {
  const context = useContext(InterviewContext);
  if (!context) {
    throw new Error('useInterview must be used within an InterviewProvider');
  }
  return context;
}