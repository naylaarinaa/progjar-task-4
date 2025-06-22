from socket import *
import socket
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer
import logging

http_server = HttpServer(logging)

def handle_client(conn, addr):
    try:
        header_bytes = b""
        while True:
            chunk = conn.recv(1)
            if not chunk:
                conn.close()
                return
            header_bytes += chunk
            if header_bytes.endswith(b"\r\n\r\n"):
                break
        header_str = header_bytes.decode("utf-8")
        lines = header_str.strip().split("\r\n")
        content_len = 0
        for line in lines:
            if line.lower().startswith("content-length:"):
                content_len = int(line.split(":", 1)[1].strip())
                break
        body_bytes = b""
        if content_len > 0:
            while len(body_bytes) < content_len:
                left = content_len - len(body_bytes)
                part = conn.recv(min(4096, left))
                if not part:
                    break
                body_bytes += part
        full_req = header_bytes + body_bytes
        resp = http_server.handle(full_req)
        if resp:
            resp += b"\r\n\r\n"
            conn.sendall(resp)
        conn.close()
    except Exception as err:
        logging.error(f"Client error {addr}: {err}")
        conn.close()

def run_server():
    clients = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 8081
    sock.bind(("0.0.0.0", port))
    sock.listen(1)
    logging.basicConfig(level=logging.INFO)
    print(f"Process Pool HTTP Server listening on port {port}")
    with ProcessPoolExecutor(20) as pool:
        while True:
            conn, addr = sock.accept()
            fut = pool.submit(handle_client, conn, addr)
            clients.append(fut)
            active = [f for f in clients if f.running()]
            print(f"Active processes: {len(active)}")

def main():
    run_server()

if __name__ == "__main__":
    main()