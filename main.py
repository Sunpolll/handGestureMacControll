import cv2
import time
import mediapipe as mp
from gestureAction import performGestureAction, getCurrentVolume

# Initialize time
volumeTime = time.time()
start_time = time.time()

# Initialize volume
current_volume = getCurrentVolume()
init_volume = current_volume
volumeGesture = False
dist = None

# initialize mediapipe
mpHands = mp.solutions.hands # hand detect module
hands = mpHands.Hands(
    max_num_hands=1,                
    min_detection_confidence=0.8, 
    min_tracking_confidence = 0.8)
mpDraw = mp.solutions.drawing_utils 

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    _, frame = cap.read()

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB color
    convertedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get height, width from current frame
    h, w, _ = frame.shape

    # Get hand landmark prediction
    hand = hands.process(convertedFrame).multi_hand_landmarks

    # Ref point of each finger from index finger to pinky for finding which finger is pointing
    fingerPoints = [(6,8),(10,12),(14,16),(18,20)]

    if hand:
        # Get landmark of each finger point
        lm = hand[0].landmark

        # Initialize fingers variable with 0 if spreading thumb else 1
        # calculate using edge and middle of thumb horizontally
        fingers = ["0" if lm[4].x > lm[3].x else "1"]

        # Append value for the less of the fingers
        for fingerPoint in fingerPoints:
            # calculate using edge and middle of current finger vertically
            fingers.append("1" if lm[fingerPoint[0]].y > lm[fingerPoint[1]].y else "0")

        # Display current pointing finger
        cv2.putText(
            img=frame,
            text=" ".join(fingers),
            org=(10,70),
            fontFace=cv2.FONT_HERSHEY_PLAIN,
            fontScale=3,
            color=(255, 0, 255))
        
        # Call performGestureAction function
        current_volume, volumeGesture, volumeTime, init_volume, dist = performGestureAction(
        fingers, frame, hand, current_volume, volumeGesture, volumeTime, init_volume, dist, lm, mpHands, mpDraw
        )

    # Show the final output
    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()

cv2.destroyAllWindows()
