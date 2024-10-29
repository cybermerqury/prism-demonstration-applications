# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only

import logging as log

import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst


class Pipeline():

    def __init__(self, name: str, xid: int) -> None:
        self.name = name
        self.xid = xid
        self.pipeline: Gst.Pipeline = None

    # Function used to check if the pipeline has been parsed and set (ie, not
    # None) This is done to prevent the operations if the pipeline does not
    # exist
    def pipeline_exists(self) -> bool:
        if (not self.pipeline):
            log.warning(f"Pipeline does not exist. Pipeline: {self.name}")
            return False
        return True

    # Function used to set the pipeline to the string passed as argument
    def set_pipeline(self, pipeline: str) -> None:
        self.pipeline = Gst.parse_launch(pipeline)

    # Function used to start the pipeline
    def start_pipeline(self) -> None:
        if (not self.pipeline_exists()):
            return
        self._set_pipeline_bus_msgs()
        self.pipeline.set_state(Gst.State.PLAYING)

    # Function used to stop the pipeline from running
    def stop_pipeline(self) -> None:
        if (not self.pipeline_exists()):
            return
        self.pipeline.set_state(Gst.State.NULL)

    # Function used to cater for message handling for the pipeline
    def _set_pipeline_bus_msgs(self) -> None:
        if (not self.pipeline_exists()):
            return
        bus = self.pipeline.get_bus()

        # Add handling for error messages
        bus.add_signal_watch()
        bus.connect("message::error", self._on_error)

        # Enable the bus to emit sync messages, and define how to handle them
        bus.enable_sync_message_emission()
        bus.connect("sync-message::element", self._on_sync_message)

    # Callback function to handle the `prepare-window-handle` message sent by
    # the video sink. This message requests a window handle to render the video
    def _on_sync_message(self, bus: Gst.Bus, msg: Gst.Message) -> None:
        if (not self.pipeline_exists()):
            return
        if msg.get_structure().get_name() == "prepare-window-handle":
            msg.src.set_window_handle(self.xid)

    # Callback function used to display an error in case an error message is
    # emitted from the bus
    def _on_error(self, bus: Gst.Bus, msg: Gst.Message) -> None:
        if (not self.pipeline_exists()):
            return
        log.error(f"An error has occured: { msg.parse_error()}")
