import cv2
import mediapipe as mp
from deepface import DeepFace

class SmartVisionSystem:
    def __init__(self, detect_emotion=True, detect_hands=True):
        self.detect_emotion = detect_emotion
        self.detect_hands = detect_hands

        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.video_cap = cv2.VideoCapture(0)

        if self.detect_hands:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
            self.mp_drawing = mp.solutions.drawing_utils

    def analyze_emotion(self, face_img):
        try:
            result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
            return result[0]['dominant_emotion']
        except:
            return "Unknown"

    def count_fingers(self, landmarks):
        tips = [4, 8, 12, 16, 20]
        fingers = []

        if landmarks[tips[0]].x < landmarks[tips[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)

        for tip in tips[1:]:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return sum(fingers), fingers

    def get_hand_sign(self, fingers):
        if fingers == [0, 1, 1, 0, 0]:
            return "Peace ✌️"
        elif fingers == [1, 0, 0, 0, 0]:
            return "Thumbs Up 👍"
        elif fingers == [0, 1, 0, 0, 0]:
            return "Pointing ☝️"
        elif fingers == [1, 1, 1, 1, 1]:
            return "Open Palm 🖐️"
        elif fingers == [0, 0, 0, 0, 0]:
            return "Fist ✊"
        else:
            return "Gesture"

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            emotion = self.analyze_emotion(face_img) if self.detect_emotion else ""
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if emotion:
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        if self.detect_hands:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    count, fingers = self.count_fingers(hand_landmarks.landmark)
                    sign = self.get_hand_sign(fingers)
                    x = int(hand_landmarks.landmark[0].x * frame.shape[1])
                    y = int(hand_landmarks.landmark[0].y * frame.shape[0])
                    cv2.putText(frame, f"Fingers: {count} | {sign}", (x - 20, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return frame

    def run(self):
        print("Press 'a' to exit.")
        while True:
            ret, frame = self.video_cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            processed_frame = self.process_frame(frame)
            cv2.imshow("Smart Vision System", processed_frame)

            if cv2.waitKey(10) & 0xFF == ord('a'):
                break

        self.video_cap.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    system = SmartVisionSystem(detect_emotion=True, detect_hands=True)
    system.run()
