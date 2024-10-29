# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env python3
import logging
import socket
import sys

HOST = "127.0.0.1"
PORT = 10001

def main() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    logging.info("Listening")
    while True:
        conn, addr = sock.accept()
        with conn:
            data = conn.recv(1024)
            logging.info("Address is: %s",addr)
            logging.info("received message: %s", data)

if __name__ == "__main__":
    main()
