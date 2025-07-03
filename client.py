import socket
import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class HTTPClient:
    def __init__(self):
        pass

    def send_request(self, host, port, req):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall(req)
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                resp += chunk
                if b"\r\n\r\n" in resp:
                    # Get content length to read full response
                    header_part = resp.split(b"\r\n\r\n")[0]
                    headers = header_part.decode().split("\r\n")
                    content_length = 0
                    for line in headers:
                        if line.lower().startswith("content-length"):
                            content_length = int(line.split(":")[1].strip())
                    
                    # Read remaining body if needed
                    body_received = len(resp.split(b"\r\n\r\n", 1)[1])
                    while body_received < content_length:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        resp += chunk
                        body_received = len(resp.split(b"\r\n\r\n", 1)[1])
                    break
            s.close()
            return resp
        except Exception as err:
            logging.error(f"Socket error: {err}")
            return None

    def get(self, url):
        parsed = urlparse(url)
        host = parsed.hostname
        path = parsed.path or "/"
        port = parsed.port or 8885
        req = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

    def delete(self, url):
        parsed = urlparse(url)
        host = parsed.hostname
        path = parsed.path or "/"
        port = parsed.port or 8885
        req = f"DELETE {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

    def upload(self, url, filename, content):
        parsed = urlparse(url)
        host = parsed.hostname
        path = parsed.path or "/"
        port = parsed.port or 8885
        
        # Format sesuai dengan server yang ada: filename\ncontent
        body = f"{filename}\n{content}"
        req = f"POST {path} HTTP/1.0\r\nHost: {host}\r\nContent-Length: {len(body.encode())}\r\nConnection: close\r\n\r\n{body}".encode()
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

def print_menu():
    print("="*40)
    print("         HTTP CLIENT         ")
    print("="*40)
    print("1. Lihat daftar file di direktori")
    print("2. Upload file")
    print("3. Hapus file")
    print("4. Keluar")
    print("="*40)

if __name__ == "__main__":
    print("="*40)
    print("         HTTP CLIENT         ")
    print("="*40)
    print("Pilih mode server:")
    print("1. Thread Pool (8885)")
    print("2. Process Pool (8889)")
    mode = input("Pilih [1/2]: ").strip()
    if mode == "2":
        base_url = "http://127.0.0.1:8889"
    else:
        base_url = "http://127.0.0.1:8885"
    client = HTTPClient()
    while True:
        print_menu()
        pilihan = input("Pilih menu [1-4]: ").strip()
        if pilihan == "1":
            print("\nDAFTAR FILE DI SERVER:")
            url = f"{base_url}/list"
            result = client.get(url)
            print(result)
        elif pilihan == "2":
            fname = input("Nama file yang akan diupload: ").strip()
            content = input("Masukkan isi file: ").strip()
            url = f"{base_url}/upload"
            print(f"Mengupload file: {fname}")
            result = client.upload(url, fname, content)
            print(result)
        elif pilihan == "3":
            fname = input("Nama file yang ingin dihapus: ").strip()
            url = f"{base_url}/{fname}"
            result = client.delete(url)
            print(result)
        elif pilihan == "4":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")