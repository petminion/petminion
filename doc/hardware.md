
## Current 'bill of materials'

This project is only ready for 'brave' co-developers at this point - so these instructions are very preliminary.  Don't buy this hardware unless you are ready to tinker - it might not work out of the box (but we can improve this project together).

The current rough BOM for the system I'm using now is:

FIXME raspberry PI 3 doesn't have enough RAM runs super slow with the models.  The full virtual size of our python process is about 6GB, but the resident size only needs to be about 1GB.  But a 1GB rpi3 doesn't have enough free RAM to avoid constantly paging that 1GB.

* A raspberry PI 3 (see below for details).  (Developers with a linux computer can also run/develop on their desktop directly)
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
