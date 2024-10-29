# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env python3

import logging
import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 10_001
OUTPUT_FILE = "sample_file_received.txt"
BUFFER_SIZE_BYTES = 100

def main() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.info("Server started")

    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))


    with open(OUTPUT_FILE, "ab") as file:
        while True:
            data, _ = sock.recvfrom(BUFFER_SIZE_BYTES)
            logging.info("packet received. saving to file")
            file.write(data)


if __name__ == "__main__":
    main()
