set -e

echo "This is a script that tries to install all of the dependencies needed to run petminion."
echo "it should run on virtually any 'debian' linux machine (i.e. rasberry pi should work)."
echo "however, this project is young - if you see error messages please report them on github."
read -p "Press any key to continue... " -n1 -s

# move to project root (relative to install-all.sh)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

echo "Updating repositories..."
sudo apt-get update

echo "Installing runtime prerequisites..."
sudo apt-get upgrade -y mosquitto python3 docker-compose

echo "Installing development prerequisites..."
sudo apt-get upgrade -y v4l-utils virtualenv mosquitto-clients

echo "Configuring docker (needed for zigbee2mqtt)"
sudo groupadd docker
sudo usermod -aG docker $USER

echo "Enabling and starting MQTT broker..."
sudo cp mosquitto/petminion.conf /etc/mosquitto/conf.d/
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

echo "Testing MQTT broker install..."
sleep 2
mosquitto_pub -t test_topic -m testing

# DEPRECATED/disabled echo "Installing and configuring docker (needed for zigbee2mqtt)"
# assumes 64 bit OS, might need changes if 32 bit rpi version: https://docs.docker.com/engine/install/raspberry-pi-os/
# per https://docs.docker.com/engine/install/debian/
#for pkg in docker docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
#sudo groupadd docker
#sudo usermod -aG docker $USER
#newgrp docker
#docker run hello-world

echo "Running zigbee2mqtt install script"
bin/zigbee2mqtt-install.sh

echo "Configuring zigbee2mqtt service"
cp zigbee2mqtt/data/configuration.yaml /opt/zigbee2mqtt/data/configuration.yaml
sudo cp zigbee2mqtt/zigbee2mqtt.service /etc/systemd/system

# Give user access to serial port (for zigbee adapter)
sudo adduser $USER dialout
newgrp dialout

# Start zigbee2mqtt
sudo systemctl enable zigbee2mqtt
sudo systemctl start zigbee2mqtts

sleep 5
echo "Zigbee2mqtt is running, now you should pair your feeder to the zigbee network (long-press the reset button - after success the feeder will beep)"

echo "Generating a test feeder command (your feeder should dispense)"
mosquitto_pub -t zigbee2mqtt/feeder/set -m "{ \"feed\": \"START\", \"mode\": \"manual\" }"


