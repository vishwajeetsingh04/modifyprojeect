import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Camera, 
  Mic, 
  Brain, 
  BarChart3, 
  Users, 
  Clock, 
  CheckCircle, 
  ArrowRight,
  Play,
  Upload,
  Eye,
  MessageSquare
} from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const userStr = localStorage.getItem('user');
    setIsAuthenticated(!!userStr);
  }, []);

  const handleStartInterview = () => {
    if (!isAuthenticated) {
      navigate('/login');
    } else {
      navigate('/setup');
    }
  };

  const features = [
    {
      icon: <Camera className="w-8 h-8" />,
      title: "Real-time Face Detection",
      description: "Advanced computer vision technology monitors eye contact and facial expressions during interviews."
    },
    {
      icon: <Mic className="w-8 h-8" />,
      title: "Speech Analysis",
      description: "AI-powered speech recognition analyzes clarity, tone, and detects filler words in real-time."
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "Emotion Recognition",
      description: "Machine learning algorithms identify emotions and confidence levels from facial expressions."
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Performance Analytics",
      description: "Comprehensive scoring and detailed feedback on interview performance metrics."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Personalized Questions",
      description: "AI generates customized interview questions based on your uploaded resume."
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: "Real-time Feedback",
      description: "Instant warnings and suggestions to improve your interview performance."
    }
  ];

  const benefits = [
    "Improve interview confidence and skills",
    "Get unbiased, objective feedback",
    "Practice with personalized questions",
    "Track your progress over time",
    "Save time and resources",
    "Prepare for real interviews effectively"
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 text-white">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <motion.h1 
              className="text-5xl md:text-7xl font-bold mb-6"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              AI-Powered Interview
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400">
                Assessment System
              </span>
            </motion.h1>
            
            <motion.p 
              className="text-xl md:text-2xl mb-8 text-blue-100"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Practice interviews with AI that monitors your performance in real-time.
              Get personalized feedback to improve your interview skills.
            </motion.p>
            
            <motion.div 
              className="flex flex-col sm:flex-row gap-4 justify-center"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <button
                onClick={handleStartInterview}
                className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-all duration-300 transform hover:scale-105"
              >
                <Play className="w-5 h-5 mr-2" />
                Start Interview
              </button>
              {isAuthenticated ? (
                <Link 
                  to="/dashboard"
                  className="inline-flex items-center px-8 py-4 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-blue-600 transition-all duration-300"
                >
                  <BarChart3 className="w-5 h-5 mr-2" />
                  View Results
                </Link>
              ) : (
                <Link 
                  to="/login"
                  className="inline-flex items-center px-8 py-4 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-blue-600 transition-all duration-300"
                >
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Login to View Results
                </Link>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Advanced AI Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our system uses cutting-edge artificial intelligence to provide comprehensive interview assessment and feedback.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Simple steps to get started with your AI-powered interview practice
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div 
              className="text-center"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Resume</h3>
              <p className="text-gray-600">
                Upload your resume to get personalized interview questions based on your experience and skills.
              </p>
            </motion.div>
            
            <motion.div 
              className="text-center"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="w-20 h-20 bg-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Start Interview</h3>
              <p className="text-gray-600">
                Begin your interview session with AI monitoring your face, voice, and responses in real-time.
              </p>
            </motion.div>
            
            <motion.div 
              className="text-center"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="w-20 h-20 bg-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Feedback</h3>
              <p className="text-gray-600">
                Receive comprehensive analysis and detailed feedback to improve your interview performance.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Why Choose Our AI Interview System?
              </h2>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.li 
                    key={index}
                    className="flex items-center text-lg text-gray-700"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <CheckCircle className="w-6 h-6 text-green-500 mr-3 flex-shrink-0" />
                    {benefit}
                  </motion.li>
                ))}
              </ul>
            </motion.div>
            
            <motion.div
              className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-8 text-white"
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h3 className="text-2xl font-bold mb-4">Ready to Improve Your Interview Skills?</h3>
              <p className="text-blue-100 mb-6">
                Join thousands of candidates who have improved their interview performance with our AI-powered system.
              </p>
              <button
                onClick={handleStartInterview}
                className="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-all duration-300"
              >
                Get Started Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Developed by Team Code Force
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Graphic Era Hill University, Dehradun
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              'Bhumika Gupta',
              'Vishwajeet Singh',
              'Vandana Rautela',
              'Sneha Thapliyal'
            ].map((member, index) => (
              <motion.div
                key={index}
                className="p-4 bg-white rounded-lg shadow-sm"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold mx-auto mb-3">
                  {member.split(' ').map(n => n[0]).join('')}
                </div>
                <p className="font-medium text-gray-900">{member}</p>
                <p className="text-sm text-gray-600">7th Semester B.Tech CSE</p>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-8 text-gray-600">
            <p>Supervised by Dr. Seema Gulati</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;