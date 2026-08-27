import cv2
import pytesseract
import subprocess
import time
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def speak(message):

    command = f'''
    Add-Type -AssemblyName System.Speech
    $speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $speaker.Speak("{message}")
    '''

    subprocess.run(
        ["powershell", "-Command", command],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def detect_color(frame, x1, y1, x2, y2):

    area = frame[y1:y2, x1:x2]

    hsv = cv2.cvtColor(area, cv2.COLOR_BGR2HSV)

    hue = hsv[:, :, 0].mean()
    saturation = hsv[:, :, 1].mean()
    brightness = hsv[:, :, 2].mean()

    if brightness < 50:
        return "black"

    if saturation < 30 and brightness > 180:
        return "white"

    if saturation < 30:
        return "gray"

    if hue < 10 or hue >= 170:
        return "red"

    if hue < 20:
        return "orange"

    if hue < 35:
        return "yellow"

    if hue < 85:
        return "green"

    if hue < 130:
        return "blue"

    if hue < 160:
        return "purple"

    return "pink"
    
camera = cv2.VideoCapture(1) # Access inbuilt camera. 0 for internal & 1 for external

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Sets the frame width to 1280
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Sets the frame height to 720

# Checks if camera is detected and opened
if not camera.isOpened():
    print("Could not open camera!") # If camera is not detected an error messaged is printed to the screen
    exit()                          # Exits the program

def detect_object(frame): 
    # Ask YOLO to detect object
    result = model(frame, verbose=False) # Acessing YOLO model, passing frame & setting verbose to False to not log objects
        
    # Get detected object names
    detected_objects = []
    for box in result[0].boxes:
        class_id = int(box.cls[0])
        object_name = model.names[class_id] 
        
        if object_name not in detected_objects:
            detected_objects.append(object_name)

    # Draw detected objects
    anotation_texted_frame = result[0].plot() # Gets the name of the object & displays to the screen.  
        
    return detected_objects,anotation_texted_frame

print("-------===========---------")
print("SeeSpeak") # Prints the title of the window to the screen
print("Press s to speak")
print("Press c for color detection")
print("Press q to exit")     # Prints to the screen thw instruction to exit  
print("-------===========---------")

# Main camera loop
while True:
    success, frame = camera.read() # Sucess stores boolean of the camera's read function & frame stores the data

    # If camera is not readable then error message is printed to the screen 
    if not success:
        print("Could not read camera!")
        break

    # frame = cv2.flip(frame, 1) # 0 is vertical flip, 1 is horizontal flip
    
    detected_objects, anotation_texted_frame = detect_object(frame)

    # Showing instructions
    cv2.putText(anotation_texted_frame, "S: speak | C: color | Q: quit", (20, 75), cv2.FONT_ITALIC, 0.6, (244,196,48), 2)

    height, width = frame.shape[:2]
    box_width = 100
    box_height = 100

    x1 = width // 2 - box_width // 2
    y1 = height // 2 - box_height // 2

    x2 = x1 + box_width
    y2 = y1 + box_height

    cv2.rectangle(anotation_texted_frame, (x1, y1),(x2, y2),(255, 255, 255),3)

    cv2.putText(anotation_texted_frame,"Place object inside the box",(x1, y1 - 15),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255, 255, 255),2)
        
    # Window to show camera
    cv2.imshow("Spy Master", anotation_texted_frame) # Opens a window titled 'Spy Master
   
    # Check if s is pressed, make it speak object names
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        if len(detected_objects) == 0:
            message = "No known object detected!"
        else:
            message = f"I can see {detected_objects}"

        speak(message)

    elif key == ord("c"):
       
        color = detect_color(frame, x1, y1, x2, y2)
        speak(f"I see {color} color.")
       
    elif key == ord("q"):  # Waits for keyboard input for 1 millisecond & if input is the 'q' key the entire loop is exited
        print("q pressed")
        break

# Clean up
camera.release()        # Releases camera
cv2.destroyAllWindows() # Destroys all windows

# The main function of the entire program
def main():
    pass

if __name__ == '__main__':
    main()