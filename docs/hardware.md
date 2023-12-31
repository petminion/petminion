
## Current 'bill of materials'

This project is only ready for 'brave' co-developers at this point - so these instructions are very preliminary.  Don't buy this hardware unless you are ready to tinker - it might not work out of the box (but we can improve this project together).

The current rough BOM for the system I'm using now is:

FIXME raspberry PI 3 doesn't have enough RAM runs super slow with the models.  The full virtual size of our python process is about 6GB, but the resident size only needs to be about 1GB.  But a 1GB rpi3 doesn't have enough free RAM to avoid constantly paging that 1GB.  I tried using smaller models but that only cuts the resident size to 700MB (not a big change).



With a RPi4B and the 'full/slow' machine vision model it takes about six seconds of CPU time to fully analyze a frame - which I think is fine for this application.  Eventually we will switch to Tensorflow Lite which should be **much** faster, but that will be a few months.

But even better the 'fast/slightly-crummy' machine vision models only need one secondish to fully analyze a frame!  So we are using that for now (by default, you can change it in your config.ini file).

* A raspberry PI 4 with at least 4GB of RAM, 8GB recommended.  (Developers with a linux computer can also run/develop on their desktop directly)
* This $50 camera (because waterproof and long USB cable to reach my computer inside): https://www.amazon.com/gp/product/B07C2RL8PB/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1 
* This $80 feeder https://www.amazon.com/gp/product/B0B9XZ96PH
* This $32 USB to zigbee adapter (to allow controlling the feeder) https://www.amazon.com/gp/product/B09KXTCMSC.  Though there are other adapters that might be better that are only $16

I suspect once a bit more mature a more optimal (i.e. cheap and direct connect to the selected rPi model) camera could be used (if rpi and camera were under a shell to protect from rain/wind).  And going prices for zigbee USB adapters on aliexpress are about half the price I paid.

I kinda hope that if this project begins to be useful for people (training or merely feeding crows, cats, birds) some chinese mfg will make cheap hw that works with it (still keeping the software open source). 

### Supported development boards

Most anything rasberry pi 3ish (or above) is probably fine.  We recommend running the 'DietPi' OS because it is well suited to **many** development boards.
You can find supported boards and install images (here)[https://dietpi.com/#downloadinfo].

## Not yet supported

The following hardware is not yet supported, but possibly interesting someday...

### Feeders

https://home.miot-spec.com/s/mmgg.feeder.fi1
https://home.miot-spec.com/s/feeder

Projects:
https://github.com/rytilahti/python-miio/issues/1047
https://github.com/rytilahti/python-miio

A competeting 'standard' is Tuya devices:
https://github.com/rospogrigio/localtuya/issues/1082
https://github.com/codetheweb/tuyapi?tab=readme-ov-file
https://github.com/jasonacox/tinytuya

per https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md
socks at https://iot.tuya.com/

(minionenv) kevinh@kdesktop:~/development/petminion$ python -m tinytuya scan

TinyTuya (Tuya device scanner) [1.13.1]

Scanning on UDP ports 6666 and 6667 and 7000 for devices for 18 seconds...

Unknown v3.3 Device   Product ID = keyexttaytt7m4se  [Valid Broadcast]:
    Address = 192.168.101.122   Device ID = 11181704483fda40398f (len:20)  Local Key =   Version = 3.3  Type = default, MAC = 48:3f:da:40:39:8f
    No Stats for 192.168.101.122: DEVICE KEY required to poll for status
Unknown v3.3 Device   Product ID = keyexttaytt7m4se  [Valid Broadcast]:
    Address = 192.168.101.170   Device ID = 4876527440f52004f0b8 (len:20)  Local Key =   Version = 3.3  Type = default, MAC = 40:f5:20:04:f0:b8
    No Stats for 192.168.101.170: DEVICE KEY required to poll for status
Unknown v3.3 Device   Product ID = keydpkw438xwpdtm  [Valid Broadcast]:
    Address = 192.168.101.6   Device ID = ebc9bb9b439ffacb1buuez (len:22)  Local Key =   Version = 3.3  Type = default, MAC = 
    No Stats for 192.168.101.6: DEVICE KEY required to poll for status
