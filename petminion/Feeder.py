import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger()


class Feeder:

    def feed(self):
        logger.info(f'Simulating a feeding!')


class ZigbeeFeeder(Feeder):
    def __init__(self):
        self.client = client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            logger.debug("MQTT connected with result code "+str(rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("zigbee2mqtt/feeder")

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            logger.debug(f"MQTT received { msg.topic }: { str(msg.payload) }")

        client.on_connect = on_connect
        client.on_message = on_message
        host = "localhost"
        client.connect(host, 1883, 60)
        client.loop_start()  # FIXME, need to stop looper thread if we destroy this object

    def feed(self):
        super().feed()
        logger.info(f'Feeding via Zigbee!')

        # FIXME - wait for the confirmation publish from the feeder device, if it doesn't occur soon print a big error and don't consider this a feeding
        self.client.publish("zigbee2mqtt/feeder/set",
                            '{ "feed": "START", "mode": "manual" }')
        # mosquitto_pub -t zigbee2mqtt/feeder/set -m "{ \"feed\": \"START\", \"mode\": \"manual\" }"
        # {"level":"info","message":"MQTT publish: topic 'zigbee2mqtt/feeder', payload '{\"error\":false,\"feed\":\"START\",\"feeding_size\":1,\"feeding_source\":\"remote\",\"linkquality\":185,\"portions_per_day\":4,\"weight_per_day\":32}'"}
