from typing import List

import bson
import loguru
import zmq
from me_worker.background_task.actor import BackgroundWorker
from app.config.setting import setting


class ZmqClient:
    def __init__(self):
        self.client = None
        self.back_worker = BackgroundWorker()

    def init(self, uri=None):
        context = zmq.Context()
        self.client = context.socket(zmq.PUB)
        uri = setting.imu_setting.zmq_uri if not uri else uri
        loguru.logger.info(f"connect zmq {uri}")
        self.client.bind(uri)

    def _pub_data(self, topic:bytes, data:bytes):
        loguru.logger.debug(f"{topic} pub")
        self.client.send_multipart([topic, data])

    def pub_raw(self, data: List[bytes]):
        self.client.send_multipart(data)

    def pub_data(self, topic, data:dict):
        if self.client is None:
            self.init()

        if isinstance(topic, str):
            topic = topic.encode()
        data = bson.dumps(data)
        self.back_worker.submit(self._pub_data, topic, data)


zmq_client = ZmqClient()