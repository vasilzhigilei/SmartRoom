'''
Client side of the client/server webcam socket system. Reads webcam footage and sends encoded packets
of frames to server for further analysis.
'''
import cv2
import socket
import struct
import _pickle as pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8888))
connection = client_socket.makefile('wb')

cam = cv2.VideoCapture(0)

img_counter = 0

encode_param = [int(cv2.IMWRITE_PNG_STRATEGY_DEFAULT), 90]

while True:
    ret, frame = cam.read()
    result, frame = cv2.imencode('.png', frame, encode_param) #slightly faster video (mainly when no faces), but much bigger network send
    data = pickle.dumps(frame, 0)
    size = len(data)

    client_socket.sendall(struct.pack(">L", size) + data)
    img_counter += 1

cam.release()