import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  User, 
  Play, 
  CheckCircle, 
  AlertCircle,
  Loader,
  Camera,
  Mic
} from 'lucide-react';
import { useInterview } from '../context/InterviewContext';
import toast from 'react-hot-toast';

const InterviewSetup = () => {
  const navigate = useNavigate();
  const { api, isLoading } = useInterview();
  
  const [step, setStep] = useState(1);
  const [candidateName, setCandidateName] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  // Check authentication
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      toast.error('Please login to start an interview');
      navigate('/login');
      return;
    }
    
    // Set candidate name from user
    try {
      const user = JSON.parse(userStr);
      if (user.username && !candidateName) {
        setCandidateName(user.username);
      }
    } catch (e) {
      console.error('Error parsing user data:', e);
    }
  }, [navigate, candidateName]);

  // Debug logging
  console.log('InterviewSetup render - candidateName:', candidateName, 'step:', step);

  // Dropzone for resume upload
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setResumeFile(file);
      toast.success('Resume uploaded successfully!');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxFiles: 1
  });

  // Handle resume upload and processing
  const handleResumeUpload = async () => {
    if (!resumeFile) {
      toast.error('Please upload a resume first');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await api.uploadResume(resumeFile);
      setResumeData(result.resume_data);
      setQuestions(result.questions);
      setStep(2);
      toast.success('Resume processed successfully!');
    } catch (error) {
      toast.error('Failed to process resume');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle question selection
  const toggleQuestion = (question) => {
    setSelectedQuestions(prev => {
      const isSelected = prev.find(q => q.question === question.question);
      if (isSelected) {
        return prev.filter(q => q.question !== question.question);
      } else {
        return [...prev, question];
      }
    });
  };

  // Start interview
  const handleStartInterview = async () => {
    if (!candidateName.trim()) {
      toast.error('Please enter your name');
      return;
    }

    if (selectedQuestions.length === 0) {
      toast.error('Please select at least one question');
      return;
    }

    try {
      await api.startInterview(candidateName, selectedQuestions);
      navigate('/interview');
    } catch (error) {
      toast.error('Failed to start interview');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Interview Setup
            </h1>
            <p className="text-gray-600">
              Upload your resume and configure your interview session
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2, 3].map((stepNumber) => (
                <div key={stepNumber} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold ${
                    step >= stepNumber 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {stepNumber}
                  </div>
                  {stepNumber < 3 && (
                    <div className={`w-16 h-1 mx-2 ${
                      step > stepNumber ? 'bg-blue-600' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step 1: Resume Upload */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Step 1: Upload Your Resume
                </h2>
                <p className="text-gray-600 mb-6">
                  Upload your resume to get personalized interview questions based on your experience and skills.
                </p>
              </div>

              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
                  isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-blue-600 font-medium">Drop your resume here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag & drop your resume here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports PDF, DOC, DOCX files
                    </p>
                  </div>
                )}
              </div>

              {resumeFile && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-green-800 font-medium">
                      {resumeFile.name}
                    </span>
                  </div>
                </div>
              )}

              <div className="flex justify-end">
                <button
                  onClick={handleResumeUpload}
                  disabled={!resumeFile || isProcessing}
                  className="btn-primary flex items-center"
                >
                  {isProcessing ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Process Resume
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Question Selection */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Step 2: Select Interview Questions
                </h2>
                <p className="text-gray-600 mb-6">
                  Choose the questions you'd like to be asked during your interview. You can select multiple questions.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                {questions.map((question, index) => (
                  <div
                    key={index}
                    onClick={() => toggleQuestion(question)}
                    className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedQuestions.find(q => q.question === question.question)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedQuestions.find(q => q.question === question.question) !== undefined}
                        onChange={() => {}}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 mb-1">
                          {question.question}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            question.category === 'technical' ? 'bg-blue-100 text-blue-800' :
                            question.category === 'behavioral' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {question.category}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                            question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {question.difficulty}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setStep(1)}
                  className="btn-secondary"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={selectedQuestions.length === 0}
                  className="btn-primary"
                >
                  Continue
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Final Setup */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Step 3: Final Setup
                </h2>
                <p className="text-gray-600 mb-6">
                  Enter your name and review your interview configuration.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={candidateName}
                    onChange={(e) => {
                      console.log('Input value:', e.target.value); // Debug log
                      setCandidateName(e.target.value);
                    }}
                    placeholder="Enter your full name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
                    style={{ color: '#111827' }} // Force text color
                  />
                  {/* Debug display */}
                  <p className="text-xs text-gray-500 mt-1">
                    Current value: "{candidateName}" (Length: {candidateName.length})
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Interview Summary</h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p><strong>Questions Selected:</strong> {selectedQuestions.length}</p>
                    <p><strong>Categories:</strong> {[...new Set(selectedQuestions.map(q => q.category))].join(', ')}</p>
                    <p><strong>Resume:</strong> {resumeFile?.name}</p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900 mb-1">Before you start:</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Ensure you have a working webcam and microphone</li>
                        <li>• Find a quiet, well-lit environment</li>
                        <li>• Make sure your face is clearly visible</li>
                        <li>• Speak clearly and maintain eye contact</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setStep(2)}
                  className="btn-secondary"
                >
                  Back
                </button>
                <button
                  onClick={handleStartInterview}
                  disabled={!candidateName.trim() || isLoading}
                  className="btn-primary flex items-center"
                >
                  {isLoading ? (
                    <>
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      Start Interview
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default InterviewSetup;