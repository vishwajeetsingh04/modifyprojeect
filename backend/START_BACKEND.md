# Starting the Backend Server

## Quick Start

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Start the Flask server:**
   ```bash
   python app.py
   ```

   Or if using the virtual environment:
   ```bash
   .\backend_env\Scripts\activate
   python app.py
   ```

## What's Installed

The following critical packages are already installed:
- ✅ Flask
- ✅ Flask-CORS
- ✅ Flask-SocketIO
- ✅ OpenCV (cv2)
- ✅ MediaPipe
- ✅ NumPy (1.26.4 - compatible version)
- ✅ SQLAlchemy
- ✅ Flask-SQLAlchemy

## Optional Packages

Some packages in requirements.txt may not be installed yet (like torch, tensorflow, etc.), but they're not required for basic functionality. The backend should start without them.

## Troubleshooting

If you get import errors:
1. Make sure you're in the backend directory
2. Activate the virtual environment if using one
3. Install missing packages: `pip install <package-name>`

## Backend URL

Once started, the backend will run on: `http://localhost:5000`

The frontend (running on port 3001) will automatically proxy API requests to this backend.

