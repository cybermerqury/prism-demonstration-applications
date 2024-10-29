# SPDX-FileCopyrightText: © 2024 Merqury Cybersecurity Ltd <info@merqury.eu>
# SPDX-License-Identifier: AGPL-3.0-only


import ipaddress
import logging as log

import gi
import pipeline

gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GdkX11", "3.0")
gi.require_version("GstVideo", "1.0")

from typing import Dict

from gi.repository import Gdk, GdkPixbuf, Gst, GstVideo, Gtk
from v4l2py.device import iter_video_capture_devices


class VideoCall():

    def __init__(self) -> None:
        # Variable Definitions
        css_path = "Resources/style.css"
        taskbar_icon_path = "Resources/Images/logo_mqy.svg"
        grid_spacing = 10

        # Create a window
        self.window = Gtk.Window(title="Video Call")
        self.window.connect("destroy", self._quit)
        self.window.set_resizable(False)

        # Create a grid to store everything
        grid = Gtk.Grid()
        grid.set_row_spacing(grid_spacing)
        grid.set_column_spacing(grid_spacing)
        grid.set_margin_start(grid_spacing)
        grid.set_margin_end(grid_spacing)
        grid.set_margin_top(grid_spacing)
        grid.set_margin_bottom(grid_spacing)
        self.window.add(grid)

        # Create DrawingArea for video we are sending
        self.tx_vid = Gtk.DrawingArea()
        self.tx_vid.set_size_request(380, 100)
        self.tx_vid.set_hexpand(True)
        self.tx_vid.set_vexpand(True)
        grid.attach(self.tx_vid, 2, 1, 1, 1)

        # Create a DrawingArea for the video we are receiving
        self.rx_vid = Gtk.DrawingArea()
        self.rx_vid.set_size_request(640, 480)
        self.rx_vid.set_hexpand(True)
        self.rx_vid.set_vexpand(True)
        grid.attach(self.rx_vid, 0, 0, 3, 1)

        # Create the text inputs which are required
        grid.attach(self._generate_first_column(), 0, 1, 1, 1)

        # Create buttons for start, stop and exit
        grid.attach(self._generate_second_column(), 1, 1, 1, 1)

        # Create a footer
        grid.attach(self._generate_footer(), 0, 3, 3, 1)

        # Add a taskbar icon
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(taskbar_icon_path)
        self.window.set_icon(pixbuf)

        # Apply CSS styling
        self._apply_css(css_path)

        # Note: We must show all before continuing, because the pipelines need
        # a handle to determine where to show the video data
        self.window.show_all()

        # Pipelines
        self._generate_pipelines()

        Gtk.main()

    # Callback function for when the user exits the application button.
    # The function stops all pipelines, stops the gtk main loop and exits
    def _quit(self, widget: Gtk.Widget) -> None:
        log.info("Exiting Application...")
        self.client.stop_pipeline()
        self.server.stop_pipeline()
        Gtk.main_quit()
        log.info("Application Exited!")

    # Function to generate a grid for the ip and port labels and entries
    def _generate_first_column(self) -> Gtk.Grid:
        start_call_image = "Resources/Images/call.png"

        # Generat the destination IP input
        label_dst_ip = Gtk.Label(label="Destination IP")
        label_dst_ip.set_hexpand(True)
        style_context = label_dst_ip.get_style_context()
        style_context.add_class("header-label")

        self.entry_dst_ip = Gtk.Entry()
        self.entry_dst_ip.set_hexpand(True)
        self.entry_dst_ip.set_vexpand(True)

        box_dst_ip = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_dst_ip.pack_start(label_dst_ip, True, True, 0)
        box_dst_ip.pack_start(self.entry_dst_ip, True, True, 0)

        # Generate the audio port inputs
        self.entry_src_port_audio = Gtk.Entry()
        self.entry_dst_port_audio = Gtk.Entry()
        self.entry_rx_port_audio = Gtk.Entry()
        audio_inputs = self._generate_inputs_ports("Audio",
                                                   self.entry_src_port_audio,
                                                   self.entry_dst_port_audio,
                                                   self.entry_rx_port_audio)

        # Generate the start call button
        self.start = self._generate_button("Start Call", start_call_image)
        self.start.connect("clicked", self._start_call)
        style_context = self.start.get_style_context()
        style_context.add_class("start-button")

        # Generate a grid and attach everything to it
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.attach(box_dst_ip, 0, 0, 1, 1)
        grid.attach(audio_inputs, 0, 2, 2, 1)
        grid.attach(self.start, 0, 3, 2, 1)

        return grid

    # Function to generate labels and entries for the ports. The input string
    # is used as a title header
    def _generate_inputs_ports(self, title: str, entry_src_port: Gtk.Entry,
                               entry_dst_port: Gtk.Entry,
                               entry_rx_port: Gtk.Entry) -> Gtk.Grid:
        label_title = Gtk.Label(label=title)
        label_title.set_vexpand(True)
        label_title.set_hexpand(True)
        style_context = label_title.get_style_context()
        style_context.add_class("header-label")

        label_trx_src_port = Gtk.Label(label="Trx Src Port: ")
        label_trx_src_port.set_halign(Gtk.Align.END)

        label_trx_dst_port = Gtk.Label(label="Trx Dst Port: ")
        label_trx_dst_port.set_halign(Gtk.Align.END)

        label_rx_port = Gtk.Label(label="Rx Port: ")
        label_rx_port.set_halign(Gtk.Align.END)

        grid = Gtk.Grid()
        grid.attach(label_title, 0, 0, 2, 1)
        grid.attach(label_trx_src_port, 0, 1, 1, 1)
        grid.attach(entry_src_port, 1, 1, 1, 1)
        grid.attach(label_trx_dst_port, 0, 2, 1, 1)
        grid.attach(entry_dst_port, 1, 2, 1, 1)
        grid.attach(label_rx_port, 0, 3, 1, 1)
        grid.attach(entry_rx_port, 1, 3, 1, 1)

        return grid

    # Function used to get a list of webcam devices
    # Note: this will only define the list once and keep returning the same list
    def _get_webcam_list(self) -> Dict[str, str]:
        if (not hasattr(self, 'device_list')):
            self.device_list = {}
            for device in iter_video_capture_devices():
                device.open()
                self.device_list[str(device.info.card)] = str(
                    str(device.filename))
                device.close()

        return self.device_list

    # Callback function used to handle when a user changes a webcam from
    # the ComboBox
    def _switch_webcam(self, combo: Gtk.ComboBoxText) -> None:
        selection = combo.get_active_text()
        if selection is None:
            return

        webcam_filename = self._get_webcam_list()[selection]
        if webcam_filename is None:
            log.error("Unable to find webcam in list of webcams")
            return

        self.webcam_device = webcam_filename
        if (not self.is_trx):
            self._start_server_no_tx()
        else:
            self._start_server_tx()

    # Function used to generate the 2nd column in the GUI
    def _generate_second_column(self) -> Gtk.Grid:
        hangup_image_path = "Resources/Images/hangup.png"

        # Generate a webcam input combo box
        label_webcam = Gtk.Label(label="Webcam Input")
        style_context = label_webcam.get_style_context()
        style_context.add_class("header-label")

        webcam_combo = Gtk.ComboBoxText()
        for device_name in self._get_webcam_list():
            webcam_combo.append_text(device_name)
        webcam_combo.set_active(0)
        # Note: Connect AFTER setting the active, so as not to trigger the
        # callback function
        webcam_combo.connect("changed", self._switch_webcam)

        box_webcam = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_webcam.pack_start(label_webcam, True, True, 0)
        box_webcam.pack_start(webcam_combo, True, True, 0)

        # Generate Input for Video Ports
        self.entry_src_port_video = Gtk.Entry()
        self.entry_dst_port_video = Gtk.Entry()
        self.entry_rx_port_video = Gtk.Entry()
        video_inputs = self._generate_inputs_ports("Video",
                                                   self.entry_src_port_video,
                                                   self.entry_dst_port_video,
                                                   self.entry_rx_port_video)

        # Generate a Stop Call button
        self.stop = self._generate_button("Stop Call", hangup_image_path)
        self.stop.set_sensitive(False)
        self.stop.connect("clicked", self._end_call)
        style_context = self.stop.get_style_context()
        style_context.add_class("stop-button")

        # Generate a grid and attach everything to it
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_row_homogeneous(False)

        grid.attach(box_webcam, 0, 0, 1, 1)
        grid.attach(video_inputs, 0, 2, 2, 1)
        grid.attach(self.stop, 0, 3, 1, 1)

        return grid

    # Helper function to create a button
    def _generate_button(self, label_text: str, image_path: str) -> Gtk.Button:
        button = Gtk.Button()

        image = self._load_scaled_image(60, image_path)

        # Note: Some of the labels below are filler labels, used to
        # create the desired spacing
        box = Gtk.Box()
        box.pack_start(Gtk.Label(), True, True, 0)
        box.pack_start(image, False, False, 0)
        box.pack_start(Gtk.Label(label="    "), False, False, 0)
        box.pack_start(Gtk.Label(label=label_text), False, False, 0)
        box.pack_start(Gtk.Label(label="    "), True, True, 0)
        box.set_homogeneous(False)

        button.add(box)
        button.set_relief(Gtk.ReliefStyle.NONE)

        return button

    # Helper function to load a scaled image from file
    def _load_scaled_image(self, height: int, path: str) -> Gtk.Image:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        width = int(pixbuf.get_width() * (height / pixbuf.get_height()))
        scaled_pixbuf = pixbuf.scale_simple(width, height,
                                            GdkPixbuf.InterpType.BILINEAR)
        return Gtk.Image.new_from_pixbuf(scaled_pixbuf)

    # Function used to generate a box with the footer
    def _generate_footer(self) -> Gtk.Box:
        mqy_logo_path = "Resources/Images/logo_mqy_name.svg"
        prisim_logo_path = "Resources/Images/logo_prism.svg"

        box_footer = Gtk.Box(spacing=10)

        logo_mqy = self._load_scaled_image(80, mqy_logo_path)
        logo_prism = self._load_scaled_image(120, prisim_logo_path)

        box_footer.pack_start(logo_mqy, True, True, 0)
        box_footer.pack_start(logo_prism, True, True, 0)

        return box_footer

    # Function used to load and apply a CSS style sheet
    def _apply_css(self, path: str) -> None:
        # Load the CSS style
        provider = Gtk.CssProvider()
        provider.load_from_path("Resources/style.css")

        # Apply the CSS style to the GTK window
        style_context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Helper function to create the pipelines and link them to the drawing area
    def _generate_pipelines(self) -> None:
        self.webcam_device = list(self._get_webcam_list().values())[0]
        if (self.webcam_device is None):
            self._show_error_popup("No webcam device has been found",
                                   "Please connect a webcam to make a call!")
            log.error("No webcam found.")
            exit()

        xid_server = self.tx_vid.get_property("window").get_xid()
        self.is_trx = False
        self.server = pipeline.Pipeline("Server", xid_server)
        self._start_server_no_tx()

        xid_client = self.rx_vid.get_property("window").get_xid()
        self.client = pipeline.Pipeline("Client", xid_client)

    # Function used to show a popup (which disables the main window) if there
    # are missing fields and the user clicks start
    def _show_error_popup(self, error_details: str,
                          error_resolution: str) -> None:
        popup = Gtk.Dialog(title="Error", parent=self.window)
        popup.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        popup.set_default_size(600, 50)

        titlebar = Gtk.HeaderBar()
        titlebar.set_title("Error")
        titlebar.set_show_close_button(False)
        popup.set_titlebar(titlebar)

        label_error_details = Gtk.Label(label=error_details)
        label_error_resolution = Gtk.Label(label=error_resolution)

        grid = Gtk.Grid()
        grid.attach(label_error_details, 0, 1, 1, 1)
        grid.attach(label_error_resolution, 0, 2, 1, 1)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)

        popup.vbox.add(grid)
        popup.set_transient_for(self.window)
        self.window.set_sensitive(False)
        popup.show_all()
        response = popup.run()

        if response == Gtk.ResponseType.OK:
            popup.destroy()
            self.window.set_sensitive(True)

    # Function used to start the server in a non-transmitting mode, ie, showing
    # only the webcam output to the user
    def _start_server_no_tx(self) -> None:
        server_pipeline_no_tx = """ v4l2src device={webcam} ! videoconvert !
                                    video/x-raw,framerate=30/1 ! queue !
                                    videorate ! autovideosink"""

        log.info("Starting Server in non-TX Mode...")

        self.server.stop_pipeline()
        self.server.set_pipeline(
            server_pipeline_no_tx.format(webcam=self.webcam_device))
        self.server.start_pipeline()

    # Function used to start the server in a transmitting mode, ie, sending
    # the webcam and microphone output over UDP and showing the user the webcam
    # output
    def _start_server_tx(self) -> bool:
        server_pipeline_tx = """ v4l2src device={webcam} ! tee name=t ! queue !
                    autovideosink t. ! videorate ! videoconvert !
                    video/x-raw,framerate=30/1 ! queue ! jpegenc !
                    rtpjpegpay ! udpsink host={dst_ip}
                    port={video_dst_port} bind-port={video_src_port}
                    pulsesrc ! audioconvert ! audioresample !
                    queue ! opusenc ! rtpopuspay !
                    udpsink host={dst_ip} port={audio_dst_port}
                    bind-port={audio_src_port}"""

        log.info("Starting Server in TX Mode...")

        if (not self._validate_server_inputs()):
            return False

        # Get all input from the entries
        dst_ip = self.entry_dst_ip.get_text()

        src_port_audio = self.entry_src_port_audio.get_text()
        dst_port_audio = self.entry_dst_port_audio.get_text()

        src_port_video = self.entry_src_port_video.get_text()
        dst_port_video = self.entry_dst_port_video.get_text()

        #Run the pipeine
        self.server.stop_pipeline()
        self.server.set_pipeline(
            server_pipeline_tx.format(webcam=self.webcam_device,
                                      dst_ip=dst_ip,
                                      video_dst_port=dst_port_video,
                                      video_src_port=src_port_video,
                                      audio_dst_port=dst_port_audio,
                                      audio_src_port=src_port_audio))
        self.server.start_pipeline()

        return True

    # Function used to validate the inputs for the server transmission
    # Shows a popup and returns false if there is something wrong
    # Returns true otherwise
    def _validate_server_inputs(self) -> bool:
        # Get all input from the entries
        dst_ip = self.entry_dst_ip.get_text()

        src_port_audio = self.entry_src_port_audio.get_text()
        dst_port_audio = self.entry_dst_port_audio.get_text()

        src_port_video = self.entry_src_port_video.get_text()
        dst_port_video = self.entry_dst_port_video.get_text()

        # Check that all the required text boxes are filled in
        # if not --> popup
        if (not dst_ip or not src_port_audio or not dst_port_audio
                or not src_port_video or not dst_port_video):
            self._show_error_popup(
                "Not all required fields were input.",
                "Please insert all required IP and Port inputs to start a call!"
            )
            log.error("Unable to start Server - Missing Fields")
            return False

        # Check that ports are numbers and in range
        if (not src_port_audio.isnumeric() or not dst_port_audio.isnumeric()
                or not src_port_video.isnumeric()
                or not dst_port_video.isnumeric()):
            self._show_error_popup(
                "Not all port values are numeric.",
                "Please numeric port values to start a call!")
            log.error("Unable to start Server - Non-Numeric Port Fields")

            return False

        # Check that a valid IP address has been provided
        try:
            ip = ipaddress.ip_address(dst_ip)
            if (type(ip) is not ipaddress.IPv4Address):
                self._show_error_popup(
                    "Only IPv4 addresses are supported.",
                    "Please enter a valid IPv4 address to start a call!")
                log.error("Unable to start Server - Non-IPv4 ip address")
                return False
        except:
            self._show_error_popup(
                "The IP Address entered is not valid.",
                "Please enter a valid IPv4 address to start a call!")
            log.error("Unable to start Server - Invalid IP address format")
            return False

        return True

    # Function used to start the client to receive video and audio from UDP
    def _start_client(self) -> bool:
        client_pipeline_rx = """ udpsrc port={video_rx_port} !
                        application/x-rtp, encoding-name=JPEG,payload=26 !
                        rtpjpegdepay ! jpegdec ! videoconvert !
                        queue ! autovideosink
                        udpsrc port={audio_rx_port} !
                        application/x-rtp, encoding-name=OPUS,payload=96 !
                        rtpopusdepay ! opusdec ! audioconvert !
                        queue ! pulsesink async=false"""

        log.info("Starting Client...")

        if (not self._validate_client_inputs()):
            return False

        # Get all input from the entries
        rx_port_audio = self.entry_rx_port_audio.get_text()
        rx_port_video = self.entry_rx_port_video.get_text()

        self.client.stop_pipeline()
        self.client.set_pipeline(
            client_pipeline_rx.format(video_rx_port=rx_port_video,
                                      audio_rx_port=rx_port_audio))
        self.client.start_pipeline()
        log.info("Client Started!")
        return True

    # Function used to validate the inputs for the client transmission
    # Shows a popup and returns false if there is something wrong
    # Returns true otherwise
    def _validate_client_inputs(self) -> bool:
        # Get all input from the entries
        rx_port_audio = self.entry_rx_port_audio.get_text()
        rx_port_video = self.entry_rx_port_video.get_text()

        # Check that all the required text boxes are filled in
        # if not --> popup
        if (not rx_port_audio or not rx_port_video):
            self._show_error_popup(
                "Not all required fields were input.",
                "Please insert all required IP and Port inputs to start a call!"
            )
            log.error("Unable to Start Client - Missing Fields")
            return False

        # Check that ports are numbers and in range
        if (not rx_port_audio.isnumeric() or not rx_port_video.isnumeric()):
            self._show_error_popup(
                "Not all port values are numeric.",
                "Please numeric port values to start a call!")
            log.error("Unable to Start Client - Non-Numeric Ports Fields")
            return False

        return True

    # Callback function for when the user clicks the "Start Call" button.
    # This function gets the user input from the entries, validates them
    # and starts the server tx and client rx pipelines
    def _start_call(self, widget: Gtk.Widget) -> None:

        #Run the pipeine
        log.info("Starting Call...")
        start_tx_success = self._start_server_tx()

        if (not start_tx_success):
            log.error("Unable to start tx successfully")
            return

        start_rx_success = self._start_client()

        if (not start_rx_success):
            log.error("Unable to start rx successfully")
            return

        self.start.set_sensitive(False)
        self.stop.set_sensitive(True)
        log.info("Call Started!")

    # Callback function for when the user clicks the "End Call" button.
    # The function stops the server tx and client rx pipelines, and starts
    # the server pipeline (with no tx) so that the user can still see the
    # camera output in the window
    def _end_call(self, widget: Gtk.Widget) -> None:
        log.info("Ending Call...")
        self.client.stop_pipeline()
        self.server.stop_pipeline()
        self._start_server_no_tx()
        self.start.set_sensitive(True)
        self.stop.set_sensitive(False)
        log.info("Call Ended!")
