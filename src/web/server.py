"""
server.py
---------
Fast HTTP Server serving the Modern Bento Grid UI for VoltPulse India.
Runs on port 3000.
"""

import http.server
import socketserver
import os
import sys

PORT = 3000
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

def run_server():
    os.chdir(WEB_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[VoltPulse Modern UI] Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
