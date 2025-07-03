from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection,address):
		rcv=""
		logging.info("Connected from {}".format(address))
		while True:
			try:
				data = connection.recv(32)
				if data:
					#merubah input dari socket (berupa bytes) ke dalam string
					#agar bisa mendeteksi \r\n
					d = data.decode()
					rcv=rcv+d
					if '\r\n\r\n' in rcv:
						headers_part, body_part = rcv.split('\r\n\r\n', 1)
						headers_lines = headers_part.split('\r\n')
						
						content_length = 0
						for line in headers_lines:
							if line.lower().startswith('content-length'):
								content_length = int(line.split(':')[1].strip())
								break
						
						while len(body_part.encode()) < content_length:
							additional_data = connection.recv(32)
							if additional_data:
								body_part += additional_data.decode()
							else:
								break
						
						rcv = headers_part + '\r\n\r\n' + body_part
						
						#end of command, proses string
						#logging.warning("data dari client: {}" . format(rcv))
						logging.info("Request from {}: {}".format(address, rcv.strip()))
						hasil = httpserver.proses(rcv)
						#hasil akan berupa bytes
						#untuk bisa ditambahi dengan string, maka string harus di encode
						hasil=hasil+"\r\n\r\n".encode()
						#logging.warning("balas ke  client: {}" . format(hasil))
						#hasil sudah dalam bentuk bytes
						connection.sendall(hasil)
						logging.info("Response sent to {}".format(address))
						rcv=""
						connection.close()
						logging.info("Connection closed for {}".format(address))
						return
					if rcv[-2:]=='\r\n':
						#end of command, proses string
						#logging.warning("data dari client: {}" . format(rcv))
						logging.info("Request from {}: {}".format(address, rcv.strip()))
						hasil = httpserver.proses(rcv)
						#hasil akan berupa bytes
						#untuk bisa ditambahi dengan string, maka string harus di encode
						hasil=hasil+"\r\n\r\n".encode()
						#logging.warning("balas ke  client: {}" . format(hasil))
						#hasil sudah dalam bentuk bytes
						connection.sendall(hasil)
						logging.info("Response sent to {}".format(address))
						rcv=""
						connection.close()
						logging.info("Connection closed for {}".format(address))
						return
				else:
					break
			except OSError as e:
				logging.error("OSError in ProcessTheClient for {}: {}".format(address, e))
				pass
		connection.close()
		logging.info("Connection closed for {} (no more data)".format(address))
		return

def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8889))
	my_socket.listen(1)

	logging.info("Process-based server listening on port 8889...")

	try:
		with ProcessPoolExecutor(20) as executor:
			while True:
				try:
					connection, client_address = my_socket.accept()
					#logging.warning("connection from {}".format(client_address))
					logging.info("New connection accepted from {}".format(client_address))
					p = executor.submit(ProcessTheClient, connection, client_address)
					the_clients.append(p)
					#menampilkan jumlah process yang sedang aktif
					jumlah = ['x' for i in the_clients if i.running()==True]
					print(jumlah)
					logging.info("Active processes count: {}".format(len(jumlah)))
				except socket.error:
					break
				except Exception as e:
					logging.error("Server error: {}".format(e))
					continue
	except KeyboardInterrupt:
		logging.info("Shutting down server...")
		print("Shutting down server...")
	finally:
		my_socket.close()
		logging.info("Server socket closed")

def main():
    Server()

if __name__ == "__main__":
    main()