import cv2
import mediapipe as mp
import numpy as np

def test_face_detection():
    print("OpenCV version:", cv2.__version__)
    print("MediaPipe version:", mp.__version__)
    print("NumPy version:", np.__version__)
    
    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )

    # Try to open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam. Testing with a blank image instead.")
        # Create a blank test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = 200  # Light gray background
        frame = test_image
    else:
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("Could not read frame from webcam. Using test image.")
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = 200

    # Process the frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        print(f"\nFace detected successfully!")
        print(f"Number of landmarks: {len(face_landmarks.landmark)}")
        
        # Check for iris landmarks (indices 468-477)
        iris_landmarks = list(range(468, 478))
        iris_present = all(i < len(face_landmarks.landmark) for i in iris_landmarks)
        print(f"Iris landmarks present: {iris_present}")
        
        # Verify eye landmarks
        left_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        right_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        all_eye_landmarks_present = all(
            i < len(face_landmarks.landmark) 
            for i in left_eye_indices + right_eye_indices
        )
        print(f"All eye landmarks present: {all_eye_landmarks_present}")
    else:
        print("\nNo face detected in test frame.")
        print("Try running the script again while facing the camera,")
        print("or test with a photo containing a clear face.")

if __name__ == "__main__":
    test_face_detection()