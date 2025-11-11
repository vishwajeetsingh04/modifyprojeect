# AI/ML Interview Assessment System - Setup Guide

## Project Overview
This is an AI-powered interview assessment system that uses computer vision and speech recognition to provide real-time feedback during virtual interviews. The system monitors eye contact, facial expressions, speech clarity, and confidence levels to provide comprehensive interview performance analysis.

## Team Information
- **Team**: Code Force
- **Members**: Bhumika Gupta, Vishwajeet Singh, Vandana Rautela, Sneha Thapliyal
- **Institution**: Graphic Era Hill University, Dehradun
- **Semester**: 7th Semester B.Tech CSE
- **Supervisor**: Dr. Seema Gulati

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 2GB free space
- **Webcam**: Required for face detection and eye tracking
- **Microphone**: Required for speech analysis

### Software Dependencies
- Python 3.8+
- Node.js 16+
- Git (for cloning the repository)
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd interview-assessment-system
```

### Step 2: Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install additional system dependencies** (if needed):
   ```bash
   # For Windows users, you might need to install Visual C++ Build Tools
   # For Linux users, you might need to install system libraries
   sudo apt-get install python3-dev build-essential
   ```

### Step 3: Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Install additional frontend dependencies** (if needed):
   ```bash
   npm install @tailwindcss/forms
   ```

## Running the Application

### Option 1: Using the Startup Script (Windows)
1. Double-click the `start.bat` file
2. Wait for both servers to start
3. Access the application at `http://localhost:3000`

### Option 2: Manual Startup

#### Start Backend Server
```bash
cd backend
python app.py
```
The backend server will start on `http://localhost:5000`

#### Start Frontend Server (in a new terminal)
```bash
cd frontend
npm start
```
The frontend server will start on `http://localhost:3000`

### Option 3: Using Docker (Advanced)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///interview_system.db
DEBUG=True
```

### AI Model Configuration
The system uses pre-trained models for:
- Face detection (MediaPipe)
- Emotion recognition (TensorFlow)
- Speech analysis (librosa, speech_recognition)

Models are automatically downloaded on first run.

## Usage Guide

### 1. Starting an Interview Session
1. Open the application in your browser
2. Click "Start Interview" on the home page
3. Upload your resume (PDF, DOC, DOCX)
4. Select interview questions
5. Enter your name and start the interview

### 2. During the Interview
- Ensure good lighting for face detection
- Maintain eye contact with the camera
- Speak clearly and confidently
- Answer questions naturally
- Monitor real-time feedback

### 3. Viewing Results
- Complete the interview session
- Review detailed performance analysis
- Check specific metrics (eye contact, confidence, speech clarity)
- Download performance reports

## Features

### Real-time Analysis
- **Eye Contact Tracking**: Monitors gaze direction and eye contact percentage
- **Facial Expression Analysis**: Detects emotions and confidence levels
- **Speech Analysis**: Analyzes clarity, tone, and filler words
- **Performance Metrics**: Real-time scoring and feedback

### AI Components
- **Face Detection**: Using MediaPipe for accurate facial landmark detection
- **Emotion Recognition**: Machine learning models for emotion classification
- **Speech Processing**: Audio analysis for speech quality assessment
- **Question Generation**: AI-powered personalized question generation

### User Interface
- **Modern Design**: Responsive, intuitive interface
- **Real-time Feedback**: Live metrics and warnings
- **Performance Dashboard**: Comprehensive analytics and trends
- **Session Management**: Track and review past interviews

## Troubleshooting

### Common Issues

#### Backend Issues
1. **Port already in use**:
   ```bash
   # Find and kill the process using port 5000
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   ```

2. **Python dependencies not found**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **MediaPipe installation issues**:
   ```bash
   pip install mediapipe --upgrade
   ```

#### Frontend Issues
1. **Node modules not found**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port 3000 already in use**:
   ```bash
   # Kill the process using port 3000
   npx kill-port 3000
   ```

3. **Webcam access denied**:
   - Ensure browser has camera permissions
   - Check if another application is using the camera

### Performance Optimization
1. **Close unnecessary applications** to free up system resources
2. **Ensure good lighting** for better face detection accuracy
3. **Use a wired internet connection** for stable performance
4. **Update graphics drivers** for better webcam performance

## API Documentation

### Backend Endpoints
- `GET /api/health` - Health check
- `POST /api/upload-resume` - Upload and parse resume
- `POST /api/start-interview` - Start new interview session
- `POST /api/process-frame` - Process video frame
- `POST /api/process-audio` - Process audio data
- `POST /api/end-interview/{session_id}` - End interview session
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{session_id}` - Get session details

### WebSocket Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `join_session` - Join interview session
- `metrics_update` - Real-time metrics update

## Development

### Project Structure
```
interview-assessment-system/
├── backend/                 # Python Flask API
│   ├── app.py              # Main Flask application
│   ├── ai_processor.py     # AI processing modules
│   ├── speech_analyzer.py  # Speech analysis
│   ├── question_generator.py # Question generation
│   ├── database_models.py  # Database models
│   └── requirements.txt    # Python dependencies
├── frontend/               # React.js application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context
│   │   └── App.js         # Main app component
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind configuration
├── README.md              # Project documentation
├── SETUP_GUIDE.md         # This setup guide
└── start.bat              # Windows startup script
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

### Getting Help
- Check the troubleshooting section above
- Review the API documentation
- Check browser console for frontend errors
- Check terminal output for backend errors

### Contact Information
For technical support or questions:
- **Team**: Code Force
- **Institution**: Graphic Era Hill University, Dehradun
- **Supervisor**: Dr. Seema Gulati

## License
This project is developed for academic purposes at Graphic Era Hill University.

## Acknowledgments
- MediaPipe for face detection and tracking
- TensorFlow for machine learning models
- React.js for frontend framework
- Flask for backend framework
- Tailwind CSS for styling