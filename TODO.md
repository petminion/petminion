# TODO

Project Principals

* A generalized tool for (semi?) automated training of animals
* Use 'off-the-shelf' hardware as much as possible (hopefully no soldering, no requirement for 3D printing)
* Make the software accessible and extendable by beginning coders.  Particularly for adding training rules.
* Two initial test cases: cat training and crow training
* Project should be fun and useful for both the developers and the users

new name petminion (petminion.org registered)

- make proposed state machine for initial crow and cat trainer - figure out how to deal with multiple deliveries for multiple rewards
- make basic API for recognizer/camera
- make state machineish training rules engine (find existing state machine lib?) https://github.com/pytransitions/transitions
-   Get remote debugging working
-   Have recognizer save interesting frames to a directory.  Where interesting
    can be: something not blank, something that is a bird.
-   have a blacklist of mistaken matches which we will never consider interesting  
-   Store image and the matching terms in a separate datafile  
-   Only store a max of one frame every 30 seconds.
-   Tweet when we saw something interesting
-   Store a short movie every time we see something interesting (and tweet it as a gif)
-   automatically load training rules from a directory.  This will allow users to make/share rules without using git/github
-   Use a should_trigger() method in the rules to allow multiple rules to be candidates at once
-   Add hotreloading of rules based on file changes

during development post 'success' images to mastodon https://mastodonpy.readthedocs.io/en/stable/

## General design plan

ooh someone already did something similar? https://corvidcleaning.com/

and https://www.thecrowbox.com/ seems to have failed/been abandoned?  nice design though - see youtube below
https://thecrowbox.com/wiki/doku.php?id=kit:overview_doc
https://www.youtube.com/watch?v=jcp_FWfYtLY
oh! still alive! https://groups.google.com/g/CrowBoxKit?pli=1

hmm - it seems like actual states in state machine are very limited.  instead of full general state machine at first just a base class like:

TrainingRule with methods:

overridable:
- evaluate_scene - current will already be initialized with camera image before this method is called

