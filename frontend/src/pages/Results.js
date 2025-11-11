import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Eye, 
  Brain, 
  Mic, 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle,
  Download,
  Share2,
  ArrowLeft,
  Star,
  Clock,
  Target
} from 'lucide-react';
import { useInterview } from '../context/InterviewContext';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Results = () => {
  const { finalResults, candidateName, questions, utils } = useInterview();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (finalResults) {
      setIsLoading(false);
    } else {
      // If no results, redirect to home
      utils.resetState();
    }
  }, [finalResults, utils]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (!finalResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Results Found</h2>
          <p className="text-gray-600 mb-6">Please complete an interview to view results.</p>
          <Link to="/" className="btn-primary">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const {
    eye_contact_percentage,
    confidence_score,
    speech_clarity,
    overall_score,
    feedback
  } = finalResults;

  // Chart data for overall performance
  const overallChartData = {
    labels: ['Eye Contact', 'Confidence', 'Speech Clarity'],
    datasets: [
      {
        data: [
          eye_contact_percentage,
          confidence_score * 100,
          speech_clarity * 100
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(168, 85, 247, 0.8)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(168, 85, 247, 1)'
        ],
        borderWidth: 2,
      },
    ],
  };

  // Performance comparison data
  const comparisonData = {
    labels: ['Your Score', 'Average Score'],
    datasets: [
      {
        label: 'Overall Performance',
        data: [overall_score, 75], // Assuming average is 75%
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(156, 163, 175, 0.8)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(156, 163, 175, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed}%`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed}%`;
          }
        }
      }
    }
  };

  // Get performance level
  const getPerformanceLevel = (score) => {
    if (score >= 90) return { level: 'Excellent', color: 'text-green-600', icon: <Star className="w-5 h-5" /> };
    if (score >= 80) return { level: 'Very Good', color: 'text-blue-600', icon: <TrendingUp className="w-5 h-5" /> };
    if (score >= 70) return { level: 'Good', color: 'text-yellow-600', icon: <CheckCircle className="w-5 h-5" /> };
    if (score >= 60) return { level: 'Fair', color: 'text-orange-600', icon: <Target className="w-5 h-5" /> };
    return { level: 'Needs Improvement', color: 'text-red-600', icon: <AlertTriangle className="w-5 h-5" /> };
  };

  const performanceLevel = getPerformanceLevel(overall_score);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Interview Results
          </h1>
          <p className="text-xl text-gray-600">
            Performance analysis for {candidateName}
          </p>
        </motion.div>

        {/* Overall Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        >
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              {performanceLevel.icon}
              <span className={`ml-2 text-2xl font-bold ${performanceLevel.color}`}>
                {performanceLevel.level}
              </span>
            </div>
            
            <div className="text-6xl font-bold text-gray-900 mb-2">
              {Math.round(overall_score)}%
            </div>
            
            <p className="text-gray-600 mb-6">Overall Performance Score</p>
            
            <div className="flex justify-center space-x-4">
              <Link to="/" className="btn-secondary">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Home
              </Link>
              <button className="btn-primary">
                <Download className="w-5 h-5 mr-2" />
                Download Report
              </button>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Detailed Metrics */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            {/* Eye Contact */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <Eye className="w-6 h-6 text-blue-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Eye Contact</h3>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl font-bold text-gray-900">
                  {Math.round(eye_contact_percentage)}%
                </span>
                <span className="text-sm text-gray-500">Score</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-1000"
                  style={{ width: `${eye_contact_percentage}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {eye_contact_percentage >= 70 ? 'Excellent eye contact maintained throughout the interview.' : 
                 eye_contact_percentage >= 50 ? 'Good eye contact, but could be improved.' : 
                 'Eye contact needs significant improvement for better engagement.'}
              </p>
            </div>

            {/* Confidence Score */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <Brain className="w-6 h-6 text-green-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Confidence Level</h3>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl font-bold text-gray-900">
                  {Math.round(confidence_score * 100)}%
                </span>
                <span className="text-sm text-gray-500">Score</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-green-600 h-3 rounded-full transition-all duration-1000"
                  style={{ width: `${confidence_score * 100}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {confidence_score >= 0.7 ? 'High confidence demonstrated in responses.' : 
                 confidence_score >= 0.5 ? 'Moderate confidence, room for improvement.' : 
                 'Confidence needs to be built through practice and preparation.'}
              </p>
            </div>

            {/* Speech Clarity */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <Mic className="w-6 h-6 text-purple-600 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Speech Clarity</h3>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl font-bold text-gray-900">
                  {Math.round(speech_clarity * 100)}%
                </span>
                <span className="text-sm text-gray-500">Score</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-purple-600 h-3 rounded-full transition-all duration-1000"
                  style={{ width: `${speech_clarity * 100}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {speech_clarity >= 0.7 ? 'Clear and articulate speech throughout.' : 
                 speech_clarity >= 0.5 ? 'Generally clear speech with some areas for improvement.' : 
                 'Speech clarity needs improvement for better communication.'}
              </p>
            </div>
          </motion.div>

          {/* Charts */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            {/* Performance Breakdown */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Breakdown</h3>
              <div className="h-64">
                <Doughnut data={overallChartData} options={doughnutOptions} />
              </div>
            </div>

            {/* Performance Comparison */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Comparison</h3>
              <div className="h-64">
                <Bar data={comparisonData} options={chartOptions} />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Feedback Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-xl p-8 mt-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Detailed Feedback</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="bg-green-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {overall_score >= 80 && (
                  <>
                    <li className="text-green-800">• Excellent overall performance</li>
                    <li className="text-green-800">• Strong communication skills</li>
                    <li className="text-green-800">• Good preparation and confidence</li>
                  </>
                )}
                {eye_contact_percentage >= 70 && (
                  <li className="text-green-800">• Maintained good eye contact</li>
                )}
                {confidence_score >= 0.7 && (
                  <li className="text-green-800">• Demonstrated high confidence</li>
                )}
                {speech_clarity >= 0.7 && (
                  <li className="text-green-800">• Clear and articulate speech</li>
                )}
              </ul>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-orange-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-orange-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Areas for Improvement
              </h3>
              <ul className="space-y-2">
                {eye_contact_percentage < 70 && (
                  <li className="text-orange-800">• Work on maintaining better eye contact</li>
                )}
                {confidence_score < 0.7 && (
                  <li className="text-orange-800">• Build confidence through practice</li>
                )}
                {speech_clarity < 0.7 && (
                  <li className="text-orange-800">• Improve speech clarity and articulation</li>
                )}
                {overall_score < 80 && (
                  <li className="text-orange-800">• Continue practicing interview skills</li>
                )}
              </ul>
            </div>
          </div>

          {/* Recommendations */}
          <div className="mt-6 bg-blue-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-blue-900 mb-2">Practice Tips:</h4>
                <ul className="text-blue-800 space-y-1 text-sm">
                  <li>• Practice mock interviews regularly</li>
                  <li>• Record yourself and review your performance</li>
                  <li>• Work on maintaining eye contact</li>
                  <li>• Practice speaking clearly and confidently</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-900 mb-2">Next Steps:</h4>
                <ul className="text-blue-800 space-y-1 text-sm">
                  <li>• Schedule another practice session</li>
                  <li>• Focus on identified areas for improvement</li>
                  <li>• Review common interview questions</li>
                  <li>• Build confidence through preparation</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4 mt-8"
        >
          <Link to="/setup" className="btn-primary">
            Practice Again
          </Link>
          <Link to="/dashboard" className="btn-secondary">
            View All Sessions
          </Link>
        </motion.div>
      </div>
    </div>
  );
};

export default Results;