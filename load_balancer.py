import http.server
import socketserver
import requests
import threading
from urllib.parse import urlparse, parse_qs

backends = [
    'http://10.8.195.10:8889',
    'http://10.8.195.10:8890',
    'http://10.8.195.10:8891'
]

room_mapping = {}  # room_id → backend server
current_backend = 0
lock = threading.Lock()

class LoadBalancerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global current_backend
        room_id = self.get_room_id_from_path()
        target_backend = self.get_backend_for_room(room_id)

        try:
            r = requests.get(f"{target_backend}{self.path}")
            self.send_response(r.status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(r.content)
        except Exception as e:
            self.send_error(502, f"Backend error: {e}")

    def do_POST(self):
        global current_backend
        room_id = self.get_room_id_from_path()
        target_backend = self.get_backend_for_room(room_id)

        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)

        try:
            r = requests.post(f"{target_backend}{self.path}", data=post_data)
            self.send_response(r.status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(r.content)
        except Exception as e:
            self.send_error(502, f"Backend error: {e}")

    def get_backend_for_room(self, room_id):
        global current_backend
        with lock:
            if room_id and room_id in room_mapping:
                return room_mapping[room_id]
            else:
                target = backends[current_backend]
                current_backend = (current_backend + 1) % len(backends)
                if room_id:
                    room_mapping[room_id] = target
                return target

    def get_room_id_from_path(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        return qs.get("room", [None])[0]

def run_load_balancer():
    PORT = 8881
    with socketserver.ThreadingTCPServer(("", PORT), LoadBalancerHandler) as httpd:
        print(f"Load Balancer running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_load_balancer()
