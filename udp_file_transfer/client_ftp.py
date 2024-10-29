# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env python3

import logging
import socket
import sys
import time

UDP_SRC_IP = "127.0.0.1"
UDP_DST_IP = "127.0.0.1"
UDP_SRC_PORT = 20000
UDP_DST_PORT = 10_001
INPUT_FILE = "sample_file.txt"
BUFFER_SIZE_BYTES = 100

def main() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.info("UDP source IP: %s", UDP_SRC_IP)
    logging.info("UDP destination IP: %s", UDP_DST_IP)
    logging.info("UDP source port: %s", UDP_SRC_PORT)
    logging.info("UDP destination port: %s", UDP_DST_PORT)

    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_SRC_IP, UDP_SRC_PORT))

    with open(INPUT_FILE, "rb") as file:
        while True:
            file_chunk = file.read(BUFFER_SIZE_BYTES)
            if not file_chunk:
                logging.info("file transmission completed")
                break
            sock.sendto(file_chunk, (UDP_DST_IP, UDP_DST_PORT))
            logging.info("packet sent")
            time.sleep(1)


if __name__ == "__main__":
    main()
