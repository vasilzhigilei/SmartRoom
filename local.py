import socket
import cv2
import _pickle as pickle
import struct
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import shutil
import numpy as np

window = None
lmain = None

userNames = []
option = None

def setupTkinter():
    global window, lmain, option
    window = tk.Tk()
    window.wm_title("Facial Recognition")
    window.config(background="#f2f2f2")
    imageFrame = tk.Frame(window, width=600, height=500)
    #imageFrame.pack(padx=20, pady=10)
    imageFrame.grid(row=0,column=1)
    button = tk.Button(window, text="Create", font=("Arial", 12), width=8, command=lambda: changeMethod(1))
    button2 = tk.Button(window, text="Train", font=("Arial", 12), width=8, command=lambda: changeMethod(2))
    button3 = tk.Button(window, text="Recognize", font=("Arial", 12), width=8, command=lambda: changeMethod(0))
    button.grid(row=1, column=1, sticky='W', padx=40, pady=10)
    button2.grid(row=1, column=1, pady=10)
    button3.grid(row=1, column=1, sticky='E', padx=40, pady=10)
    label = tk.Label(window,text="User:", font=("Arial", 12), width=8)
    label.grid(row=2, column = 1, sticky='W', padx=5)
    option = ttk.Combobox(window, values=userNames, width=8)
    option.grid(row=2, column=1, sticky='W', padx=80)
    #label.pack(padx=5, pady=10, side="left", expand=True)
    lmain = tk.Label(imageFrame)
    lmain.grid(row=0, column=0)
    return True

print("Tkinter setup: " + str(setupTkinter()))

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

recognizer = cv2.face.LBPHFaceRecognizer_create()

assure_path_exists("trainer/")

# Load the trained mode
recognizer.read('trainer/trainer.yml')
# Set the font style
font = cv2.FONT_HERSHEY_SIMPLEX

faceCascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_alt.xml')

cam = cv2.VideoCapture(0)

img_counter = 0


def recognizeFaces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Get all faces from the video frame
    faces = faceCascade.detectMultiScale(gray, 1.3, 5) # why 1.2, not 1.3?

    # For each face in faces
    for (x, y, w, h) in faces:

        # Create rectangle around the face
        cv2.rectangle(frame, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)

        # Recognize the face belongs to which ID
        Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        # Check if the ID exists
        if (confidence < 50):
            Id = str(Id).format(round(100 - confidence, 2))
            '''if (Id == 0):
                Id = "Vasil {0:.2f}%".format(round(100 - confidence, 2))
                # opensesame function to open door should be implemented here
            else:
                Id = "Unknown {0:.2f}%".format(round(confidence, 2))'''
        else:
            Id = "Unknown {0:.2f}%".format(round(confidence, 2))
        # Put text describe who is in the picture
        cv2.rectangle(frame, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
        cv2.putText(frame, str(Id), (x, y - 40), font, 1, (255, 255, 255), 3)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
    return img


def create(frame, userID, count):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect frames of different sizes, list of faces rectangles
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    to_add = 0
    #os.chdir(os.path.dirname(os.path.realpath(__file__)))
    #os.listdir()
    if count == 0:
        os.makedirs("dataset/user" + str(userID))
    #assure_path_exists("dataset/user" + str(userID))
    # Loops for each faces
    for (x, y, w, h) in faces:
        # Crop the image frame into rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/user"+str(userID)+"/User." + str(userID) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

        # Display the video frame, with bounded rectangle on the person's face
        to_add = 1
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
    return img, to_add

    # To stop taking video, press 'q' for at least 100ms
    #if cv2.waitKey(100) & 0xFF == ord('q'):
    #    break

def setupUser(userID = None, name=None, level="unapproved", special=None):
    global userNames
    #assure_path_exists("resources/userlist.txt") does not work
    with open("resources/userlist.txt", "r") as file:
        data = file.readlines()

    userNames = [*range(len(data))]
    for line in data:
        lineList = line.split(',')
        userNames[data.index(line)] = lineList[1]
    option['values'] = userNames

    if userID == None:
        list = os.listdir("dataset/")
        for item in list:
            list[list.index(item)] = int(item[4:])
        list.sort()
        if not list:
            userID = 0
        else:
            userID = list[-1] + 1
    else:
        shutil.rmtree("dataset/user" + str(userID))  # deletes userID folder
    if name == None:
        name = "user" + str(userID)
    if userID >= len(data):
        data.append(str(userID) + ", " + name + ", " + level + ", " + str(special) + "\n")
    else:
        data[userID] = str(userID) + ", " + name + ", " + level + ", " + str(special) + "\n"
    with open('resources/userlist.txt', 'w') as file:
        file.writelines(data)
    file.close()
    return userID

def train(path=os.path.dirname(os.path.realpath(__file__))+"/dataset"):
    # Get all file path
    userPaths = [os.path.join(path, f) for f in os.listdir(path)]
    # Initialize empty face sample
    faceSamples = []

    # Initialize empty id
    ids = []

    # Loop all the file path
    for userPath in userPaths:
        imagePaths = [os.path.join(userPath, f) for f in os.listdir(userPath)]
        print(imagePaths)
        for imagePath in imagePaths:
            # Get the image and convert it to grayscale
            PIL_img = Image.open(imagePath).convert('L')

            # PIL image to numpy array
            img_numpy = np.array(PIL_img, 'uint8')

            # Get the image id
            id = int(os.path.split(imagePath)[-1].split(".")[1])

            # Get the face from the training images
            faces = faceCascade.detectMultiScale(img_numpy)

            # Loop for each face, append to their respective ID
            for (x, y, w, h) in faces:
                # Add the image to face samples
                faceSamples.append(img_numpy[y:y + h, x:x + w])

                # Add the ID to IDs
                ids.append(id)

    # Train the model using the faces and IDs
    recognizer.train(faceSamples, np.array(ids))

    # Save the model into trainer.yml
    assure_path_exists('trainer/')
    recognizer.save('trainer/trainer.yml')
    recognizer.read('trainer/trainer.yml')
    return True

method = 1 #0 = recognizeFaces, 1 = create, 2 = train
counter = -1

def changeMethod(newMethod):
    global method
    method = newMethod
    return True


while True:
    ret, frame = cam.read()

    if method == 0:
        img = recognizeFaces(frame)
    elif method == 1:
        if counter == -1:
            id = setupUser()
            counter = 0
        img, to_add = create(frame=frame, userID=id, count=counter)
        counter += to_add
        if counter > 29:
            method = 2
            counter = -1
    elif method ==2:
        train()
        method = 0


    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    window.update()


cam.release()
