import paho.mqtt.client as mqtt
import logging
from .util import app_config

logger = logging.getLogger()


class Feeder:

    def feed(self):
        logger.info(f'Simulating a feeding!')


command_topic = "zigbee2mqtt/feeder/set"

class ZigbeeFeeder(Feeder):
    def __init__(self):
        self.client = client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            logger.debug("MQTT connected with result code "+str(rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("zigbee2mqtt/feeder")
            self.init_feeder()

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            logger.debug(f"MQTT received { msg.topic }: { str(msg.payload) }")

        client.on_connect = on_connect
        client.on_message = on_message
        host = app_config.settings['MQTTHost']
        client.connect(host, 1883, 60)
        client.loop_start()  # FIXME, need to stop looper thread if we destroy this object

    def feed(self):
        logger.info(f'Feeding via Zigbee!')

        # FIXME - wait for the confirmation publish from the feeder device, if it doesn't occur soon print a big error and don't consider this a feeding
        # FIXME - "remote" might be better than manual
        self.client.publish(command_topic,
                            '{ "feed": "START", "mode": "manual" }')
        # mosquitto_pub -t zigbee2mqtt/feeder/set -m "{ \"feed\": \"START\", \"mode\": \"manual\" }"
        # {"level":"info","message":"MQTT publish: topic 'zigbee2mqtt/feeder', payload '{\"error\":false,\"feed\":\"START\",\"feeding_size\":1,\"feeding_source\":\"remote\",\"linkquality\":185,\"portions_per_day\":4,\"weight_per_day\":32}'"}

    def init_feeder(self):
        """Send MQTT to force feeder into manual mode, with no built-in scheduled feedings"""
        # a full payload seems to contain '{"child_lock":"UNLOCK","error":false,"feed":"","feeding_size":1,"feeding_source":"schedule","led_indicator":"OFF","linkquality":149,"mode":"manual","portion_weight":8,"portions_per_day":7,"schedule":[],"serving_size":1,"weight_per_day":56}'
        payload = '{"schedule":[]}'
        self.client.publish(command_topic, payload)