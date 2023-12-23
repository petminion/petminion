# Geeksville private notes

These notes are temporary and very unlikely to be interesting/useful for others ;-)

## Coral hardware & software setup

Per https://coral.withgoogle.com/docs/dev-board/get-started/

Their demo can be reached over wifi at http://crowbot.local:4664/

Make device accessible over wifi via ssh with:
```
kevinh@kevin-server:~/development/ebike/Color_LCD/firmware/SW102$ mdt pushkey ~/.ssh/id_rsa.pub
Waiting for a device...
Connecting to crowbot at 192.168.100.2
Pushing /home/kevinh/.ssh/id_rsa.pub
Key /home/kevinh/.ssh/id_rsa.pub pushed.
kevinh@kevin-server:~/development/ebike/Color_LCD/firmware/SW102$ ssh mendel@crowbot.local
```

### Setup remote filesystem access to the Coral

On the desktop PC:
sudo apt-get install sshfs
run tools/mount-crowbot.sh

### Setup camera hardware & software

Per https://coral.withgoogle.com/docs/dev-board/camera

#### To grab and display a frame from the camera over xwindows

avconv -f video4linux2 -s 640x480 -i /dev/video1 -ss 0:0:2 -frames 1 /tmp/out.jpg
display cam-image.jpg

#### to see camera stream over xwindows

gst-launch-1.0 v4l2src device=/dev/video1 ! autovideosink

FIXME - test gstreamer to find this bug

v4l2src device=/dev/video1 ! video/x-raw,framerate=30/1,format=YUY2,height=1080,width=1920 ! tee name=t
t. ! queue max-size-buffers=1 leaky=downstream ! videoconvert ! x264enc aud=False tune=zerolatency threads=4 speed-preset=ultrafast key-int-max=5 bitrate=1000 ! video/x-h264,profile=baseline ! h264parse ! video/x-h264,alignment=nal,stream-format=byte-stream ! appsink drop=False emit-signals=True max-buffers=1 sync=False name=h264sink
t. ! queue ! glfilterbin filter=glcolorscale ! video/x-raw,width=224,format=RGBA,height=126 ! videoconvert ! video/x-raw,width=224,format=RGB,height=126 ! videobox autocrop=True ! video/x-raw,width=224,height=224 ! appsink drop=True emit-signals=True max-buffers=1 sync=False name=appsink
INFO:edgetpuvision.streaming.server:[192.168.86.4:33786] Tx thread finished
INFO:edgetpuvision.streaming.server:[192.168.86.4:33786] Stopping...
INFO:edgetpuvision.streaming.server:[192.168.86.4:33786] Stopped.
INFO:edgetpuvision.streaming.server:Number of active clients: 1
Error: gst-stream-error-quark: Internal data stream error. (1): gstbasesrc.c(2939): gst_base_src_loop (): /GstPipeline:pipeline0/GstV4l2Src:v4l2src0:
streaming stopped, reason not-negotiated (-4)

This simpler test case shows the same problem:

http://wiki.oz9aec.net/index.php/Gstreamer_cheat_sheet
gst-launch-1.0 v4l2src device=/dev/video1 ! video/x-raw,framerate=30/1,format=YUY2,height=1080,width=1920 ! videoconvert ! autovideosink

per http://www.einarsundgren.se/gstreamer-basic-real-time-streaming-tutorial/ this means
gst-launch-1.0 v4l2src device=/dev/video1 ! capsfilter caps=video/x-raw,framerate=30/1,format=YUY2,height=1080,width=1920 ! videoconvert ! autovideosink

