import socket
import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SimpleHTTPClient:
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
                if resp.endswith(b"\r\n\r\n"):
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
        port = parsed.port or 8080
        req = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

    def delete(self, url):
        parsed = urlparse(url)
        host = parsed.hostname
        path = parsed.path or "/"
        port = parsed.port or 8080
        req = f"DELETE {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

    def upload(self, url, filename):
        parsed = urlparse(url)
        host = parsed.hostname
        path = parsed.path or "/"
        port = parsed.port or 8080
        if not os.path.exists(filename):
            print("File tidak ditemukan.")
            return
        with open(filename, "rb") as f:
            filedata = f.read()
        req = f"POST {path} HTTP/1.0\r\nHost: {host}\r\nContent-Length: {len(filedata)}\r\nConnection: close\r\n\r\n".encode() + filedata
        resp = self.send_request(host, port, req)
        return resp.decode("utf-8", errors="ignore") if resp else None

def print_menu():
    print("="*40)
    print("         SIMPLE HTTP CLIENT         ")
    print("="*40)
    print("1. Lihat daftar file di direktori")
    print("2. Upload file")
    print("3. Hapus file")
    print("4. Keluar")
    print("="*40)

if __name__ == "__main__":
    print("="*40)
    print("         SIMPLE HTTP CLIENT         ")
    print("="*40)
    print("Pilih mode server:")
    print("1. Thread Pool (8080)")
    print("2. Process Pool (8081)")
    mode = input("Pilih [1/2]: ").strip()
    if mode == "2":
        base_url = "http://127.0.0.1:8081"
    else:
        base_url = "http://127.0.0.1:8080"
    client = SimpleHTTPClient()
    while True:
        print_menu()
        pilihan = input("Pilih menu [1-4]: ").strip()
        if pilihan == "1":
            print("\nDAFTAR FILE DI SERVER:")
            url = f"{base_url}/server/"
            result = client.get(url)
            print(result)
        elif pilihan == "2":
            fname = input("Nama file yang ingin di-upload: ").strip()
            url = f"{base_url}/upload/{fname}"
            result = client.upload(url, fname)
            print(result)
        elif pilihan == "3":
            fname = input("Nama file yang ingin dihapus: ").strip()
            url = f"{base_url}/delete/{fname}"
            result = client.delete(url)
            print(result)
        elif pilihan == "4":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")