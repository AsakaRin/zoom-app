import socket
import cv2, imutils
import base64, threading
import numpy as np
import pickle

HOST_IP = '127.0.0.1'
PORT = 2121
BUFF_SIZE = 65536

ROOM_CLIENT = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST_IP, PORT))
server_socket.listen()
print('Listening at', (HOST_IP, PORT))

clients = []
nicknames = []

def decode_package_to_frame(packet):
	
	data = base64.b64decode(packet,' /')
	npdata = np.fromstring(data,dtype=np.uint8)
	frame = cv2.imdecode(npdata,1)

	return frame

def send_video_to_client(addr, client_socket):

	try:
		print('CLIENT {} CONNECTED!'.format(addr))
		if client_socket:

			while True:

				package = client_socket.recv(BUFF_SIZE)
				try:
					for client in ROOM_CLIENT:
						data = {
							'package': package, 
							'addr': addr
						}
						client.sendall(pickle.dumps(data))
				except:
					print(" -> Broken Pipe ! \n Exiting")
					break
			client_socket.close()
	except Exception as e:
		print(f"CLINET {addr} DISCONNECTED")		
		if client_socket:
			ROOM_CLIENT.remove(client_socket)
		pass


def broadcast(message):
	for client in clients:
		client.send(message)

def handle(client):
	while True:
		try:
			message = client.recv(1024)
			broadcast(message)
		except:
			index = clients.index(client)
			clients.remove(client)
			client.close()
			nickname = nicknames[index]
			broadcast(f'{nickname} out!'.encode('utf8'))
			nicknames.remove(nickname)
			break


def receive():
	while True:
		client, address = server_socket.accept()
		print("Connected with {}".format(str(address)))
		client.send('NICK'.encode('utf8'))
		nickname = client.recv(1024).decode("utf8")
		nicknames.append(nickname)
		clients.append(client)
		broadcast(f'{nickname} joined chat'.encode("utf8"))
		client.send('Connected to server'.encode("utf8"))
		thread = threading.Thread(target=handle, args=(client,))
		thread.start()

receive()


# while True:
	# client_socket, addr = server_socket.accept()
	# ROOM_CLIENT.append(client_socket)
	# print(ROOM_CLIENT)
	# thread = threading.Thread(target=send_video_to_client, args=(addr, client_socket))
	# thread.start()
	# print('TOTAL CLIENTS', threading.activeCount() - 1)



	