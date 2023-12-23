# DietPi install instructions

Our recommended OS distribution for your rasberry pi (or similar) is DietPi. Here's our notes on how to install on your board:

* Basically follow the (instructions)[https://dietpi.com/docs/install/]
* Copy our recommended dietpi/dietpi.txt file onto your sdcard, overwriting the existing /boot/dietpi.txt
* Edit /boot/dietpi-wifi.txt with information to connect to your wifi (network name and password)
* To allow 'headless' configuration and booting of the device (recommended) edit /boot/dietpi.txt on the sd-card per these (details)[https://dietpi.com/docs/usage/#how-to-do-an-automatic-base-installation-at-first-boot-dietpi-automation]

FIXME - eventually our dietpi.txt will grow to 'fully' configure a virgin install of petminion, but for now you'll need to proceed and run the deploy-dev.sh script per
our crude documentation.