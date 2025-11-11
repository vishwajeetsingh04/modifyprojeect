import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  Mic, 
  MicOff, 
  Eye, 
  Brain, 
  BarChart3, 
  AlertTriangle,
  CheckCircle,
  X,
  Play,
  Pause,
  SkipForward,
  SkipBack,
  Square,
  Volume2,
  VolumeX
} from 'lucide-react';
import { useInterview } from '../context/InterviewContext';
import toast from 'react-hot-toast';

const InterviewRoom = () => {
  const navigate = useNavigate();
  const { 
    sessionId, 
    candidateName, 
    questions, 
    currentQuestionIndex,
    metrics,
    api,
    utils,
    isLoading,
    isInterviewActive,
    isInterviewCompleted,
    dispatch
  } = useInterview();

  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [interviewTime, setInterviewTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [showWarnings, setShowWarnings] = useState(false);
  const [warningMessages, setWarningMessages] = useState([]);

  // Check if we have session data
  useEffect(() => {
    if (!sessionId || !questions.length) {
      navigate('/setup');
      return;
    }
  }, [sessionId, questions, navigate]);

  // Start interview timer
  useEffect(() => {
    if (isInterviewActive && !isPaused) {
      const timer = setInterval(() => {
        setInterviewTime(prev => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isInterviewActive, isPaused]);

  // Process video frames
  const processFrame = useCallback(async () => {
    if (webcamRef.current && isVideoEnabled && isInterviewActive) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        await api.processFrame(imageSrc);
      }
    }
  }, [api, isVideoEnabled, isInterviewActive]);

  // Process frames at regular intervals
  useEffect(() => {
    const interval = setInterval(processFrame, 1000); // Process every second
    return () => clearInterval(interval);
  }, [processFrame]);

  // Start interview
  const startInterview = () => {
    if (dispatch) {
      dispatch({ type: 'SET_INTERVIEW_ACTIVE', payload: true });
    }
    toast.success('Interview started!');
  };

  // End interview
  const endInterview = async () => {
    if (window.confirm('Are you sure you want to end the interview?')) {
      try {
        await api.endInterview();
        navigate('/results');
      } catch (error) {
        toast.error('Failed to end interview');
      }
    }
  };

  // Toggle video
  const toggleVideo = () => {
    setIsVideoEnabled(!isVideoEnabled);
    toast.success(isVideoEnabled ? 'Video disabled' : 'Video enabled');
  };

  // Toggle audio
  const toggleAudio = () => {
    setIsAudioEnabled(!isAudioEnabled);
    toast.success(isAudioEnabled ? 'Audio disabled' : 'Audio enabled');
  };

  // Toggle pause
  const togglePause = () => {
    setIsPaused(!isPaused);
    toast.success(isPaused ? 'Interview resumed' : 'Interview paused');
  };

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get current question
  const currentQuestion = utils?.getCurrentQuestion ? utils.getCurrentQuestion() : questions[currentQuestionIndex];

  // Get performance color
  const getPerformanceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get performance status
  const getPerformanceStatus = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  // Analyze metrics and generate warnings
  const analyzeWarnings = useCallback(() => {
    const warnings = [];
    
    // First priority: Check if face detection is working
    if (!metrics?.face_detected) {
      warnings.push({
        type: 'error',
        message: 'No face detected! Please position yourself in front of the camera.',
        icon: '👤',
        priority: 1,
        category: 'detection'
      });
      
      // If no face detected, don't show other warnings - just focus on getting face detected
      setWarningMessages(warnings);
      return;
    }
    
    // Second priority: Check if eyes are visible (basic face detection passed)
    if (metrics.face_detected && metrics.eyeContactPercentage === 0) {
      warnings.push({
        type: 'error',
        message: 'Eyes not visible! Please look directly at the camera.',
        icon: '👁️',
        priority: 2,
        category: 'detection'
      });
      
      // If eyes not visible, only show detection warnings
      setWarningMessages(warnings);
      return;
    }
    
    // Third priority: Basic face analysis (face and eyes detected)
    if (metrics.face_detected && metrics.eyeContactPercentage > 0) {
      // Show basic detection success
      warnings.push({
        type: 'success',
        message: 'Face and eyes detected successfully!',
        icon: '✅',
        priority: 0,
        category: 'detection'
      });
      
      // Now analyze performance metrics
      if (metrics.eyeContactPercentage < 30) {
        warnings.push({
          type: 'error',
          message: 'Low eye contact detected. Try to look at the camera more.',
          icon: '👁️',
          priority: 3,
          category: 'performance'
        });
      } else if (metrics.eyeContactPercentage < 50) {
        warnings.push({
          type: 'warning',
          message: 'Eye contact could be improved. Focus on the camera.',
          icon: '👁️',
          priority: 4,
          category: 'performance'
        });
      } else {
        warnings.push({
          type: 'success',
          message: 'Good eye contact maintained!',
          icon: '👁️',
          priority: 0,
          category: 'performance'
        });
      }
      
      // Check confidence score
      if (metrics.confidenceScore < 0.4) {
        warnings.push({
          type: 'error',
          message: 'Low confidence detected. Try to sit up straight and maintain good posture.',
          icon: '💪',
          priority: 3,
          category: 'performance'
        });
      } else if (metrics.confidenceScore < 0.6) {
        warnings.push({
          type: 'warning',
          message: 'Confidence could be improved. Maintain better posture.',
          icon: '💪',
          priority: 4,
          category: 'performance'
        });
      } else {
        warnings.push({
          type: 'success',
          message: 'Good confidence and posture!',
          icon: '💪',
          priority: 0,
          category: 'performance'
        });
      }
      
      // Check speech clarity
      if (metrics.speechClarity < 0.6) {
        warnings.push({
          type: 'error',
          message: 'Speech clarity needs improvement. Speak more clearly and slowly.',
          icon: '🗣️',
          priority: 3,
          category: 'performance'
        });
      } else if (metrics.speechClarity < 0.8) {
        warnings.push({
          type: 'warning',
          message: 'Speech clarity could be improved.',
          icon: '🗣️',
          priority: 4,
          category: 'performance'
        });
      } else {
        warnings.push({
          type: 'success',
          message: 'Excellent speech clarity!',
          icon: '🗣️',
          priority: 0,
          category: 'performance'
        });
      }
      
      // Check for negative emotions
      if (metrics.emotionScores) {
        const negativeEmotions = ['angry', 'sad', 'fear', 'disgust'];
        let hasNegativeEmotion = false;
        
        negativeEmotions.forEach(emotion => {
          if (metrics.emotionScores[emotion] > 0.5) {
            hasNegativeEmotion = true;
            warnings.push({
              type: 'warning',
              message: `Detected ${emotion} expression. Try to maintain a positive demeanor.`,
              icon: '😊',
              priority: 4,
              category: 'emotion'
            });
          }
        });
        
        if (!hasNegativeEmotion) {
          warnings.push({
            type: 'success',
            message: 'Positive emotional state detected!',
            icon: '😊',
            priority: 0,
            category: 'emotion'
          });
        }
      }
    }
    
    // Sort warnings by priority (0 = success, 1 = highest priority error)
    warnings.sort((a, b) => a.priority - b.priority);
    setWarningMessages(warnings);
  }, [metrics]);

  // Get face detection status
  const getFaceDetectionStatus = () => {
    if (!metrics?.face_detected) {
      return {
        status: 'no-face',
        text: 'No Face Detected',
        color: 'text-red-500',
        bgColor: 'bg-red-500/20',
        icon: '👤'
      };
    }
    
    if (metrics.eyeContactPercentage === 0) {
      return {
        status: 'no-eyes',
        text: 'Eyes Not Visible',
        color: 'text-orange-500',
        bgColor: 'bg-orange-500/20',
        icon: '👁️'
      };
    }
    
    return {
      status: 'face-detected',
      text: 'Face Detected',
      color: 'text-green-500',
      bgColor: 'bg-green-500/20',
      icon: '✅'
    };
  };

  const faceStatus = getFaceDetectionStatus();

  // Update warnings when metrics change
  useEffect(() => {
    if (isInterviewActive) {
      analyzeWarnings();
    }
  }, [analyzeWarnings, isInterviewActive]);

  // Auto-hide warnings after 5 seconds for better UX
  useEffect(() => {
    if (warningMessages.length > 0) {
      const timer = setTimeout(() => {
        setWarningMessages(prev => prev.slice(0, 2)); // Keep only 2 most important warnings
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [warningMessages]);

  // Demo mode: Generate sample warnings for testing (remove in production)
  useEffect(() => {
    if (isInterviewActive && interviewTime > 5 && warningMessages.length === 0) {
      // Simulate progressive detection warnings for demo purposes
      const demoWarnings = [
        {
          type: 'error',
          message: 'No face detected! Please position yourself in front of the camera.',
          icon: '👤',
          priority: 1,
          category: 'detection'
        }
      ];
      setWarningMessages(demoWarnings);
      
      // After 3 seconds, simulate eyes not visible
      setTimeout(() => {
        if (warningMessages.length === 1 && warningMessages[0].priority === 1) {
          setWarningMessages([
            {
              type: 'error',
              message: 'Eyes not visible! Please look directly at the camera.',
              icon: '👁️',
              priority: 2,
              category: 'detection'
            }
          ]);
        }
      }, 3000);
      
      // After 6 seconds, simulate successful detection and show performance warnings
      setTimeout(() => {
        if (warningMessages.length === 1 && warningMessages[0].priority === 2) {
          setWarningMessages([
            {
              type: 'success',
              message: 'Face and eyes detected successfully!',
              icon: '✅',
              priority: 0,
              category: 'detection'
            },
            {
              type: 'warning',
              message: 'Eye contact could be improved. Focus on the camera.',
              icon: '👁️',
              priority: 4,
              category: 'performance'
            },
            {
              type: 'success',
              message: 'Good confidence and posture!',
              icon: '💪',
              priority: 0,
              category: 'performance'
            }
          ]);
        }
      }, 6000);
    }
  }, [isInterviewActive, interviewTime, warningMessages.length]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="text-white">
            <h1 className="text-2xl font-bold">Interview Session</h1>
            <p className="text-blue-100">Candidate: {candidateName}</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 text-white">
              <span className="text-sm">Time: {formatTime(interviewTime)}</span>
            </div>
            
            {/* Interview Status Indicator */}
            <div className={`px-3 py-2 rounded-lg backdrop-blur-sm flex items-center space-x-2 status-indicator ${
              warningMessages.length === 0 
                ? 'bg-green-500/20 text-green-100' 
                : warningMessages.some(w => w.type === 'error')
                ? 'bg-red-500/20 text-red-100'
                : 'bg-yellow-500/20 text-yellow-100'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                warningMessages.length === 0 
                  ? 'bg-green-400' 
                  : warningMessages.some(w => w.type === 'error')
                  ? 'bg-red-400'
                  : 'bg-yellow-400'
              }`}></div>
              <span className="text-sm font-medium">
                {warningMessages.length === 0 
                  ? 'All Good' 
                  : warningMessages.some(w => w.type === 'error')
                  ? 'Critical Issues'
                  : 'Needs Attention'
                }
              </span>
            </div>
            
            {/* Face Detection Status Indicator */}
            <div className={`px-3 py-2 rounded-lg backdrop-blur-sm flex items-center space-x-2 ${faceStatus.bgColor} ${
              faceStatus.status === 'no-face' ? 'face-status-no-face' :
              faceStatus.status === 'no-eyes' ? 'face-status-no-eyes' :
              'face-status-detected'
            }`}>
              <span className="text-lg">{faceStatus.icon}</span>
              <span className={`text-sm font-medium ${faceStatus.color}`}>
                {faceStatus.text}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={togglePause}
                className="p-2 bg-white/10 backdrop-blur-sm rounded-lg text-white hover:bg-white/20 transition-colors"
              >
                {isPaused ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
              </button>
              
              <button
                onClick={endInterview}
                className="p-2 bg-red-500 rounded-lg text-white hover:bg-red-600 transition-colors"
              >
                <Square className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Interview Area */}
          <div className="lg:col-span-2 space-y-6">
                       {/* Webcam */}
                       <div className="relative">
               <div className="webcam-container">
                 {isVideoEnabled ? (
                   <Webcam
                     ref={webcamRef}
                     audio={false}
                     screenshotFormat="image/jpeg"
                     className="w-full h-96 object-cover rounded-lg"
                   />
                 ) : (
                   <div className="w-full h-96 bg-gray-800 rounded-lg flex items-center justify-center">
                     <div className="text-center text-white">
                       <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                       <p>Camera Disabled</p>
                     </div>
                   </div>
                 )}
                 
                 {!isInterviewActive && (
                   <div className="webcam-overlay">
                     <div className="text-center">
                       <p className="mb-4">Ready to start your interview?</p>
                       <button
                         onClick={startInterview}
                         className="btn-primary"
                       >
                         Start Interview
                       </button>
                     </div>
                   </div>
                 )}

                 {/* Detection Progress Indicator */}
                 {isInterviewActive && (
                   <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
                     <div className="bg-black/50 backdrop-blur-sm rounded-lg px-4 py-2 text-white">
                       <div className="flex items-center space-x-3">
                         <div className={`w-3 h-3 rounded-full ${
                           metrics?.face_detected ? 'bg-green-400' : 'bg-red-400'
                         } ${!metrics?.face_detected ? 'animate-pulse' : ''}`}></div>
                         <span className="text-sm font-medium">Face Detection</span>
                         
                         <div className="w-px h-4 bg-white/30"></div>
                         
                         <div className={`w-3 h-3 rounded-full ${
                           metrics?.face_detected && metrics?.eyeContactPercentage > 0 ? 'bg-green-400' : 'bg-orange-400'
                         } ${metrics?.face_detected && metrics?.eyeContactPercentage === 0 ? 'animate-pulse' : ''}`}></div>
                         <span className="text-sm font-medium">Eye Detection</span>
                         
                         <div className="w-px h-4 bg-white/30"></div>
                         
                         <div className={`w-3 h-3 rounded-full ${
                           metrics?.face_detected && metrics?.eyeContactPercentage > 0 ? 'bg-green-400' : 'bg-gray-400'
                         }`}></div>
                         <span className="text-sm font-medium">Analysis</span>
                       </div>
                     </div>
                   </div>
                 )}

                 {/* Real-time Warnings Overlay */}
                 {isInterviewActive && warningMessages.length > 0 && (
                   <div className="absolute top-4 right-4 z-20 space-y-2 max-w-sm">
                     {warningMessages.slice(0, 3).map((warning, index) => (
                       <motion.div
                         key={index}
                         initial={{ opacity: 0, x: 100, scale: 0.8 }}
                         animate={{ opacity: 1, x: 0, scale: 1 }}
                         exit={{ opacity: 0, x: 100, scale: 0.8 }}
                         transition={{ duration: 0.3, delay: index * 0.1 }}
                         className={`p-3 rounded-lg backdrop-blur-md border-l-4 shadow-xl ${
                           warning.type === 'success'
                           ? 'bg-green-500/95 text-white border-green-600' 
                           : warning.type === 'error' 
                           ? 'bg-red-500/95 text-white border-red-600' 
                           : warning.type === 'warning'
                           ? 'bg-yellow-500/95 text-white border-yellow-600'
                           : 'bg-blue-500/95 text-white border-blue-600'
                         }`}
                       >
                         <div className="flex items-start space-x-2">
                           <span className="text-lg flex-shrink-0">{warning.icon}</span>
                           <div className="flex-1 min-w-0">
                             <p className="text-sm font-medium leading-tight">{warning.message}</p>
                             <div className="flex items-center space-x-2 mt-1">
                               <span className={`text-xs px-2 py-1 rounded-full ${
                                 warning.priority === 0 ? 'bg-green-600/50' :
                                 warning.priority === 1 ? 'bg-red-600/50' :
                                 warning.priority === 2 ? 'bg-orange-600/50' :
                                 warning.priority === 3 ? 'bg-yellow-600/50' :
                                 'bg-blue-600/50'
                               }`}>
                                 {warning.priority === 0 ? 'Success' : `Priority ${warning.priority}`}
                               </span>
                               <span className="text-xs px-2 py-1 rounded-full bg-white/20">
                                 {warning.category}
                               </span>
                               <span className="text-xs opacity-75">
                                 {warning.type === 'success' ? 'Good Job!' :
                                  warning.type === 'error' ? 'Critical' : 
                                  warning.type === 'warning' ? 'Important' : 'Info'}
                               </span>
                             </div>
                           </div>
                           <button
                             onClick={() => setWarningMessages(prev => prev.filter((_, i) => i !== index))}
                             className="text-white/80 hover:text-white ml-2 flex-shrink-0"
                           >
                             <X className="w-4 h-4" />
                           </button>
                         </div>
                       </motion.div>
                     ))}
                   </div>
                 )}
               </div>

              {/* Camera Controls */}
              <div className="absolute bottom-4 left-4 flex space-x-2">
                <button
                  onClick={toggleVideo}
                  className={`p-2 rounded-lg backdrop-blur-sm transition-colors ${
                    isVideoEnabled 
                      ? 'bg-white/20 text-white' 
                      : 'bg-red-500 text-white'
                  }`}
                >
                  <Camera className="w-5 h-5" />
                </button>
                
                <button
                  onClick={toggleAudio}
                  className={`p-2 rounded-lg backdrop-blur-sm transition-colors ${
                    isAudioEnabled 
                      ? 'bg-white/20 text-white' 
                      : 'bg-red-500 text-white'
                  }`}
                >
                  {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Current Question */}
            {currentQuestion && (
              <motion.div
                key={currentQuestionIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="question-card"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="text-sm opacity-75">Question {currentQuestionIndex + 1} of {questions.length}</span>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        currentQuestion.category === 'technical' ? 'bg-blue-500/20' :
                        currentQuestion.category === 'behavioral' ? 'bg-green-500/20' :
                        'bg-gray-500/20'
                      }`}>
                        {currentQuestion.category}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        currentQuestion.difficulty === 'easy' ? 'bg-green-500/20' :
                        currentQuestion.difficulty === 'medium' ? 'bg-yellow-500/20' :
                        'bg-red-500/20'
                      }`}>
                        {currentQuestion.difficulty}
                      </span>
                    </div>
                  </div>
                </div>
                
                <h3 className="text-xl font-semibold mb-4">
                  {currentQuestion.question}
                </h3>
                
                <div className="flex justify-between">
                  <button
                    onClick={() => utils.previousQuestion()}
                    disabled={currentQuestionIndex === 0}
                    className="flex items-center px-4 py-2 bg-white/20 rounded-lg text-white hover:bg-white/30 transition-colors disabled:opacity-50"
                  >
                    <SkipBack className="w-4 h-4 mr-2" />
                    Previous
                  </button>
                  
                  <button
                    onClick={() => utils.nextQuestion()}
                    disabled={currentQuestionIndex === questions.length - 1}
                    className="flex items-center px-4 py-2 bg-white/20 rounded-lg text-white hover:bg-white/30 transition-colors disabled:opacity-50"
                  >
                    Next
                    <SkipForward className="w-4 h-4 ml-2" />
                  </button>
                </div>
              </motion.div>
            )}
          </div>

          {/* Metrics Panel */}
          <div className="space-y-6">
            {/* Face Detection Status */}
            <div className="metrics-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-2">{faceStatus.icon}</span>
                Face Detection Status
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Status</span>
                  <span className={`text-sm font-semibold ${faceStatus.color}`}>
                    {faceStatus.text}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Face Detected</span>
                  <span className={`text-sm font-semibold ${
                    metrics?.face_detected ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metrics?.face_detected ? 'Yes' : 'No'}
                  </span>
                </div>
                
                {metrics?.face_detected && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Landmarks</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {metrics?.landmarks || 0}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Eye Contact</span>
                      <span className={`text-sm font-semibold ${
                        metrics?.eyeContactPercentage > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metrics?.eyeContactPercentage > 0 ? 'Detected' : 'Not Detected'}
                      </span>
                    </div>
                  </>
                )}
                
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      faceStatus.status === 'face-detected' ? 'bg-green-600' :
                      faceStatus.status === 'no-eyes' ? 'bg-orange-600' :
                      'bg-red-600'
                    }`}
                    style={{ 
                      width: faceStatus.status === 'face-detected' ? '100%' :
                             faceStatus.status === 'no-eyes' ? '50%' : '0%'
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Real-time Metrics */}
            <div className="metrics-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Real-time Metrics
              </h3>
              
              <div className="space-y-4">
                {/* Eye Contact */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Eye Contact</span>
                    <span className={`text-sm font-semibold ${getPerformanceColor(metrics.eyeContactPercentage)}`}>
                      {Math.round(metrics.eyeContactPercentage)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${metrics.eyeContactPercentage}%` }}
                    />
                  </div>
                </div>

                {/* Confidence Score */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Confidence</span>
                    <span className={`text-sm font-semibold ${getPerformanceColor(metrics.confidenceScore * 100)}`}>
                      {Math.round(metrics.confidenceScore * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${metrics.confidenceScore * 100}%` }}
                    />
                  </div>
                </div>

                {/* Speech Clarity */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Speech Clarity</span>
                    <span className={`text-sm font-semibold ${getPerformanceColor(metrics.speechClarity * 100)}`}>
                      {Math.round(metrics.speechClarity * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${metrics.speechClarity * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

         {/* Warnings */}
         <div className="metrics-card p-6">
               <div className="flex items-center justify-between mb-4">
                 <div className="flex items-center space-x-2">
                   <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                     <AlertTriangle className="w-5 h-5 mr-2 text-red-500" />
                     Live Warnings
                   </h3>
                   <div className="group relative">
                     <div className="w-4 h-4 bg-gray-300 rounded-full flex items-center justify-center cursor-help">
                       <span className="text-xs text-gray-600">?</span>
                     </div>
                     <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-20">
                       <div className="mb-1">
                         <span className="font-semibold">Priority System:</span>
                       </div>
                       <div>1: Critical (No face/eyes)</div>
                       <div>2: High (Basic issues)</div>
                       <div>3: Medium (Improvements needed)</div>
                       <div>4: Low (Minor suggestions)</div>
                       <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                     </div>
                   </div>
                 </div>
                 <div className="flex items-center space-x-2">
                   <span className={`px-2 py-1 text-xs rounded-full ${
                     warningMessages.length === 0 
                       ? 'bg-green-100 text-green-700' 
                       : warningMessages.some(w => w.priority === 1)
                       ? 'bg-red-100 text-red-700'
                       : 'bg-yellow-100 text-yellow-700'
                   }`}>
                     {warningMessages.length === 0 ? 'All Good' : 
                      warningMessages.some(w => w.priority === 1) ? 'Critical' : 'Warning'}
                   </span>
                   <button
                     onClick={() => setShowWarnings(!showWarnings)}
                     className={`px-3 py-1 text-xs rounded-full transition-colors ${
                       showWarnings 
                         ? 'bg-blue-100 text-blue-700' 
                         : 'bg-gray-100 text-gray-700'
                     }`}
                   >
                     {showWarnings ? 'Hide' : 'Show'}
                   </button>
                 </div>
               </div>
               
               {/* Warning Summary */}
               {warningMessages.length > 0 && (
                 <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                   <div className="flex items-center justify-between mb-2">
                     <span className="text-sm font-medium text-gray-700">Warning Summary</span>
                     <span className="text-sm text-gray-500">{warningMessages.length} total</span>
                   </div>
                   <div className="flex space-x-2">
                     {warningMessages.some(w => w.priority === 1) && (
                       <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full">
                         {warningMessages.filter(w => w.priority === 1).length} Critical
                       </span>
                     )}
                     {warningMessages.some(w => w.priority === 2) && (
                       <span className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full">
                         {warningMessages.filter(w => w.priority === 2).length} High
                       </span>
                     )}
                     {warningMessages.some(w => w.priority === 3) && (
                       <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full">
                         {warningMessages.filter(w => w.priority === 3).length} Medium
                       </span>
                     )}
                     {warningMessages.some(w => w.priority === 4) && (
                       <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                         {warningMessages.filter(w => w.priority === 4).length} Low
                       </span>
                     )}
                   </div>
                 </div>
               )}
               
               {showWarnings && (
                 <>
                   {warningMessages.length > 0 ? (
                     <div className="space-y-3">
                       {warningMessages.map((warning, index) => (
                         <motion.div
                           key={index}
                           initial={{ opacity: 0, y: 10 }}
                           animate={{ opacity: 1, y: 0 }}
                           className={`flex items-start space-x-3 p-3 rounded-lg border-l-4 ${
                             warning.type === 'success' ? 'success-message' :
                             warning.priority === 1 ? 'priority-1' :
                             warning.priority === 2 ? 'priority-2' :
                             warning.priority === 3 ? 'priority-3' :
                             'priority-4'
                           }`}
                         >
                           <span className="text-lg flex-shrink-0">{warning.icon}</span>
                           <div className="flex-1 min-w-0">
                             <p className={`text-sm font-medium ${
                               warning.type === 'success' ? 'text-green-800' :
                               warning.priority === 1 ? 'text-red-800' :
                               warning.priority === 2 ? 'text-orange-800' :
                               warning.priority === 3 ? 'text-yellow-800' :
                               'text-blue-800'
                             }`}>
                               {warning.message}
                             </p>
                             <div className="flex items-center space-x-2 mt-2">
                               <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                                 warning.priority === 0 ? 'bg-green-200 text-green-800' :
                                 warning.priority === 1 ? 'bg-red-200 text-red-800' :
                                 warning.priority === 2 ? 'bg-orange-200 text-orange-800' :
                                 warning.priority === 3 ? 'bg-yellow-200 text-yellow-800' :
                                 'bg-blue-200 text-blue-800'
                               }`}>
                                 {warning.priority === 0 ? 'Success' : `Priority ${warning.priority}`}
                               </span>
                               <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                                 {warning.category}
                               </span>
                               <span className={`text-xs px-2 py-1 rounded-full ${
                                 warning.type === 'success' ? 'bg-green-100 text-green-700' : 
                                 warning.type === 'error' ? 'bg-red-100 text-red-700' : 
                                 warning.type === 'warning' ? 'bg-yellow-100 text-yellow-700' : 
                                 'bg-blue-100 text-blue-700'
                               }`}>
                                 {warning.type === 'success' ? 'Excellent' : 
                                  warning.type === 'error' ? 'Critical' : 
                                  warning.type === 'warning' ? 'Important' : 'Info'}
                               </span>
                             </div>
                           </div>
                           <button
                             onClick={() => setWarningMessages(prev => prev.filter((_, i) => i !== index))}
                             className={`p-1 rounded hover:bg-white/50 transition-colors ${
                               warning.type === 'success' ? 'text-green-600 hover:text-green-700' :
                               warning.priority === 1 ? 'text-red-600 hover:text-red-700' :
                               warning.priority === 2 ? 'text-orange-600 hover:text-orange-700' :
                               warning.priority === 3 ? 'text-yellow-600 hover:text-yellow-700' :
                               'text-blue-600 hover:text-blue-700'
                             }`}
                           >
                             <X className="w-4 h-4" />
                           </button>
                         </motion.div>
                       ))}
                     </div>
                   ) : (
                     <div className="text-center py-6">
                       <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                       <p className="text-sm font-medium text-green-800 mb-1">No warnings detected</p>
                       <p className="text-xs text-green-600">Keep up the excellent work!</p>
                     </div>
                   )}
                 </>
               )}
               
               {!showWarnings && (
                 <div className="text-center py-4">
                   <p className="text-sm text-gray-500">
                     {warningMessages.length === 0 
                       ? 'All systems are working perfectly!' 
                       : `${warningMessages.length} warning${warningMessages.length !== 1 ? 's' : ''} detected`}
                   </p>
                 </div>
               )}
             </div>
            {/* Emotion Analysis */}
            {metrics.emotionScores && Object.keys(metrics.emotionScores).length > 0 && (
              <div className="metrics-card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  Emotion Analysis
                </h3>
                
                <div className="space-y-2">
                  {Object.entries(metrics.emotionScores).map(([emotion, score]) => (
                    <div key={emotion} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700 capitalize">{emotion}</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {Math.round(score * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Interview Progress */}
            <div className="metrics-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Questions Completed</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {currentQuestionIndex + 1} / {questions.length}
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                  />
                </div>
                
                <div className="text-center">
                  <span className="text-xs text-gray-500">
                    {Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}% Complete
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewRoom;