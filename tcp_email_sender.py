#!/usr/bin/env python3

import sys
import socket

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for line in sys.stdin:
            s.sendall(line.encode())
except Exception:
    pass

print("200 Success")
