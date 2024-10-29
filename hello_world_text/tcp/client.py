# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env python3
import logging
import socket
import sys
import time

TCP_SRC_IP = "127.0.0.1"
TCP_DST_IP = "127.0.0.1"
TCP_SRC_PORT = 20000
TCP_DST_PORT = 10001


root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    sock.bind((TCP_SRC_IP, TCP_SRC_PORT))
    logging.info("Bound")
    sock.connect((TCP_DST_IP, TCP_DST_PORT))
    logging.info("Connected")
    sock.send(b"Hello, world")
    logging.info("Message Sent")
    sock.close()
    time.sleep(5)
