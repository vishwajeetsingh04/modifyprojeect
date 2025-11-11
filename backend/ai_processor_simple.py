import cv2
import mediapipe as mp
import numpy as np
import os
import math
from typing import Dict, List, Tuple, Optional

class AIProcessor:
    def __init__(self):
        """Initialize AI processor with MediaPipe for face and eye detection"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize MediaPipe Face Mesh with improved parameters
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False  # Better for video streams
        )
        
        # Basic emotion labels (we'll use simple heuristics instead of ML model)
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Eye tracking parameters
        self.eye_landmarks = {
            'left_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            'right_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        }
        
        # Confidence tracking
        self.confidence_history = []
        self.eye_contact_history = []
        
    def is_face_detection_ready(self) -> bool:
        """Check if face detection is ready"""
        return self.face_mesh is not None
    
    def is_emotion_recognition_ready(self) -> bool:
        """Check if emotion recognition is ready (simplified version)"""
        return True  # We use simple heuristics instead of ML model
    
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
            emotion_scores = self._analyze_emotions_simple(frame, face_landmarks)
            
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
        """Calculate eye contact percentage based on gaze direction and eye visibility"""
        try:
            # Get eye landmarks - ensure we have valid indices
            left_eye_points = []
            right_eye_points = []
            
            # Check if we have enough landmarks
            if len(landmarks.landmark) < 468:
                return 0
            
            for idx in self.eye_landmarks['left_eye']:
                if idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[idx]
                    left_eye_points.append([landmark.x * width, landmark.y * height])
            
            for idx in self.eye_landmarks['right_eye']:
                if idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[idx]
                    right_eye_points.append([landmark.x * width, landmark.y * height])
            
            # Need at least 4 points per eye for EAR calculation
            if len(left_eye_points) < 4 or len(right_eye_points) < 4:
                return 0
            
            # Calculate eye aspect ratio (EAR) - indicates if eyes are open
            left_ear = self._eye_aspect_ratio(left_eye_points)
            right_ear = self._eye_aspect_ratio(right_eye_points)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Eyes must be open (EAR > 0.2 typically means eyes are open)
            if ear < 0.15:
                return 0  # Eyes closed or not visible
            
            # Calculate gaze direction using iris/pupil position if available
            # For MediaPipe, we can use eye center and nose position
            left_eye_center = landmarks.landmark[33]  # Left eye center
            right_eye_center = landmarks.landmark[263]  # Right eye center
            nose_tip = landmarks.landmark[4]  # Nose tip
            
            # Calculate head orientation (facing forward = good)
            eye_center_x = (left_eye_center.x + right_eye_center.x) / 2 * width
            eye_center_y = (left_eye_center.y + right_eye_center.y) / 2 * height
            
            # Calculate how centered the face is
            center_x = width / 2
            center_y = height / 2
            
            # Distance from center (normalized)
            distance_x = abs(eye_center_x - center_x) / (width / 2)
            distance_y = abs(eye_center_y - center_y) / (height / 2)
            
            # Combined distance (0 = perfectly centered, 1 = at edge)
            normalized_distance = math.sqrt(distance_x**2 + distance_y**2)
            
            # Calculate head pose score (facing forward)
            head_pose_score = max(0, 1 - normalized_distance * 1.5)  # Penalize being off-center
            
            # Combine EAR (eye openness) and head pose (facing camera)
            # Normalize EAR to 0-1 range (typical range: 0.15-0.3)
            normalized_ear = min(1.0, (ear - 0.15) / 0.15)  # Normalize 0.15-0.3 to 0-1
            
            # Eye contact score: 60% from eye openness, 40% from head pose
            eye_contact_score = (normalized_ear * 0.6 + head_pose_score * 0.4) * 100
            
            return max(0, min(100, eye_contact_score))
            
        except Exception as e:
            print(f"Error calculating eye contact: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _eye_aspect_ratio(self, eye_points: List[List[float]]) -> float:
        """Calculate the eye aspect ratio (EAR) - indicates if eye is open"""
        try:
            if len(eye_points) < 6:
                return 0.0
            
            # Convert to numpy array for easier computation
            points = np.array(eye_points)
            
            # Calculate vertical distances (top to bottom of eye)
            # Using multiple vertical measurements for robustness
            vertical_distances = []
            if len(points) >= 6:
                # Top to bottom measurements
                vertical_distances.append(np.linalg.norm(points[1] - points[5]))
                if len(points) >= 7:
                    vertical_distances.append(np.linalg.norm(points[2] - points[4]))
            
            # Calculate horizontal distance (eye width)
            horizontal_distances = []
            if len(points) >= 4:
                horizontal_distances.append(np.linalg.norm(points[0] - points[3]))
            
            if not vertical_distances or not horizontal_distances:
                return 0.0
            
            # Average vertical and horizontal distances
            avg_vertical = np.mean(vertical_distances) if vertical_distances else 0
            avg_horizontal = np.mean(horizontal_distances) if horizontal_distances else 0
            
            if avg_horizontal == 0:
                return 0.0
            
            # Eye aspect ratio: (vertical1 + vertical2) / (2 * horizontal)
            ear = avg_vertical / avg_horizontal
            
            return max(0.0, ear)
            
        except Exception as e:
            print(f"Error calculating EAR: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def _calculate_gaze_center(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """Calculate the center point of gaze direction"""
        try:
            # Use nose tip and eye centers for gaze estimation
            nose_tip = landmarks.landmark[4]  # Nose tip
            left_eye_center = landmarks.landmark[33]  # Left eye center
            right_eye_center = landmarks.landmark[263]  # Right eye center
            
            # Calculate gaze center (simplified)
            gaze_x = (nose_tip.x + left_eye_center.x + right_eye_center.x) / 3 * width
            gaze_y = (nose_tip.y + left_eye_center.y + right_eye_center.y) / 3 * height
            
            return gaze_x, gaze_y
            
        except Exception as e:
            print(f"Error calculating gaze center: {e}")
            return width/2, height/2
    
    def _calculate_confidence(self, landmarks, width: int, height: int) -> float:
        """Calculate confidence score based on facial features"""
        try:
            confidence_factors = []
            
            # 1. Head pose (facing forward)
            head_pose_score = self._calculate_head_pose_score(landmarks, width, height)
            confidence_factors.append(head_pose_score)
            
            # 2. Eye openness
            eye_openness_score = self._calculate_eye_openness_score(landmarks, width, height)
            confidence_factors.append(eye_openness_score)
            
            # 3. Facial symmetry
            symmetry_score = self._calculate_symmetry_score(landmarks, width, height)
            confidence_factors.append(symmetry_score)
            
            # 4. Mouth position (neutral/confident)
            mouth_score = self._calculate_mouth_score(landmarks, width, height)
            confidence_factors.append(mouth_score)
            
            # Average all factors
            confidence_score = np.mean(confidence_factors) * 100
            return max(0, min(100, confidence_score))
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 50  # Default neutral score
    
    def _calculate_head_pose_score(self, landmarks, width: int, height: int) -> float:
        """Calculate head pose score (facing forward = good)"""
        try:
            # Use nose and ear positions to estimate head pose
            nose = landmarks.landmark[4]
            left_ear = landmarks.landmark[234]
            right_ear = landmarks.landmark[454]
            
            # Calculate head tilt
            head_width = abs(left_ear.x - right_ear.x) * width
            expected_width = 0.3 * width  # Expected head width ratio
            
            # Score based on how close to expected width (facing forward)
            width_ratio = head_width / expected_width
            score = max(0, 1 - abs(1 - width_ratio))
            
            return score
            
        except Exception as e:
            print(f"Error calculating head pose: {e}")
            return 0.5
    
    def _calculate_eye_openness_score(self, landmarks, width: int, height: int) -> float:
        """Calculate eye openness score"""
        try:
            # Get eye landmarks
            left_eye_points = []
            right_eye_points = []
            
            for idx in self.eye_landmarks['left_eye']:
                landmark = landmarks.landmark[idx]
                left_eye_points.append([landmark.x * width, landmark.y * height])
            
            for idx in self.eye_landmarks['right_eye']:
                landmark = landmarks.landmark[idx]
                right_eye_points.append([landmark.x * width, landmark.y * height])
            
            # Calculate EAR for both eyes
            left_ear = self._eye_aspect_ratio(left_eye_points)
            right_ear = self._eye_aspect_ratio(right_eye_points)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Normalize EAR (typical range: 0.2-0.3)
            normalized_ear = min(1.0, ear / 0.25)
            
            return normalized_ear
            
        except Exception as e:
            print(f"Error calculating eye openness: {e}")
            return 0.5
    
    def _calculate_symmetry_score(self, landmarks, width: int, height: int) -> float:
        """Calculate facial symmetry score"""
        try:
            # Compare left and right side landmarks
            left_eye_center = landmarks.landmark[33]
            right_eye_center = landmarks.landmark[263]
            nose_tip = landmarks.landmark[4]
            
            # Calculate distances
            left_distance = math.sqrt((left_eye_center.x - nose_tip.x)**2 + (left_eye_center.y - nose_tip.y)**2)
            right_distance = math.sqrt((right_eye_center.x - nose_tip.x)**2 + (right_eye_center.y - nose_tip.y)**2)
            
            # Symmetry score (closer to 1 = more symmetric)
            if left_distance + right_distance > 0:
                symmetry = 1 - abs(left_distance - right_distance) / (left_distance + right_distance)
                return max(0, symmetry)
            else:
                return 0.5
                
        except Exception as e:
            print(f"Error calculating symmetry: {e}")
            return 0.5
    
    def _calculate_mouth_score(self, landmarks, width: int, height: int) -> float:
        """Calculate mouth position score (neutral/confident)"""
        try:
            # Use mouth landmarks to estimate expression
            upper_lip = landmarks.landmark[13]
            lower_lip = landmarks.landmark[14]
            
            # Calculate mouth openness
            mouth_openness = abs(upper_lip.y - lower_lip.y)
            
            # Normalize (typical range: 0.01-0.05)
            normalized_openness = min(1.0, mouth_openness / 0.03)
            
            # Slightly open mouth (not too much, not closed) = confident
            if 0.1 < normalized_openness < 0.7:
                return 1.0
            else:
                return 0.5
                
        except Exception as e:
            print(f"Error calculating mouth score: {e}")
            return 0.5
    
    def _analyze_emotions_simple(self, frame: np.ndarray, landmarks) -> Dict[str, float]:
        """Simple emotion analysis using facial landmarks (no ML model)"""
        try:
            emotion_scores = {label: 0.0 for label in self.emotion_labels}
            
            # Extract facial features
            eye_openness = self._calculate_eye_openness_score(landmarks, frame.shape[1], frame.shape[0])
            mouth_score = self._calculate_mouth_score(landmarks, frame.shape[1], frame.shape[0])
            symmetry = self._calculate_symmetry_score(landmarks, frame.shape[1], frame.shape[0])
            
            # Simple heuristics for emotion detection
            if eye_openness > 0.8 and mouth_score > 0.8:
                emotion_scores['happy'] = 0.7
                emotion_scores['neutral'] = 0.3
            elif eye_openness < 0.3:
                emotion_scores['sad'] = 0.6
                emotion_scores['neutral'] = 0.4
            elif mouth_score < 0.3:
                emotion_scores['angry'] = 0.5
                emotion_scores['neutral'] = 0.5
            else:
                emotion_scores['neutral'] = 0.8
                emotion_scores['happy'] = 0.1
                emotion_scores['sad'] = 0.1
            
            return emotion_scores
            
        except Exception as e:
            print(f"Error analyzing emotions: {e}")
            return {label: 0.0 for label in self.emotion_labels}
    
    def _extract_face_region(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Extract face region from frame"""
        try:
            height, width = frame.shape[:2]
            
            # Get face bounding box
            x_coords = [landmark.x * width for landmark in landmarks.landmark]
            y_coords = [landmark.y * height for landmark in landmarks.landmark]
            
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            
            # Add padding
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(width, x_max + padding)
            y_max = min(height, y_max + padding)
            
            return frame[y_min:y_max, x_min:x_max]
            
        except Exception as e:
            print(f"Error extracting face region: {e}")
            return frame