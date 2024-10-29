# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

import ipaddress
import logging as log

import gi

import video_call

gi.require_version("Gst", "1.0")

from gi.repository import Gst


def main() -> None:
    log.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                    level=log.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
    Gst.init(None)
    call = video_call.VideoCall()


if __name__ == "__main__":
    main()
