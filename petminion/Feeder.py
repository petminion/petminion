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
                            f'{{ "feed": "START", "mode": "manual", "serving_size": { num_feedings } }}')

    def init_feeder(self):
        """Send MQTT to force feeder into manual mode, with no built-in scheduled feedings"""
        # set portions_weight in attempt to fix error message seen on boot (if feeder lost power) - seems non fatal?
        # Dec 20 07:57:41 petminion npm[595]: Zigbee2MQTT:info  2023-12-20 07:57:41: MQTT publish: topic 'zigbee2mqtt/feeder', payload '{"child_lock":"UNLOCK","error":false,"feed":"START","feeding_size":1,"feeding_source":"remote","led_indicator":"OFF","linkquality":163,"mode":"manual","portion_weight":8,"portions_per_day":0,"schedule":[],"serving_size":1,"weight_per_day":0}'
        # Dec 20 07:57:41 petminion python[21390]: 07:57:41 DEBUG MQTT received zigbee2mqtt/feeder: b'{"child_lock":"UNLOCK","error":false,"feed":"START","feeding_size":1,"feeding_source":"remote","led_indicator":"OFF","linkquality":163,"mode":"manual","portion_weight":8,"portions_per_day":0,"schedule":[],"serving_size":1,"weight_per_day":0}'
        # Dec 20 07:57:41 petminion npm[595]: Zigbee2MQTT:error 2023-12-20 07:57:41: Exception while calling fromZigbee converter: Expected one of: 1, 2, 4, 8, 16, 31, 32, 42, 64, 85, 96, 127, got: 'undefined'}

        # a full payload seems to contain '{"child_lock":"UNLOCK","error":false,"feed":"","feeding_size":1,"feeding_source":"schedule","led_indicator":"OFF","linkquality":149,"mode":"manual","portion_weight":8,"portions_per_day":7,"schedule":[],"serving_size":1,"weight_per_day":56}'
        payload = '{"schedule":[], "portion_weight":8 }'
        self.client.publish(command_topic, payload)
