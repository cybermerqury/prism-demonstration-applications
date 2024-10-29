# Running a Server and Client via GStreamer

The below is a guide on how to create GStreamer server and client pipelines to
stream video (captured via webcam) and audio (captured by a microphone).

The video is JPEG encoded and the audio is encoded via the Opus audio codec.
The user has the ability to set the:

* Source port (set to `7788` for video and `8899` for audio).
* Destination ip address (set to `127.0.0.1` in the example below).
* Destination port (set to `5200` for video and `5201` for audio).

Both streams are automatically synced together at the client side.

Note that the ports mentioned above are not hardcoded, but rather used 
as an example.
In the python application, they are changed to whatever the user inputs.

## GStreamer Installation

GStreamer is a framework to create multimedia streaming applications.
A GStreamer `pipeline` dictates the flow of data, including input, processing
and output.
To install GStreamer, please follow
[this](https://gstreamer.freedesktop.org/documentation/installing/index.html?gi-language=c#installing-gstreamer)
link, which contains directions on how to install GStreamer, depending on your
OS.

For Ubuntu 20.04, the following was used:

``` bash
sudo apt-get install    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
                        libgstreamer-plugins-bad1.0-dev \
                        gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                        gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
                        gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x \
                        gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 \
                        gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

## Server Pipeline

``` bash
gst-launch-1.0  v4l2src ! videorate ! videoconvert ! \
                video/x-raw,framerate=30/1 ! queue ! jpegenc ! rtpjpegpay ! \
                udpsink host=127.0.0.1 port=5200 bind-port=7788 pulsesrc ! \
                audioconvert ! audioresample ! queue ! opusenc ! rtpopuspay ! \
                udpsink host=127.0.0.1 port=5201 bind-port=8899
```

The above server pipeline takes input from the webcam (`v4lsrc`).
The video rate is set to 30fps, and the video is converted to a suitable format
for encoding. The pipeline then performs JPEG Encoding on the frames
(`jpegenc`), creates an
RTP payload (`rtpjpegpay`) and sends it via UDP (`udpsink`).
It also takes input from a microphone (`pulsesrc`) and prepares it for encoding
via `audioconvert` and `audioresample`.
It then compresses it (`opusenc`), creates an RTP payload (`rtpopuspay`) and
transmits it via UDP (`udpsink`).

## Client Pipeline

``` bash
gst-launch-1.0  udpsrc port=5200 ! application/x-rtp, \
                encoding-name=JPEG,payload=26 !  rtpjpegdepay ! jpegdec ! \
                videoconvert ! queue ! autovideosink \
                udpsrc port=5201 ! application/x-rtp, \
                encoding-name={OPUS},payload=96 ! rtpopusdepay ! opusdec ! \
                audioconvert ! queue ! alsasink async=false
```

The above client pipeline takes a UDP input (`udpsrc`) on port 5200, specifies
the type of data (`application/x-rtp, encoding-name=JPEG,payload=26`), extracts
JPEG packets (`rtpjpegdepay`), and decompresses them (`jpegdec`).
The pipeline then converts them to a suitable output format (`videoconvert`)
and outputs them (`autovideosink`).
Similarly, it listens for UDP input (`udpsrc`) on port 5201, specifies the type
of data (`application/x-rtp, encoding-name={OPUS},payload=96`), extracts the
Opus packets (`rtpopusdepay`), and decodes them (`opusdec`).
It then converts them to a suitable format (`audioconvert`), puts them in a
`queue` and outputs them (`alsasink`).
