from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)

# Simple database models
class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    questions = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')

class PerformanceMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_session.id'), nullable=False)
    eye_contact_percentage = db.Column(db.Float, default=0)
    confidence_score = db.Column(db.Float, default=0)
    speech_clarity = db.Column(db.Float, default=0)
    overall_score = db.Column(db.Float, default=0)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    """Main application entry point"""
    return jsonify({'message': 'Interview System API is running'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Basic API is working'
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
        
        # Save resume file
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # Generate sample questions (without complex AI processing)
        sample_questions = [
            {
                "id": 1,
                "question": "Tell me about yourself and your background.",
                "category": "behavioral",
                "difficulty": "easy",
                "type": "open_ended"
            },
            {
                "id": 2,
                "question": "What are your strengths and weaknesses?",
                "category": "behavioral",
                "difficulty": "medium",
                "type": "open_ended"
            },
            {
                "id": 3,
                "question": "Why are you interested in this position?",
                "category": "behavioral",
                "difficulty": "easy",
                "type": "open_ended"
            },
            {
                "id": 4,
                "question": "Describe a challenging situation you faced at work and how you handled it.",
                "category": "behavioral",
                "difficulty": "medium",
                "type": "situation"
            },
            {
                "id": 5,
                "question": "Where do you see yourself in 5 years?",
                "category": "behavioral",
                "difficulty": "easy",
                "type": "open_ended"
            }
        ]
        
        return jsonify({
            'success': True,
            'resume_data': {
                'filename': filename,
                'upload_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(filepath)
            },
            'questions': sample_questions,
            'message': 'Resume uploaded and questions generated successfully'
        })
    
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name', 'Anonymous')
        questions = data.get('questions', [])
        
        # Create new session
        session = InterviewSession(
            candidate_name=candidate_name,
            start_time=datetime.now(),
            questions=json.dumps(questions),
            status='active'
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'message': 'Interview session started successfully'
        })
    
    except Exception as e:
        print(f"Error in start_interview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/end-interview/<int:session_id>', methods=['POST'])
def end_interview(session_id):
    """End interview session and generate final report"""
    try:
        session = InterviewSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update session status
        session.end_time = datetime.now()
        session.status = 'completed'
        
        # Generate sample final report
        final_report = {
            'eye_contact_percentage': 75,
            'confidence_score': 0.8,
            'speech_clarity': 0.85,
            'overall_score': 80,
            'feedback': [
                "Good eye contact maintained throughout the interview",
                "Confident and clear communication",
                "Well-structured responses to questions"
            ]
        }
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'final_report': final_report,
            'message': 'Interview completed successfully'
        })
    
    except Exception as e:
        print(f"Error in end_interview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed session information"""
    try:
        session = InterviewSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session': {
                'id': session.id,
                'candidate_name': session.candidate_name,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'status': session.status,
                'questions': json.loads(session.questions) if session.questions else []
            }
        })
    
    except Exception as e:
        print(f"Error in get_session_details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_all_sessions():
    """Get all interview sessions"""
    try:
        sessions = InterviewSession.query.order_by(InterviewSession.start_time.desc()).all()
        
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
        print(f"Error in get_all_sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
