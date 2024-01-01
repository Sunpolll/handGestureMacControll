import pyautogui
import cv2
import time
import math
import subprocess

# Set volume using subprocess and osascript
def setVolume(volume):
    applescript = f"set volume output volume {volume}"
    subprocess.run(["osascript", "-e", applescript])

# Get current volume using subprocess and osascript 
def getCurrentVolume():
    result = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
    return int(result.stdout.strip())

# Handle method for each hand gestures
def performGestureAction(fingers, frame, hand, current_volume, volumeGesture, volumeTime, init_volume, dist, lm, mpHands, mpDraw):

    # Move the cursor if all fingers are extended
    if ["1", "1", "1", "1", "1"] == fingers:
        frame_h, frame_w, _ = frame.shape
        landmarks = hand[0].landmark
        finger_tip = landmarks[8]

        # Calculate the coordinates of the finger tip
        x = int(finger_tip.x * frame_w)
        y = int(finger_tip.y * frame_h)
        screen_w, screen_h = pyautogui.size()

        # Calculate the cursor's coordinates on the screen
        screen_x = int(finger_tip.x * screen_w * 1.25)
        screen_y = int(finger_tip.y * screen_h * 1.25)

        # Move the cursor to the calculated coordinates
        pyautogui.moveTo(screen_x, screen_y)

    # Click when thumb is closed
    elif ["1", "1", "1", "1"] == fingers[1:5]:
        pyautogui.click()
        pyautogui.sleep(1)

    # Scroll down when index and middle finger are pointing
    elif ["1", "1"] == fingers[1:3]:
        pyautogui.scroll(-5)

    # Scroll up when only index finger is pointing
    elif ["0", "1"] == fingers[0:2]:
        pyautogui.scroll(5)

    # Adjust volume when thumb is spread and index finger is pointing
    elif ["1", "1"] == fingers[0:2]:

        # Display current volume
        cv2.putText(
            img = frame, 
            text = f"volume {current_volume}", 
            org = (10, 200), 
            fontFace = cv2.FONT_HERSHEY_PLAIN, 
            fontScale = 4, 
            color = (255, 0, 255))
        
        # Check if we still in hand gesture for volume adjustment
        if volumeGesture:

            # Fix time interval for adjusting volume for not too often
            if time.time() - volumeTime >= 0.5:
                tf = [lm[4].x, lm[4].y]
                pf = [lm[8].x, lm[8].y]
                if dist:
                    # Calculate distance between edge of thumb and index finger
                    current_dist = math.dist(tf, pf)

                    # Adjust current volume with normalize current_dist 
                    current_volume = init_volume + round((current_dist - dist) * 450)

                    # Check if current_volume out of range
                    if current_volume > 100: 
                        current_volume = 100
                    elif current_volume < 0: 
                        current_volume = 0
                    
                    # Set volume
                    setVolume(current_volume)

                # When doing this hand gesture for the first time will set dist for reference
                else:
                    dist = math.dist(tf, pf)

        # If it first time for a while reset variable
        else:
            init_volume = getCurrentVolume()
            current_volume = init_volume
            volumeGesture = True
            volumeTime = time.time()
    else:
        volumeGesture = False
        dist = None
    mpDraw.draw_landmarks(frame, hand[0], mpHands.HAND_CONNECTIONS)

    return current_volume, volumeGesture, volumeTime, init_volume, dist