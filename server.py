'''
Server socket receives webcam packets from client. The server then tries to recognize any faces with a given
confidence level using OpenCV. The recognition footage is then displayed in a simple tkinter GUI.
'''
import socket
import cv2
import _pickle as pickle
import struct
import os

import tkinter as tk
from PIL import Image, ImageTk

window = tk.Tk()
window.wm_title("Facial Recognition")
window.config(background="#f2f2f2")
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.pack(padx=20,pady=10)
button=tk.Button(window, text="Create", font=("Arial", 12), width=8)
button2=tk.Button(window, text="Train", font=("Arial", 12), width=8)
button3=tk.Button(window, text="Recognize", font=("Arial", 12), width=8)
button.pack(padx=5, pady=10, side="left", expand=True);
button2.pack(padx=5, pady=10, side="left", expand=True);
button3.pack(padx=5, pady=10, side="left", expand=True)
lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)

HOST='127.0.0.1'
PORT=8888

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
# Create Local Binary Patterns Histograms for face recognization
recognizer = cv2.face.LBPHFaceRecognizer_create()

assure_path_exists("trainer/")

# Load the trained mode
recognizer.read('trainer/trainer.yml')
# Set the font style
font = cv2.FONT_HERSHEY_SIMPLEX


faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

data = b""
payload_size = struct.calcsize(">L")
print("payload_size: {}".format(payload_size))

while True:
    while len(data) < payload_size:
        #print("Recv: {}".format(len(data)))
        data += conn.recv(4096)
    #print("Done Recv: {}".format(len(data)))
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    #print("msg_size: {}".format(msg_size))
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # Convert the captured frame into grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Get all faces from the video frame
    faces = faceCascade.detectMultiScale(gray, 1.2, 5)

    # For each face in faces
    for (x, y, w, h) in faces:

        # Create rectangle around the face
        cv2.rectangle(frame, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)

        # Recognize the face belongs to which ID
        Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        # Check if the ID exists
        if (confidence < 50):
            if (Id == 1):
                Id = "Vasil {0:.2f}%".format(round(100 - confidence, 2))
        else:
            Id = "Unknown {0:.2f}%".format(round(confidence, 2))
        # Put text describe who is in the picture
        cv2.rectangle(frame, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
        cv2.putText(frame, str(Id), (x, y - 40), font, 1, (255, 255, 255), 3)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    window.update()