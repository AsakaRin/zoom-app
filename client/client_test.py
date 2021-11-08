import socket
import cv2, imutils, pickle
import base64
import threading
import numpy as np

HOST_IP = '127.0.0.1'
PORT = 2121
BUFF_SIZE = 65536

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

vid = cv2.VideoCapture('video_test.mp4')
WIDTH=400

client_socket.connect((HOST_IP, PORT))

def encode_frame_to_package(frame):
	encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
	package = base64.b64encode(buffer)
	return package

def decode_package_to_frame(packet):

	data = base64.b64decode(packet,' /')
	npdata = np.fromstring(data,dtype=np.uint8)
	frame = cv2.imdecode(npdata,1)

	return frame

def send_video_to_server():
	while (vid.isOpened()):

		# encode package
		_,frame = vid.read()
		frame = imutils.resize(frame,width=WIDTH)
		package = encode_frame_to_package(frame)
		try:
			client_socket.sendall(package)
		except:
			print(" -> Broken Pipe ! \n Exiting")
			break

		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):

			client_socket.close()

def recv_video_from_server():
	while True:

		data = client_socket.recv(BUFF_SIZE)
		try:
			recv_object = pickle.loads(data)
			package = recv_object['package']
			addr = recv_object['addr']

			frame = decode_package_to_frame(package)

			nameWindow = str(addr[0]) + " " + str(addr[1])
			cv2.namedWindow(nameWindow)
			cv2.imshow(nameWindow, frame)
			if cv2.waitKey(1) & 0xFF == ord('x'):
				client_socket.close()
				break
		except:
			pass


if client_socket:

	send_video_thread = threading.Thread(target=send_video_to_server)
	recv_video_thread = threading.Thread(target=recv_video_from_server)
	send_video_thread.start()
	recv_video_thread.start()
