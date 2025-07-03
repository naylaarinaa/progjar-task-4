import sys
import os.path
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.types={}
		self.types['.pdf']='application/pdf'
		self.types['.jpg']='image/jpeg'
		self.types['.txt']='text/plain'
		self.types['.html']='text/html'
	def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")

		response_headers=''
		for i in resp:
			response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
		if (type(messagebody) is not bytes):
			messagebody = messagebody.encode()

		response = response_headers.encode() + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		
		requests = data.split("\r\n")
		#print(requests)

		baris = requests[0]
		#print(baris)

		all_headers = [n for n in requests[1:] if n!='']

		j = baris.split(" ")
		try:
			method=j[0].upper().strip()
			if (method=='GET'):
				object_address = j[1].strip()
				return self.http_get(object_address, all_headers)
			if (method=='POST'):
				object_address = j[1].strip()
				return self.http_post(object_address, all_headers)
			if (method=='DELETE'):
				object_address = j[1].strip()
				return self.http_delete(object_address, all_headers)
			else:
				return self.response(400,'Bad Request','',{})
		except IndexError:
			return self.response(400,'Bad Request','',{})
	def http_get(self,object_address,headers):
		files = glob('./*')
		#print(files)
		thedir='./'
		if (object_address == '/'):
			return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

		if (object_address == '/video'):
			return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
		if (object_address == '/santai'):
			return self.response(200,'OK','santai saja',dict())

		if (object_address == '/list'):
			file_list = os.listdir(thedir)
			list_text = "\n".join(file_list)
			headers_response = {'Content-Type': 'text/plain'}
			return self.response(200,'OK',list_text,headers_response)

		object_address=object_address[1:]
		if thedir+object_address not in files:
			return self.response(404,'Not Found','',{})
		fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
		#harus membaca dalam bentuk byte dan BINARY
		isi = fp.read()
		
		fext = os.path.splitext(thedir+object_address)[1]
		if fext in self.types:
			content_type = self.types[fext]
		else:
			content_type = 'application/octet-stream'
		
		headers={}
		headers['Content-type']=content_type
		
		return self.response(200,'OK',isi,headers)
	def http_post(self,object_address,headers):
		if object_address == '/upload':
			try:
				body = headers[-1] if headers else ""
				parts = body.split("\n", 1)
				if len(parts) != 2:
					return self.response(400,'Bad Request','Format upload salah',{})
				
				filename = parts[0].strip()
				content = parts[1]
				
				with open(filename, 'w') as f:
					f.write(content)
				
				success_message = 'File {} berhasil diupload'.format(filename)
				return self.response(200,'OK',success_message,{})
			except Exception as e:
				error_message = str(e)
				return self.response(500,'Internal Server Error',error_message,{})
		else:
			headers ={}
			isi = "kosong"
			return self.response(200,'OK',isi,headers)
	
	def http_delete(self,object_address,headers):
		filename = object_address.lstrip("/")
		return self.handle_delete(filename)
	
	def handle_delete(self, filename):
		try:
			if not os.path.exists(filename):
				return self.response(404,'Not Found','File tidak ditemukan',{})
			os.remove(filename)
			success_message = 'File {} berhasil dihapus'.format(filename)
			return self.response(200,'OK',success_message,{})
		except Exception as e:
			error_message = str(e)
			return self.response(500,'Internal Server Error',error_message,{})
		
			 	
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET testing.txt HTTP/1.0')
	print(d)
	d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
#	d = httpserver.http_get('testing.txt')
#	print(d)