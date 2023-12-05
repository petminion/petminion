# Former README contents to be merged or deleted soon...

A machine driven bot for training animals (initially the loud but supposedly smart crows outside my house)

## Required hardware

* A [Google Coral dev board](https://coral.withgoogle.com/docs/dev-board/get-started/).  This is a really cool board which provides hardware acceleration for their TensorFlow machine learning models.  I'll try to use this project as a meaty test/example of what that board can do.
* A 3D printable feeder with associated servo. (Not yet available, will likely be based on [this](https://www.thingiverse.com/thing:3269637))
* A feeding platform (approximately 4' x 4' of plywood, painted white)
* A pullcord (that the crow pulls to request new food - needed for the 4th challenge - see below)

## Implementation plan

But my rough plan is (I'll keep a running public write-up on the progress in a nice markdown that goes with the git code / feeder model)

* Convert my existing 3d printed rpi based cat feeder pwm stepper to be driven from a coral gpio.  Possibly also reuse bits from my [hummingbird recognizer Twitterbot](https://github.com/geeksville/hummingbot). Post updated feeder and Coral case/mount to [my Thingverse repo](https://www.thingiverse.com/punkgeek/about).
* Install feeder on my deck with the coral camera looking at a white background where the feed is dispensed and the crow is expected to stand (and eventually interact)
* Initially dispense a small amount of food periodically - to ensure ready bait for any bird (I have lots of crows in my neighborhood but want to start easy)
* Use the sample recognizer + current image has at least low confidence of bird + "save current image to disk/emit a little new food 5 min from now (to allow current bird only one feeding at a time and avoid scaring them due to machine noises"
* Use images from previous step to build a curated corpus of: not bird vs not crow vs crow buckets.  I'll use the Coral/Tensorflow documentation to somehow convert that corpus into a custom model for my application.
* Change to only feeding crows
* First crow challenge: if the crow stays at the feeder, keep dispensing food. (Advance to new challenges as my crows learn - adjust challenges as needed)
* 2nd challenge: only keep dispensing food if the crow stands in a certain marked area of the target
* 3rd challenge: no longer 'prime the pump' with free food.  Instead dispense only if the crow stands on the target
* 4th challenge: after initial food only keep dispensing if the crow Pulls the string at the target (connect to gpio)

So that's my rough plan - any feedback is welcome.

### Trainer engine

statemachine ish engine?
watch for keywords from recognizer to cause transitions
different state machines can be listed as worth considering

#### typical level 0 machine

Runs until we get occasional bird visits

if no food present, emit food 

#### typical level 1 machine

if bird present, emit food
once no bird stop emitting food

#### typical level 2 machine

twigs/tokens/something TBD is in circle B

only emit food if bird is in circle A

#### typical level 3 machine

only emit food if bird in circle A and anything is in 

FIXME

## Task notes

These notes might be expanded into a full article at some point, but for now they are just my notes on getting the hardware working.

## Home Assistant notes

Use this zigbee adapter: https://www.amazon.com/dp/B09KXTCMSC

created crowbot/ha/docker.yaml then "docker compose up -d" to start the container (with full access to the USB dongle for zigbee)

  http://localhost:8123/

  user: kevinh

  Add the zigbee controller ( http://localhost:8123/config/integrations/integration/zha ) - it should be found automatically on the USB0 port

  Attach feeder to USB power
  Go to the zigbee controller device, ie: http://localhost:8123/config/devices/device/74283cf05c2ab831503920ea5f763162

  Click on "add devices via this device"

  Click the leftmost button (reset) on the feeder, hold it for 5 seconds.  LED on feeder will blink to indicate in pairing mode

  HomeAssistant UI should prompt to add the device.  Add it and keep its default name of "aqara_aqara_feeder_acn001_feed".  Optionally change icon to "mdi:bird"

### How to programmatically control

per https://smarthomescene.com/reviews/aqara-c1-smart-pet-feeder-review/

```
description: ""
mode: single
trigger:
  - platform: time
    at: "08:00:00"
condition: []
action:
  - service: number.set_value
    data:
      value: "5"
    target:
      entity_id: number.aqara_aqara_feeder_acn001_serving_to_dispense
  - service: button.press
    data: {}
    target:
      entity_id: button.aqara_aqara_feeder_acn001_feed
```

### How to calibrate feeder

The Aqara C1 does not have a dedicated weight sensor to measure your pet food serving size. You need to measure it manually and subsequently operate the device knowing this information. To get an idea of how much you are feeding your pet:

Dispense one portion manually with the button
Measure the weight with a kitchen scale
Let’s say your measurement is 7 grams and your cat needs 35g per feeding
Set the portion weight to 7 grams
Set the serving size to 5
7g x 5 servings = 35g
The Aqara C1 will dispense 5 servings one after another and fill the bowl

Go to "http://localhost:8123/config/devices/device/b2f5b5fd1df7b186d7bb4ea313205596" to configure the portion 
weight/serving size.

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


### 3D printable devboard mount

Requirements: rainproof for exterior mounting, good fan vent support, ribbon cable opening to camera case.  Mount camera case at an adustable angle using two screws.  Or probably keep the camera fixed relative to the devboard case and pivot the entire case.

Or possibly just put the USB camera outside (don't use Coral camera) and leave Coral inside.

STEP file [here](https://coral.withgoogle.com/docs/dev-board/datasheet/)

Per [datasheet](https://coral.withgoogle.com/docs/camera/datasheet/) Camera STEP file

WIP editable CAD model [here](https://cad.onshape.com/documents/f2a0b54590053dee5f07391b/w/a71138c8f6a13ec4c8450d21/e/8161a625f06e7b739b82fb44).

### Setup remote filesystem access to the Coral

On the desktop PC:
sudo apt-get install sshfs
run tools/mount-crowbot.sh

### Setup USB Camera

per <https://coral.withgoogle.com/docs/dev-board/camera/#connect-a-usb-camera>

Best camera is probably a C920 but with these hacks applied: <https://www.christitus.com/logitech-c920-linux-driver/>
v4l2-ctl -d /dev/video6 --set-ctrl=exposure_auto=1 # turn on auto exposure
v4l2-ctl -d /dev/video6 --set-ctrl=focus_auto=0 # to turn on/off autofocus

### Remote debugging python on Coral with Intellij

per <https://www.jetbrains.com/help/idea/run-debug-configuration-python-remote-debug.html>

### coral board notes

ssh crowbot
