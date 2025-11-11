import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import math
from typing import Dict, List, Tuple, Optional

class AIProcessor:
    def __init__(self):
        """Initialize AI processor with MediaPipe and emotion recognition models"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize MediaPipe Face Mesh with improved parameters
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,  # Increased for more accurate detection
            min_tracking_confidence=0.6,   # Increased for better tracking
            static_image_mode=False        # Set to False for video processing
        )
        
        # Emotion recognition model
        self.emotion_model = None
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.load_emotion_model()
        
        # Enhanced eye tracking parameters
        self.eye_landmarks = {
            'left_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            'right_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            'left_iris': [468, 469, 470, 471, 472],  # Iris landmarks
            'right_iris': [473, 474, 475, 476, 477]  # Iris landmarks
        }
        
        # Initialize model directories
        self.model_dir = os.path.join(os.path.dirname(__file__), 'ai_models')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        
        # Confidence and eye contact tracking with decay
        self.confidence_history = []
        self.eye_contact_history = []
        self.history_max_len = 30  # Maximum history length
        self.history_weight = 0.7  # Weight for recent frames
        
    def load_emotion_model(self):
        """Load pre-trained emotion recognition model"""
        try:
            # For now, we'll use a simple model. In production, you'd load a pre-trained model
            model_path = os.path.join('ai_models', 'emotion_model.h5')
            if os.path.exists(model_path):
                self.emotion_model = load_model(model_path)
            else:
                print("Emotion model not found. Using basic emotion detection.")
                self.emotion_model = None
        except Exception as e:
            print(f"Error loading emotion model: {e}")
            self.emotion_model = None
    
    def is_face_detection_ready(self) -> bool:
        """Check if face detection is ready"""
        return self.face_mesh is not None
    
    def is_emotion_recognition_ready(self) -> bool:
        """Check if emotion recognition is ready"""
        return self.emotion_model is not None
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame for face detection, eye tracking, and emotion analysis"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width = frame.shape[:2]
            
            # Process with MediaPipe
            results = self.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return self._get_default_results()
            
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract metrics
            eye_contact_percentage = self._calculate_eye_contact(face_landmarks, width, height)
            confidence_score = self._calculate_confidence(face_landmarks, width, height)
            emotion_scores = self._analyze_emotions(frame, face_landmarks)
            
            # Update history
            self.eye_contact_history.append(eye_contact_percentage)
            self.confidence_history.append(confidence_score)
            
            # Keep only last 30 frames for averaging
            if len(self.eye_contact_history) > 30:
                self.eye_contact_history.pop(0)
            if len(self.confidence_history) > 30:
                self.confidence_history.pop(0)
            
            return {
                'eye_contact_percentage': np.mean(self.eye_contact_history),
                'confidence_score': np.mean(self.confidence_history),
                'emotion_scores': emotion_scores,
                'face_detected': True,
                'landmarks': len(face_landmarks.landmark)
            }
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return self._get_default_results()
    
    def _get_default_results(self) -> Dict:
        """Return default results when no face is detected"""
        return {
            'eye_contact_percentage': 0,
            'confidence_score': 0,
            'emotion_scores': {label: 0 for label in self.emotion_labels},
            'face_detected': False,
            'landmarks': 0
        }
    
    def _calculate_eye_contact(self, landmarks, width: int, height: int) -> float:
        """Calculate eye contact percentage based on gaze direction"""
        try:
            # Get eye landmarks
            left_eye_points = []
            right_eye_points = []
            
            # Get iris landmarks (new in MediaPipe FaceMesh)
            left_iris = [landmarks.landmark[468], landmarks.landmark[469], 
                        landmarks.landmark[470], landmarks.landmark[471], landmarks.landmark[472]]
            right_iris = [landmarks.landmark[473], landmarks.landmark[474], 
                         landmarks.landmark[475], landmarks.landmark[476], landmarks.landmark[477]]
            
            for idx in self.eye_landmarks['left_eye']:
                landmark = landmarks.landmark[idx]
                left_eye_points.append([landmark.x * width, landmark.y * height])
            
            for idx in self.eye_landmarks['right_eye']:
                landmark = landmarks.landmark[idx]
                right_eye_points.append([landmark.x * width, landmark.y * height])
            
            # Calculate eye aspect ratio (EAR)
            left_ear = self._eye_aspect_ratio(left_eye_points)
            right_ear = self._eye_aspect_ratio(right_eye_points)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Calculate iris positions relative to eye centers
            left_iris_center = np.mean([(p.x, p.y) for p in left_iris], axis=0)
            right_iris_center = np.mean([(p.x, p.y) for p in right_iris], axis=0)
            
            # Calculate relative iris positions
            left_eye_center = np.mean(left_eye_points, axis=0)
            right_eye_center = np.mean(right_eye_points, axis=0)
            
            # Calculate gaze direction using iris positions
            left_gaze = self._calculate_iris_score(left_iris_center, left_eye_center, width, height)
            right_gaze = self._calculate_iris_score(right_iris_center, right_eye_center, width, height)
            
            # Average gaze score
            gaze_score = (left_gaze + right_gaze) / 2.0
            
            # Combine EAR and gaze direction with weighted importance
            eye_contact_score = (ear * 0.4 + gaze_score * 0.6) * 100
            
            return max(0, min(100, eye_contact_score))
            
        except Exception as e:
            print(f"Error calculating eye contact: {e}")
            return 0
    
    def _eye_aspect_ratio(self, eye_points: List[List[float]]) -> float:
        """Calculate the eye aspect ratio"""
        try:
            # Vertical distances
            A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            
            # Horizontal distance
            C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            # Eye aspect ratio
            ear = (A + B) / (2.0 * C)
            return ear
            
        except Exception as e:
            print(f"Error calculating EAR: {e}")
            return 0
    
    def _calculate_gaze_center(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """Calculate the center point of gaze direction using iris detection"""
        try:
            # Use iris centers for more accurate gaze estimation
            left_iris_center = np.mean([(landmarks.landmark[i].x, landmarks.landmark[i].y) 
                                      for i in range(468, 473)], axis=0)
            right_iris_center = np.mean([(landmarks.landmark[i].x, landmarks.landmark[i].y) 
                                       for i in range(473, 478)], axis=0)
            
            # Calculate gaze center as the midpoint between iris centers
            gaze_x = (left_iris_center[0] + right_iris_center[0]) / 2 * width
            gaze_y = (left_iris_center[1] + right_iris_center[1]) / 2 * height
            
            return gaze_x, gaze_y
            
        except Exception as e:
            print(f"Error calculating gaze center: {e}")
            return width/2, height/2
            
    def _calculate_iris_score(self, iris_center: Tuple[float, float],
                            eye_center: np.ndarray, width: int, height: int) -> float:
        """Calculate how centered the iris is within the eye"""
        try:
            # Convert iris center to pixel coordinates
            iris_x, iris_y = iris_center[0] * width, iris_center[1] * height

            # Calculate distance from iris center to eye center
            distance = np.linalg.norm([iris_x - eye_center[0], iris_y - eye_center[1]])

            # Normalize the distance (closer to eye center = better score)
            # Typical eye size is about 3% of face width
            max_distance = width * 0.03
            normalized_distance = 1 - min(distance / max_distance, 1)

            return normalized_distance

        except Exception as e:
            print(f"Error calculating iris score: {e}")
            return 0.5
    
    def _calculate_confidence(self, landmarks, width: int, height: int) -> float:
        """Calculate confidence score based on facial features"""
        try:
            confidence_factors = []
            
            # 1. Head pose (facing forward)
            head_pose_score = self._calculate_head_pose_score(landmarks, width, height)
            confidence_factors.append(head_pose_score)
            
            # 2. Facial symmetry
            symmetry_score = self._calculate_symmetry_score(landmarks, width, height)
            confidence_factors.append(symmetry_score)
            
            # 3. Eye openness
            eye_openness_score = self._calculate_eye_openness_score(landmarks, width, height)
            confidence_factors.append(eye_openness_score)
            
            # 4. Mouth position (not too open, not too closed)
            mouth_score = self._calculate_mouth_score(landmarks, width, height)
            confidence_factors.append(mouth_score)
            
            # Average all factors
            confidence_score = np.mean(confidence_factors)
            return max(0, min(1, confidence_score))
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0
    
    def _calculate_head_pose_score(self, landmarks, width: int, height: int) -> float:
        """Calculate head pose score (facing forward = higher score)"""
        try:
            # Use nose and ear landmarks to estimate head pose
            nose_tip = landmarks.landmark[4]
            left_ear = landmarks.landmark[234]
            right_ear = landmarks.landmark[454]
            
            # Calculate head tilt
            head_width = abs(left_ear.x - right_ear.x) * width
            expected_width = 0.3 * width  # Expected head width ratio
            
            # Score based on how close to expected width
            width_ratio = head_width / expected_width
            score = 1 - abs(1 - width_ratio)
            
            return max(0, min(1, score))
            
        except Exception as e:
            print(f"Error calculating head pose: {e}")
            return 0.5
    
    def _calculate_symmetry_score(self, landmarks, width: int, height: int) -> float:
        """Calculate facial symmetry score"""
        try:
            # Compare left and right side landmarks
            left_eye = landmarks.landmark[33]
            right_eye = landmarks.landmark[263]
            left_mouth = landmarks.landmark[61]
            right_mouth = landmarks.landmark[291]
            
            # Calculate symmetry
            eye_symmetry = 1 - abs(left_eye.y - right_eye.y)
            mouth_symmetry = 1 - abs(left_mouth.y - right_mouth.y)
            
            symmetry_score = (eye_symmetry + mouth_symmetry) / 2
            return max(0, min(1, symmetry_score))
            
        except Exception as e:
            print(f"Error calculating symmetry: {e}")
            return 0.5
    
    def _calculate_eye_openness_score(self, landmarks, width: int, height: int) -> float:
        """Calculate eye openness score"""
        try:
            left_ear = self._eye_aspect_ratio([landmarks.landmark[i] for i in self.eye_landmarks['left_eye']])
            right_ear = self._eye_aspect_ratio([landmarks.landmark[i] for i in self.eye_landmarks['right_eye']])
            
            avg_ear = (left_ear + right_ear) / 2
            
            # Normalize EAR to 0-1 range (typical EAR range is 0.2-0.3)
            normalized_ear = (avg_ear - 0.2) / 0.1
            return max(0, min(1, normalized_ear))
            
        except Exception as e:
            print(f"Error calculating eye openness: {e}")
            return 0.5
    
    def _calculate_mouth_score(self, landmarks, width: int, height: int) -> float:
        """Calculate mouth position score"""
        try:
            # Mouth landmarks for openness calculation
            mouth_landmarks = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
            mouth_points = [landmarks.landmark[i] for i in mouth_landmarks]
            
            # Calculate mouth aspect ratio (MAR)
            vertical_distances = []
            for i in range(0, len(mouth_points), 2):
                if i + 1 < len(mouth_points):
                    dist = np.linalg.norm([
                        mouth_points[i].x - mouth_points[i+1].x,
                        mouth_points[i].y - mouth_points[i+1].y
                    ])
                    vertical_distances.append(dist)
            
            if vertical_distances:
                mar = np.mean(vertical_distances)
                # Normalize MAR (typical range 0.1-0.3)
                normalized_mar = (mar - 0.1) / 0.2
                return max(0, min(1, 1 - normalized_mar))  # Invert so lower MAR = higher score
            
            return 0.5
            
        except Exception as e:
            print(f"Error calculating mouth score: {e}")
            return 0.5
    
    def _analyze_emotions(self, frame: np.ndarray, landmarks) -> Dict[str, float]:
        """Analyze emotions in the frame"""
        try:
            if self.emotion_model is None:
                # Basic emotion detection using facial features
                return self._basic_emotion_detection(landmarks)
            
            # Extract face region
            face_region = self._extract_face_region(frame, landmarks)
            if face_region is None:
                return {label: 0 for label in self.emotion_labels}
            
            # Preprocess for model
            face_region = cv2.resize(face_region, (48, 48))
            face_region = face_region / 255.0
            face_region = np.expand_dims(face_region, axis=[0, -1])
            
            # Predict emotions
            predictions = self.emotion_model.predict(face_region, verbose=0)
            emotion_scores = {label: float(score) for label, score in zip(self.emotion_labels, predictions[0])}
            
            return emotion_scores
            
        except Exception as e:
            print(f"Error analyzing emotions: {e}")
            return {label: 0 for label in self.emotion_labels}
    
    def _basic_emotion_detection(self, landmarks) -> Dict[str, float]:
        """Basic emotion detection using facial landmarks"""
        try:
            emotions = {label: 0.0 for label in self.emotion_labels}
            
            # Analyze mouth shape for happiness/sadness
            mouth_landmarks = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
            mouth_points = [landmarks.landmark[i] for i in mouth_landmarks]
            
            # Calculate mouth curvature
            mouth_center = np.mean([(p.x, p.y) for p in mouth_points], axis=0)
            mouth_curvature = 0
            
            for point in mouth_points:
                mouth_curvature += (point.y - mouth_center[1])
            
            mouth_curvature /= len(mouth_points)
            
            # Assign emotions based on mouth curvature
            if mouth_curvature > 0.01:
                emotions['happy'] = 0.7
                emotions['neutral'] = 0.3
            elif mouth_curvature < -0.01:
                emotions['sad'] = 0.6
                emotions['neutral'] = 0.4
            else:
                emotions['neutral'] = 0.8
                emotions['happy'] = 0.1
                emotions['sad'] = 0.1
            
            return emotions
            
        except Exception as e:
            print(f"Error in basic emotion detection: {e}")
            return {label: 0.0 for label in self.emotion_labels}
    
    def _extract_face_region(self, frame: np.ndarray, landmarks) -> Optional[np.ndarray]:
        """Extract face region from frame"""
        try:
            # Get face bounding box
            x_coords = [landmark.x for landmark in landmarks.landmark]
            y_coords = [landmark.y for landmark in landmarks.landmark]
            
            x_min, x_max = int(min(x_coords) * frame.shape[1]), int(max(x_coords) * frame.shape[1])
            y_min, y_max = int(min(y_coords) * frame.shape[0]), int(max(y_coords) * frame.shape[0])
            
            # Add padding
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(frame.shape[1], x_max + padding)
            y_max = min(frame.shape[0], y_max + padding)
            
            # Extract face region
            face_region = frame[y_min:y_max, x_min:x_max]
            
            if face_region.size == 0:
                return None
            
            return face_region
            
        except Exception as e:
            print(f"Error extracting face region: {e}")
            return None
    
    def get_performance_summary(self) -> Dict:
        """Get summary of performance metrics"""
        return {
            'avg_eye_contact': np.mean(self.eye_contact_history) if self.eye_contact_history else 0,
            'avg_confidence': np.mean(self.confidence_history) if self.confidence_history else 0,
            'total_frames_processed': len(self.eye_contact_history)
        }