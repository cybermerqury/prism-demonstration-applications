# Video Call

## Setup

Before running the app, the following installation steps need to take place:

1. Run the following command in a terminal:
   ```sudo apt install libcairo2-dev pkg-config python3-dev libgtk-3-dev libgirepository1.0-dev```
2. Install gstreamer as per the documentation [here](https://github.com/cybermerqury/video-conferencing-app/blob/main/docs/gstreamer_server_and_client-pipelines.md).
3. Run the following to install the required Python pacakges:
   ```pip3 install -r requirements.txt```

*For more information about the gstreamer pipeline definions, please refer to the documentation [here](https://github.com/cybermerqury/video-conferencing-app/blob/main/docs/gstreamer_server_and_client-pipelines.md)*

## Usage

1. Make sure you have an available webcam connected to your setup.
2. `cd` to the root directory.
3. Run the following command, following the instructions as prompted:
   ```./echo_cancell.sh```.
4. Run the following command:
   ```python3 main.py```.
   This will open the application.
5. Fill in the necessary IP address and port inputs.
6. Select the webcam which you would like to use as input.
   Notice how the bottom right drawing area is showing the output from your selected webcam.
7. From your system settings, (ie, not from the app) ensure that you have the microphone and speaker output of your choice selected.
8. Click on the green `Start Call` button to start a call.
9. Click on the red `End Call` button to end a call.
10. To close the app, click on the `X` button found in the title bar.

## Known Limitations

* The application currently only supports Linux based OSes.
This is because of how it shows the gstreamer output in the gtk window, ie, the way it receives a handle to the drawing area.
* Should a webcam device be disconnected or connected while the app is running, the change will not be reflected in the app.
To view the changes, please close the app and start it again.


## License

© 2024 Merqury Cybersecurity Ltd.
This project is licensed under the
[GNU Affero General Public License v3.0 only](https://www.gnu.org/licenses/agpl-3.0.txt).
If you would like to use this product under a different license, kindly contact
us on [info@merqury.eu](mailto:info@merqury.eu).

## Acknowledgements

This software has been developed in the project PRISM (Physical Security
for Public Infrastructure in Malta) which is co-funded by the European Union
under the Digital Europe Programme grant agreement number 101111875.
