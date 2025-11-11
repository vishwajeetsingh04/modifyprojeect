from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class InterviewSession(db.Model):
    """Model for storing interview session information"""
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Link to user
    candidate_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, cancelled
    questions = db.Column(db.Text, nullable=True)  # JSON string of questions
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to performance metrics and user
    performance = db.relationship('PerformanceMetrics', backref='session', uselist=False)
    user = db.relationship('User', backref='interview_sessions')
    
    def __repr__(self):
        return f'<InterviewSession {self.id}: {self.candidate_name}>'
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'questions': self.questions,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PerformanceMetrics(db.Model):
    """Model for storing performance metrics for each interview session"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    
    # Core metrics
    eye_contact_percentage = db.Column(db.Float, nullable=False, default=0.0)
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)
    speech_clarity = db.Column(db.Float, nullable=False, default=0.0)
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    
    # Detailed metrics (stored as JSON)
    emotion_scores = db.Column(db.Text, nullable=True)  # JSON string
    filler_words_count = db.Column(db.Integer, nullable=False, default=0)
    speaking_rate = db.Column(db.Float, nullable=False, default=0.0)
    pause_frequency = db.Column(db.Float, nullable=False, default=0.0)
    
    # Feedback and analysis
    feedback = db.Column(db.Text, nullable=True)  # JSON string of feedback points
    strengths = db.Column(db.Text, nullable=True)  # JSON string
    areas_for_improvement = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PerformanceMetrics {self.id}: Session {self.session_id}>'
    
    def to_dict(self):
        """Convert metrics to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'eye_contact_percentage': self.eye_contact_percentage,
            'confidence_score': self.confidence_score,
            'speech_clarity': self.speech_clarity,
            'overall_score': self.overall_score,
            'emotion_scores': self.emotion_scores,
            'filler_words_count': self.filler_words_count,
            'speaking_rate': self.speaking_rate,
            'pause_frequency': self.pause_frequency,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class QuestionBank(db.Model):
    """Model for storing question bank"""
    __tablename__ = 'question_bank'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # technical, behavioral, general, etc.
    difficulty = db.Column(db.String(20), nullable=False, default='medium')  # easy, medium, hard
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuestionBank {self.id}: {self.category}>'
    
    def to_dict(self):
        """Convert question to dictionary"""
        return {
            'id': self.id,
            'question_text': self.question_text,
            'category': self.category,
            'difficulty': self.difficulty,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model):
    """Model for storing user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='candidate')  # candidate, interviewer, admin
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.id}: {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ResumeData(db.Model):
    """Model for storing parsed resume data"""
    __tablename__ = 'resume_data'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    
    # Parsed resume information
    candidate_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Structured data (stored as JSON)
    education = db.Column(db.Text, nullable=True)  # JSON string
    experience = db.Column(db.Text, nullable=True)  # JSON string
    skills = db.Column(db.Text, nullable=True)  # JSON string
    projects = db.Column(db.Text, nullable=True)  # JSON string
    
    # Raw resume text
    raw_text = db.Column(db.Text, nullable=True)
    
    # File information
    original_filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResumeData {self.id}: Session {self.session_id}>'
    
    def to_dict(self):
        """Convert resume data to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'candidate_name': self.candidate_name,
            'email': self.email,
            'phone': self.phone,
            'education': self.education,
            'experience': self.experience,
            'skills': self.skills,
            'projects': self.projects,
            'raw_text': self.raw_text,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Database initialization function
def init_db(app):
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add sample questions to question bank
        sample_questions = [
            {
                'question_text': 'Tell me about yourself.',
                'category': 'general',
                'difficulty': 'easy',
                'tags': '["introduction", "personal"]'
            },
            {
                'question_text': 'Why are you interested in this position?',
                'category': 'general',
                'difficulty': 'medium',
                'tags': '["motivation", "interest"]'
            },
            {
                'question_text': 'What are your strengths and weaknesses?',
                'category': 'general',
                'difficulty': 'medium',
                'tags': '["self-assessment", "reflection"]'
            },
            {
                'question_text': 'Tell me about a time when you had to solve a difficult problem.',
                'category': 'behavioral',
                'difficulty': 'hard',
                'tags': '["problem-solving", "situation"]'
            },
            {
                'question_text': 'Describe a situation where you had to work under pressure.',
                'category': 'behavioral',
                'difficulty': 'hard',
                'tags': '["pressure", "stress-management"]'
            },
            {
                'question_text': 'Can you explain your experience with Python?',
                'category': 'technical',
                'difficulty': 'medium',
                'tags': '["python", "programming"]'
            },
            {
                'question_text': 'What is your experience with machine learning?',
                'category': 'technical',
                'difficulty': 'hard',
                'tags': '["machine-learning", "ai"]'
            },
            {
                'question_text': 'How do you handle working with a difficult team member?',
                'category': 'behavioral',
                'difficulty': 'medium',
                'tags': '["teamwork", "conflict-resolution"]'
            }
        ]
        
        # Check if questions already exist
        existing_questions = QuestionBank.query.count()
        if existing_questions == 0:
            for question_data in sample_questions:
                question = QuestionBank(**question_data)
                db.session.add(question)
            
            db.session.commit()
            print("Sample questions added to database.")