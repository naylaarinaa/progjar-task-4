import os
from datetime import datetime

class HTTPServer:
    def __init__(self, logger=None):
        self.mime_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain",
            ".html": "text/html"
        }
        self.logger = logger
        self.root_dir = "./"
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def build_response(self, code=404, msg="Not Found", body=bytes(), headers={}):
        now = datetime.now().strftime("%c")
        lines = [
            f"HTTP/1.0 {code} {msg}\r\n",
            f"Date: {now}\r\n",
            "Connection: close\r\n",
            "Server: server/1.0\r\n",
            f"Content-Length: {len(body)}\r\n"
        ]
        for k, v in headers.items():
            lines.append(f"{k}:{v}\r\n")
        lines.append("\r\n")
        resp_hdr = "".join(lines)
        if not isinstance(body, bytes):
            body = body.encode()
        return resp_hdr.encode() + body

    def handle(self, req_data):
        if b"\r\n\r\n" in req_data:
            hdrs, body = req_data.split(b"\r\n\r\n", 1)
            hdrs = hdrs.decode("utf-8")
        else:
            hdrs = req_data
            body = b""
        lines = hdrs.split("\r\n")
        req_line = lines[0] if lines else ""
        headers = lines[1:] if len(lines) > 1 else []
        parts = req_line.split(" ")
        try:
            method = parts[0].upper().strip()
            if method == "GET":
                return self.list_dir("", headers)
            elif method == "POST":
                path = parts[1].strip()
                if path.startswith("/upload"):
                    return self.do_upload(path, headers, body)
                return self.do_post(path, headers, body)
            elif method == "DELETE":
                path = parts[1].strip()
                return self.do_delete(path, headers)
            else:
                return self.build_response(400, "Bad Request", "", {})
        except Exception:
            return self.build_response(400, "Bad Request", "", {})

    def list_dir(self, rel_path, headers):
        dir_path = os.path.abspath(self.root_dir)
        try:
            files = os.listdir(dir_path)
            body = "\n".join(files)
            return self.build_response(200, "OK", body, {"Content-type": "text/plain"})
        except Exception as err:
            return self.build_response(404, "Not Found", str(err), {"Content-type": "text/plain"})

    def do_upload(self, path, headers, body):
        if path.startswith("/upload/"):
            fname = path[8:]
        else:
            fname = path.lstrip("/")
        if not fname:
            return self.build_response(400, "Bad Request", "No filename", {"Content-type": "text/plain"})
        safe_name = os.path.basename(fname).lower()  # rename jadi lowercase
        fpath = os.path.join(self.root_dir, safe_name)
        try:
            with open(fpath, "wb+") as f:
                f.write(body)
            return self.build_response(
                201, "Created",
                f"File {fname} diupload dan di-rename jadi {safe_name} ({len(body)} bytes)",
                {"Content-type": "text/plain"}
            )
        except Exception as err:
            return self.build_response(500, "Internal Server Error", f"Upload error: {err}", {"Content-type": "text/plain"})

    def do_delete(self, path, headers):
        if path.startswith("/delete/"):
            fname = path[8:]
        else:
            fname = path.lstrip("/")
        if not fname:
            return self.build_response(400, "Bad Request", "No filename", {"Content-type": "text/plain"})
        fpath = os.path.join(self.root_dir, fname)
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
                return self.build_response(200, "OK", f"File {fname} deleted", {"Content-type": "text/plain"})
            else:
                return self.build_response(404, "Not Found", f"File {fname} not found", {"Content-type": "text/plain"})
        except Exception as err:
            return self.build_response(500, "Internal Server Error", f"Delete error: {err}", {"Content-type": "text/plain"})