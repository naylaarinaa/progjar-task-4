import socket
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from http import HTTPServer  # Versi http.py dengan self.logger

# Setup logging: timestamp, level, pesan
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Inisialisasi HTTPServer dengan logger
http_server = HTTPServer(logger=logging)

def handle_client(conn, addr):
    start_time = time.time()
    logging.info(f"[THREAD] Connection from {addr} accepted")
    try:
        # Baca header hingga \r\n\r\n
        header_bytes = b""
        while not header_bytes.endswith(b"\r\n\r\n"):
            chunk = conn.recv(1)
            if not chunk:
                raise ConnectionError("Client closed connection early")
            header_bytes += chunk

        header_str = header_bytes.decode("utf-8")
        # Dapatkan method & path untuk log
        request_line = header_str.split("\r\n",1)[0]
        method, path, _ = request_line.split(" ", 2)
        logging.info(f"[THREAD] Received request: {method} {path}")

        # Cari Content-Length
        content_len = 0
        for line in header_str.strip().split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_len = int(line.split(":",1)[1].strip())
                break

        # Baca body jika ada
        body_bytes = b""
        if content_len > 0:
            while len(body_bytes) < content_len:
                part = conn.recv(min(4096, content_len - len(body_bytes)))
                if not part:
                    break
                body_bytes += part

        # Gabungkan full request dan proses
        full_req = header_bytes + body_bytes
        resp = http_server.handle(full_req)
        if resp:
            # Kirim response
            conn.sendall(resp + b"\r\n\r\n")
            logging.info(
                f"[THREAD] Sent {len(resp)} bytes response to {addr}"
            )

    except Exception as err:
        logging.error(f"[THREAD] Error handling {addr}: {err}")
    finally:
        conn.close()
        elapsed = time.time() - start_time
        logging.info(f"[THREAD] Closed connection {addr} (handled in {elapsed:.3f}s)")

def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 8080
    sock.bind(("0.0.0.0", port))
    sock.listen()
    logging.info(f"Thread Pool HTTP Server listening on port {port}")

    with ThreadPoolExecutor(20) as pool:
        while True:
            conn, addr = sock.accept()
            pool.submit(handle_client, conn, addr)

if __name__ == "__main__":
    run_server()
