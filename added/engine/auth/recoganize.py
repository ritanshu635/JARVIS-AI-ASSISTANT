import cv2
import face_recognition
import os
import numpy as np
from typing import Optional, List, Tuple
import pickle

class FaceAuthenticator:
    """Face authentication system - exactly like jarvis-main auth system"""
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        
        # Paths for storing face data
        self.faces_dir = "engine/auth/faces"
        self.encodings_file = "engine/auth/face_encodings.pkl"
        
        # Create directories if they don't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        os.makedirs("engine/auth", exist_ok=True)
        
        # Load known faces
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known face encodings from file or create from images"""
        try:
            # Try to load from pickle file first
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                    print(f"✅ Loaded {len(self.known_face_names)} known faces from file")
                    return
        except Exception as e:
            print(f"⚠️ Could not load face encodings from file: {e}")
        
        # Load from image files
        self.load_faces_from_images()
    
    def load_faces_from_images(self):
        """Load face encodings from image files in faces directory"""
        try:
            image_files = [f for f in os.listdir(self.faces_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for image_file in image_files:
                image_path = os.path.join(self.faces_dir, image_file)
                name = os.path.splitext(image_file)[0]
                
                # Load image and get face encoding
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    print(f"✅ Loaded face for: {name}")
                else:
                    print(f"⚠️ No face found in image: {image_file}")
            
            # Save encodings to file for faster loading next time
            if self.known_face_encodings:
                self.save_face_encodings()
                
        except Exception as e:
            print(f"❌ Error loading faces from images: {e}")
    
    def save_face_encodings(self):
        """Save face encodings to pickle file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print("✅ Face encodings saved to file")
        except Exception as e:
            print(f"❌ Error saving face encodings: {e}")
    
    def add_face(self, name: str, image_path: Optional[str] = None) -> bool:
        """Add a new face to the known faces"""
        try:
            if image_path and os.path.exists(image_path):
                # Load from provided image path
                image = face_recognition.load_image_file(image_path)
            else:
                # Capture from camera
                image = self.capture_face_image()
                if image is None:
                    return False
            
            # Get face encoding
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(name)
                
                # Save image to faces directory
                if image_path is None:
                    save_path = os.path.join(self.faces_dir, f"{name}.jpg")
                    cv2.imwrite(save_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                
                # Save encodings
                self.save_face_encodings()
                
                print(f"✅ Added face for: {name}")
                return True
            else:
                print("❌ No face detected in image")
                return False
                
        except Exception as e:
            print(f"❌ Error adding face: {e}")
            return False
    
    def capture_face_image(self) -> Optional[np.ndarray]:
        """Capture face image from camera"""
        try:
            video_capture = cv2.VideoCapture(0)
            
            if not video_capture.isOpened():
                print("❌ Could not open camera")
                return None
            
            print("📸 Position your face in front of the camera and press SPACE to capture, ESC to cancel")
            
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                # Display the frame
                cv2.imshow('Face Capture - Press SPACE to capture, ESC to cancel', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space key
                    # Convert BGR to RGB for face_recognition
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return rgb_frame
                elif key == 27:  # ESC key
                    break
            
            video_capture.release()
            cv2.destroyAllWindows()
            return None
            
        except Exception as e:
            print(f"❌ Error capturing face image: {e}")
            return None
    
    def authenticate_face(self, timeout: int = 30) -> int:
        """Authenticate face using camera - returns 1 for success, 0 for failure"""
        try:
            video_capture = cv2.VideoCapture(0)
            
            if not video_capture.isOpened():
                print("❌ Could not open camera for authentication")
                return 0
            
            if not self.known_face_encodings:
                print("⚠️ No known faces loaded. Please add faces first.")
                video_capture.release()
                return 0
            
            print("🔍 Face authentication started...")
            start_time = cv2.getTickCount()
            
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                # Check timeout
                elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                if elapsed_time > timeout:
                    print("⏰ Authentication timeout")
                    break
                
                # Only process every other frame to save time
                if self.process_this_frame:
                    # Resize frame for faster processing
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    # Find faces in the frame
                    self.face_locations = face_recognition.face_locations(rgb_small_frame)
                    self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                    
                    self.face_names = []
                    for face_encoding in self.face_encodings:
                        # Compare with known faces
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        
                        # Use the known face with the smallest distance
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                            name = self.known_face_names[best_match_index]
                            print(f"✅ Face authenticated: {name}")
                            video_capture.release()
                            cv2.destroyAllWindows()
                            return 1
                        
                        self.face_names.append(name)
                
                self.process_this_frame = not self.process_this_frame
                
                # Display the results (optional, can be disabled for headless operation)
                self.display_frame_with_faces(frame)
                
                # Break on ESC key
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            
            video_capture.release()
            cv2.destroyAllWindows()
            print("❌ Face authentication failed")
            return 0
            
        except Exception as e:
            print(f"❌ Face authentication error: {e}")
            return 0
    
    def display_frame_with_faces(self, frame):
        """Display frame with face recognition results"""
        try:
            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Draw a box around the face
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
            # Display the resulting image
            cv2.imshow('Face Authentication - Press ESC to cancel', frame)
            
        except Exception as e:
            print(f"❌ Display error: {e}")
    
    def list_known_faces(self) -> List[str]:
        """Get list of known face names"""
        return self.known_face_names.copy()
    
    def remove_face(self, name: str) -> bool:
        """Remove a face from known faces"""
        try:
            if name in self.known_face_names:
                index = self.known_face_names.index(name)
                self.known_face_names.pop(index)
                self.known_face_encodings.pop(index)
                
                # Remove image file if exists
                image_path = os.path.join(self.faces_dir, f"{name}.jpg")
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # Save updated encodings
                self.save_face_encodings()
                
                print(f"✅ Removed face: {name}")
                return True
            else:
                print(f"⚠️ Face not found: {name}")
                return False
                
        except Exception as e:
            print(f"❌ Error removing face: {e}")
            return False

# Global instance for compatibility with jarvis-main
face_authenticator = FaceAuthenticator()

def AuthenticateFace() -> int:
    """Main authentication function - exactly like jarvis-main"""
    return face_authenticator.authenticate_face()

def AddFace(name: str, image_path: Optional[str] = None) -> bool:
    """Add a new face - enhanced function"""
    return face_authenticator.add_face(name, image_path)

def ListFaces() -> List[str]:
    """List all known faces"""
    return face_authenticator.list_known_faces()

def RemoveFace(name: str) -> bool:
    """Remove a face"""
    return face_authenticator.remove_face(name)

# Test the face authentication system
if __name__ == "__main__":
    print("🔍 Testing Face Authentication System")
    
    # List current faces
    faces = ListFaces()
    print(f"Known faces: {faces}")
    
    if not faces:
        print("No faces found. Would you like to add a face? (y/n)")
        response = input().lower()
        if response == 'y':
            name = input("Enter name for the face: ")
            if AddFace(name):
                print(f"✅ Face added successfully for {name}")
            else:
                print("❌ Failed to add face")
    
    # Test authentication
    print("Starting face authentication test...")
    result = AuthenticateFace()
    
    if result == 1:
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed!")