protected:
- do_feeding - called by evaulateScene as needed, default method saves current success image, talks to feeder and has a short delay to give time for eating (1 min?)
- current is a ProcessedImage.  ProcessedImage constructor takes in a raw camera image as a parameter
- current.save(description, notes = None, is_success = True) - saves (raw & annotated) image with timestamp and description in the name, if notes are provided will be saved in name.txt, if !is_sucess save image as a sample failure image.  images stored in a directory format suitable for feeding to SimCamera
- current.annotated - current image with annotations 
- current.detections - array of current detected objects, confidence and positions (use cached_property - https://madhumithakannan7.medium.com/lazy-loading-in-python-d4258c94f599).  inherits from ImageClassification
- current.classifications - array of current detections and confidence (no positions provided).  use https://stackoverflow.com/questions/44320382/subclassing-collections-namedtuple

Other classes:

Trainer - the main class.  sets up hardware, loads and repeatedly executes the correct current training rule

Feeder - provides control of a feeder (to allow that other crow project hw to work with this) also serves as a simulated feeder if not subclassed
  feed()
  ZigbeeFeeder - subclass uses MQTT to control the feeder

Camera.read_image() - uses camera apis to read images from a USB camera
  CVCamera - reads from a USB camera
  SimCamera - pulls images from a directory of test images

ImageRecognizer - initially just one implementation using the library I found

Use PyPi for initial distribution (including all dependencies).

### Sample cat training

level 0 attempt CatTrainingRule0:

- look for targets (springs) on white board.  
- count number of springs seen.
- if number of springs increases & cat present -> emit food (if # feed events per day not reached - or implicitly limited by # of springs in house)

states: looking, feeding

level 1 attempt CatTrainingRule1:

- after spring seen and feed event -> power GPIO to somehow empty the target area

### Sample crow training

level 0 attempt (keep food always present CrowTrainingRule0):

- look at target and if no food present -> emit food

states: looking, feeding

level 1 attempt (only emit food once we see a bird - to get birds used to feeder noise):

- look at target no food and no bird -> emit food 

states: looking, feeding

level 2 attempt (only feed crows):

- look at target no food and no crow -> emit food 

states: looking, feeding

level 3 attempt (provide tokens on a shelf just above target - hopefully crow knocks tokens into target)

- look at target no food, no crow and no token -> emit food

level 4 attempt (provide tokens nearby but not on shelf)

- same as above except tokens are not close, also we will count anything as a 'token' doesn't have to be the tokens we provided

FIXME - add GPIO control to empty unused food and empty tokens.


## Recognizer setup

Install prerequisites 
```
apt install v4l-utils virtualenv
```

Create and activate python environment
```
kevinh@kdesktop:~/development/crowbot$ virtualenv crowenv
created virtual environment CPython3.11.6.final.0-64 in 188ms
  creator CPython3Posix(dest=/home/kevinh/development/crowbot/crowenv, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/kevinh/.local/share/virtualenv)
    added seed packages: pip==23.2, setuptools==68.1.2, wheel==0.41.0
  activators BashActivator,CShellActivator,FishActivator,NushellActivator,PowerShellActivator,PythonActivator
kevinh@kdesktop:~/development/crowbot$ source crowenv/bin/activate
(crowenv) kevinh@kdesktop:~/development/crowbot$ 
```

(To exit this python environment use deactivate)

Read from USB camera in python
```
pip install opencv-python
```

ImageAI setup:
```
pip install cython pillow>=7.0.0 numpy>=1.18.1 opencv-python>=4.1.2 torch>=1.9.0 --extra-index-url https://download.pytorch.org/whl/cpu torchvision>=0.10.0 --extra-index-url https://download.pytorch.org/whl/cpu pytest==7.1.3 tqdm==4.64.1 scipy>=1.7.3 matplotlib>=3.4.3 mock==4.0.3
pip install imageai --upgrade

(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ mv ~/Downloads/yolov3.pt .
(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ mv ~/Downloads/image2.jpg .
(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ python test-detection.py 
person  :  99.99  :  [174, 107, 278, 270]
--------------------------------
person  :  99.97  :  [415, 132, 534, 264]
--------------------------------
person  :  93.68  :  [300, 173, 391, 283]
--------------------------------
person  :  98.51  :  [23, 310, 342, 438]
--------------------------------
apple  :  96.51  :  [527, 343, 557, 365]
--------------------------------
bed  :  99.56  :  [23, 211, 715, 553]
--------------------------------
laptop  :  99.85  :  [451, 204, 579, 284]
--------------------------------
laptop  :  99.89  :  [279, 322, 402, 427]
--------------------------------
laptop  :  98.99  :  [120, 208, 259, 293]
--------------------------------
laptop  :  99.53  :  [304, 241, 390, 290]
--------------------------------

(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ mv ~/Downloads/1.jpg .
(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ python test-classifier.py 
/home/kevinh/development/crowbot/crowenv/lib/python3.11/site-packages/torchvision/models/_utils.py:208: UserWarning: The parameter 'pretrained' is deprecated since 0.13 and may be removed in the future, please use 'weights' instead.
  warnings.warn(
/home/kevinh/development/crowbot/crowenv/lib/python3.11/site-packages/torchvision/models/_utils.py:223: UserWarning: Arguments other than a weight enum or `None` for 'weights' are deprecated since 0.13 and may be removed in the future. The current behavior is equivalent to passing `weights=None`.
  warnings.warn(msg)
/home/kevinh/development/crowbot/crowenv/lib/python3.11/site-packages/torchvision/models/inception.py:43: FutureWarning: The default weight initialization of inception_v3 will be changed in future releases of torchvision. If you wish to keep the old behavior (which leads to long initialization times due to scipy/scipy#11299), please set init_weights=True.
  warnings.warn(
sports car  :  65.5919
convertible  :  12.3927
car wheel  :  8.0013
beach wagon  :  5.3134
grille  :  4.7836
(crowenv) kevinh@kdesktop:~/development/crowbot/imageai$ 

```

Tensorflow setup:

```
pip3 install tf-models-official numpy protobuf protobuf-compiler

# Clone the tensorflow models repository
git clone --depth 1 https://github.com/tensorflow/models

kevinh@kdesktop:~/development/crowbot$ v4l2-ctl --list-formats-ext --device /dev/video0
ioctl: VIDIOC_ENUM_FMT
	Type: Video Capture

	[0]: 'MJPG' (Motion-JPEG, compressed)
		Size: Discrete 1920x1080
			Interval: Discrete 0.033s (30.000 fps)
		Size: Discrete 1280x720
			Interval: Discrete 0.017s (60.000 fps)
		Size: Discrete 1024x768
			Interval: Discrete 0.033s (30.000 fps)
		Size: Discrete 640x480
			Interval: Discrete 0.008s (120.101 fps)
		Size: Discrete 800x600
			Interval: Discrete 0.017s (60.000 fps)
		Size: Discrete 1280x1024
			Interval: Discrete 0.033s (30.000 fps)
		Size: Discrete 320x240
			Interval: Discrete 0.008s (120.101 fps)
	[1]: 'YUYV' (YUYV 4:2:2)
		Size: Discrete 1920x1080
			Interval: Discrete 0.167s (6.000 fps)
		Size: Discrete 1280x720
			Interval: Discrete 0.111s (9.000 fps)
		Size: Discrete 1024x768
			Interval: Discrete 0.167s (6.000 fps)
		Size: Discrete 640x480
			Interval: Discrete 0.033s (30.000 fps)
		Size: Discrete 800x600
			Interval: Discrete 0.050s (20.000 fps)
		Size: Discrete 1280x1024
			Interval: Discrete 0.167s (6.000 fps)
		Size: Discrete 320x240
			Interval: Discrete 0.033s (30.000 fps)
```

FIXME - find how to make cuda work with tensorflow: >>> import tensorflow as tf
2023-12-01 12:47:20.772159: I external/local_tsl/tsl/cuda/cudart_stub.cc:31] Could not find cuda drivers on your machine, GPU will not be used.


### Recognizer

* reads from USB camera
* recognizer runs and outputs keywords/confidence for matches

Plywood with marked circle A, feeder bowl (which can be emptied) and circle B

### Feeder control

USE mqtt to activate feeder

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

## Zigbee2mqtt config

per https://www.zigbee2mqtt.io/guide/installation/02_docker.html

use my docker compose file.

docker compose up -d

## MQTT broker config

in /home/kevinh/development/crowbot/mosquitto/compose.yaml per https://www.homeautomationguy.io/blog/docker-tips/configuring-the-mosquitto-mqtt-docker-container-for-use-with-home-assistant

To subscribe to all

mosquitto_sub -h localhost -t \#

### flash new firmware onto the sonoff adapter

per https://www.zigbee2mqtt.io/guide/adapters/flashing/flashing_via_cc2538-bsl.html

```
docker run --rm \
    --device /dev/ttyUSB0:/dev/ttyUSB0 \
    -e FIRMWARE_URL=https://github.com/Koenkk/Z-Stack-firmware/raw/Z-Stack_3.x.0_coordinator_20230507/coordinator/Z-Stack_3.x.0/bin/CC1352P2_CC2652P_launchpad_coordinator_20230507.zip \
    ckware/ti-cc-tool -ewv -p /dev/ttyUSB0 --bootloader-sonoff-usb
```

### pair feeder to zigbee2mqtt

* completely unplug feeder from power
* then plug in and hold reset for 5 secs

### control feeder via MQTT publishes

Publish to "zigbee2mqtt/feeder/set"

I bet payload only needs { "feed": "START" }

I can't figure out how to set feeding size.  But this works for one dose:

mosquitto_pub -t zigbee2mqtt/feeder/set -m "{ \"feed\": \"START\", \"mode\": \"manual\" }"

{"level":"info","message":"MQTT publish: topic 'zigbee2mqtt/feeder', payload '{\"error\":false,\"feed\":\"START\",\"feeding_size\":1,\"feeding_source\":\"remote\",\"linkquality\":185,\"portions_per_day\":4,\"weight_per_day\":32}'"}

## coral board notes

ssh crowbot
