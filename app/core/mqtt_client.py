#!/usr/bin/env python
import os
import time
from typing import Optional

import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(
        self,
        broker: str,
        port: int,
        topic: str,
        client_id: Optional[str] = None,
        qos: int = 1,
    ) -> None:
        self.topic = topic
        self.qos = qos
        cid = client_id or f"scenario-pub-{os.getpid()}"
        self.client = mqtt.Client(client_id=cid, clean_session=True)
        self.client.loop_start()
        self.client.connect_async(broker, port, keepalive=60)
        for _ in range(50):
            if self.client.is_connected():
                break
            time.sleep(0.1)

    def publish(self, payload: str) -> None:
        info = self.client.publish(self.topic, payload, qos=self.qos)
        info.wait_for_publish()

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()


