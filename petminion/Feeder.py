import logging

import paho.mqtt.client as mqtt

from .util import app_config

logger = logging.getLogger()


class Feeder:

    def feed(self, num_feedings=1):
        logger.info(f'Simulating {num_feedings} feedings!')


command_topic = "zigbee2mqtt/feeder/set"


class ZigbeeFeeder(Feeder):
    def __init__(self):
        self.client = client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            logger.debug("MQTT connected with result code " + str(rc))

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

    def feed(self, num_feedings=1) -> None:
        logger.info(f'Feeding {num_feedings} feedings via Zigbee!')

        # FIXME - wait for the confirmation publish from the feeder device, if it doesn't occur soon print a big error and don't consider this a feeding
        # FIXME - "remote" might be better than manual
        self.client.publish(command_topic,
                            f'{{ "feed": "START", "mode": "manual", "feeding_size": { num_feedings } }}')
