# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

#!/usr/bin/env bash

pactl unload-module module-echo-cancel

echo "Press make sure that you have selected the mic and speaker you intend to use for the call."
read -rp "Press Enter to continue when done..."

pactl load-module module-echo-cancel rate=16000 aec_method=webrtc source_name=echocancel sink_name=echocancel1
pactl load-module module-echo-cancel source_name=echocancel sink_name=echocancel1
pacmd set-default-source echocancel
pacmd set-default-sink echocancel1
