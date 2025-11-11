from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import base64
import cv2
import numpy as np
from datetime import datetime
import threading
import time

# Import custom modules
from ai_processor_simple import AIProcessor
from speech_analyzer import SpeechAnalyzer
from question_generator import QuestionGenerator
from database_models import db, InterviewSession, PerformanceMetrics, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)

# Initialize AI components
ai_processor = AIProcessor()
speech_analyzer = SpeechAnalyzer()
question_generator = QuestionGenerator()

# Global variables for active sessions
active_sessions = {}

# Helper function to get current user
def get_current_user():
    """Get current logged-in user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

# Helper function to require authentication
def require_auth():
    """Decorator helper to check if user is authenticated"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    return None

@app.route('/')
def index():
    """Main application entry point"""
    return render_template('index.html')

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='candidate'
        )
        db.session.add(user)
        db.session.commit()
        
        # Log user in
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Log user in
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Get current logged-in user information"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_components': {
            'face_detection': ai_processor.is_face_detection_ready(),
            'emotion_recognition': ai_processor.is_emotion_recognition_ready(),
            'speech_analysis': speech_analyzer.is_ready()
        }
    })

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Upload and parse resume to generate personalized questions"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save and parse resume
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # Extract information and generate questions
        resume_data = question_generator.parse_resume(filepath)
        questions = question_generator.generate_questions(resume_data)
        
        return jsonify({
            'success': True,
            'resume_data': resume_data,
            'questions': questions,
            'message': 'Resume uploaded and questions generated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        # Check authentication
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        candidate_name = data.get('candidate_name', user.username)
        questions = data.get('questions', [])
        
        # Ensure database tables exist (will create if they don't exist)
        db.create_all()
        
        # Create new session linked to user
        interview_session = InterviewSession(
            user_id=user.id,
            candidate_name=candidate_name,
            start_time=datetime.now(),
            questions=json.dumps(questions) if questions else '[]',
            status='active'
        )
        db.session.add(interview_session)
        db.session.commit()
        
        # Initialize session data
        active_sessions[interview_session.id] = {
            'session_id': interview_session.id,
            'user_id': user.id,
            'candidate_name': candidate_name,
            'questions': questions,
            'current_question': 0,
            'metrics': {
                'eye_contact_percentage': 0,
                'confidence_score': 0,
                'speech_clarity': 0,
                'emotion_scores': {},
                'warnings': []
            },
            'start_time': datetime.now()
        }
        
        return jsonify({
            'success': True,
            'session_id': interview_session.id,
            'message': 'Interview session started successfully'
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in start_interview: {str(e)}")
        print(f"Traceback: {error_trace}")
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'details': error_trace if app.debug else None
        }), 500

@app.route('/api/process-frame', methods=['POST'])
def process_frame():
    """Process video frame for face detection and emotion analysis"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        frame_data = data.get('frame_data')  # Base64 encoded image
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Process frame with AI
        results = ai_processor.process_frame(frame)
        
        # Update session metrics
        session = active_sessions[session_id]
        session['metrics']['eye_contact_percentage'] = results.get('eye_contact_percentage', 0)
        session['metrics']['confidence_score'] = results.get('confidence_score', 0)
        session['metrics']['emotion_scores'] = results.get('emotion_scores', {})
        session['metrics']['face_detected'] = results.get('face_detected', False)
        session['metrics']['landmarks'] = results.get('landmarks', 0)
        
        # Check for warnings
        warnings = []
        if results['eye_contact_percentage'] < 30:
            warnings.append('Low eye contact detected')
        if results['confidence_score'] < 0.5:
            warnings.append('Low confidence detected')
        
        session['metrics']['warnings'] = warnings
        
        # Emit real-time updates via WebSocket
        socketio.emit('metrics_update', {
            'session_id': session_id,
            'metrics': {
                'eyeContactPercentage': session['metrics']['eye_contact_percentage'],
                'confidenceScore': session['metrics']['confidence_score'],
                'speechClarity': session['metrics'].get('speech_clarity', 0),
                'emotionScores': session['metrics']['emotion_scores'],
                'face_detected': session['metrics']['face_detected'],
                'landmarks': session['metrics']['landmarks'],
                'warnings': warnings
            }
        })
        
        return jsonify({
            'success': True,
            'results': {
                'eye_contact_percentage': results.get('eye_contact_percentage', 0),
                'confidence_score': results.get('confidence_score', 0),
                'emotion_scores': results.get('emotion_scores', {}),
                'face_detected': results.get('face_detected', False),
                'landmarks': results.get('landmarks', 0)
            },
            'warnings': warnings
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-audio', methods=['POST'])
def process_audio():
    """Process audio for speech analysis"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        audio_data = data.get('audio_data')  # Base64 encoded audio
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Process audio
        speech_results = speech_analyzer.analyze_audio(audio_data)
        
        # Update session metrics
        session = active_sessions[session_id]
        session['metrics']['speech_clarity'] = speech_results['clarity_score']
        session['metrics']['filler_words'] = speech_results['filler_words']
        
        return jsonify({
            'success': True,
            'speech_results': speech_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/end-interview/<int:session_id>', methods=['POST'])
def end_interview(session_id):
    """End interview session and generate final report"""
    try:
        # Check authentication
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session_data = active_sessions[session_id]
        
        # Verify user owns this session
        if session_data.get('user_id') != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Calculate final metrics
        final_metrics = calculate_final_metrics(session_data)
        
        # Save to database
        performance = PerformanceMetrics(
            session_id=session_id,
            eye_contact_percentage=final_metrics['eye_contact_percentage'],
            confidence_score=final_metrics['confidence_score'],
            speech_clarity=final_metrics['speech_clarity'],
            overall_score=final_metrics['overall_score'],
            feedback=json.dumps(final_metrics['feedback']),
            created_at=datetime.now()
        )
        db.session.add(performance)
        
        # Update session status
        interview_session = InterviewSession.query.get(session_id)
        if interview_session:
            interview_session.end_time = datetime.now()
            interview_session.status = 'completed'
        
        db.session.commit()
        
        # Remove from active sessions
        del active_sessions[session_id]
        
        return jsonify({
            'success': True,
            'final_report': final_metrics,
            'message': 'Interview completed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed session information"""
    try:
        # Check authentication
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        interview_session = InterviewSession.query.get(session_id)
        if not interview_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check if user owns this session
        if interview_session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        performance = PerformanceMetrics.query.filter_by(session_id=session_id).first()
        
        return jsonify({
            'session': {
                'id': interview_session.id,
                'candidate_name': interview_session.candidate_name,
                'start_time': interview_session.start_time.isoformat(),
                'end_time': interview_session.end_time.isoformat() if interview_session.end_time else None,
                'status': interview_session.status,
                'questions': json.loads(interview_session.questions) if interview_session.questions else []
            },
            'performance': {
                'eye_contact_percentage': performance.eye_contact_percentage,
                'confidence_score': performance.confidence_score,
                'speech_clarity': performance.speech_clarity,
                'overall_score': performance.overall_score,
                'feedback': json.loads(performance.feedback) if performance.feedback else []
            } if performance else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_all_sessions():
    """Get all interview sessions for the current user"""
    try:
        # Check authentication
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get only sessions belonging to the current user
        sessions = InterviewSession.query.filter_by(user_id=user.id).order_by(InterviewSession.start_time.desc()).all()
        
        return jsonify({
            'sessions': [{
                'id': session.id,
                'candidate_name': session.candidate_name,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'status': session.status
            } for session in sessions]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_final_metrics(session_data):
    """Calculate final performance metrics"""
    metrics = session_data['metrics']
    
    # Calculate overall score (weighted average)
    overall_score = (
        metrics['eye_contact_percentage'] * 0.3 +
        metrics['confidence_score'] * 100 * 0.3 +
        metrics['speech_clarity'] * 0.4
    )
    
    # Generate feedback
    feedback = []
    if metrics['eye_contact_percentage'] < 50:
        feedback.append("Work on maintaining better eye contact during interviews")
    if metrics['confidence_score'] < 0.6:
        feedback.append("Practice to build more confidence in your responses")
    if metrics['speech_clarity'] < 0.7:
        feedback.append("Focus on speaking clearly and reducing filler words")
    
    if not feedback:
        feedback.append("Excellent performance! Keep up the good work.")
    
    return {
        'eye_contact_percentage': metrics['eye_contact_percentage'],
        'confidence_score': metrics['confidence_score'],
        'speech_clarity': metrics['speech_clarity'],
        'overall_score': round(overall_score, 2),
        'feedback': feedback
    }

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    if session_id in active_sessions:
        print(f'Client joined session {session_id}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)