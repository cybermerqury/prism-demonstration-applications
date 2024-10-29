# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env python3
import logging
import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 10_001

def main() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    sock = socket.socket(
        socket.AF_INET,  # Internet
        socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    logging.info("Server started")

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        logging.info("Address is: %s", addr)
        logging.info("received message: %s", data)


if __name__ == "__main__":
    main()
