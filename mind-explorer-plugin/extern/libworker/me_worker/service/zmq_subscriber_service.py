import asyncio

import loguru
from me_worker.service.msg_service.msg_adapter import msg_adapter_producer, ZmqSubscriber
from me_worker.service.msg_service.topic import SUB_PINGPONG, SUB_ZMQ_CC_HS_DATA

from me_worker.config.settings import setting


class ZMQSubscriberService:
    topic = SUB_ZMQ_CC_HS_DATA
    ZMQ_URI = None

    def __init__(self):
        self._client = msg_adapter_producer.get_msg_adapter("zmq", uri=self.ZMQ_URI)
        self.sub:ZmqSubscriber = None

    async def drop_msg(self):
        if self.sub.pending_msgs > setting.rt_pending_num // 2:
            drop_size = int(setting.rt_pending_num * 0.1)
        elif self.sub.pending_bytes > setting.rt_pending_bytes // 2:
            drop_size = int(self.sub.pending_msgs * 0.5)
        else:
            drop_size = 0

        if drop_size > 0:
            loguru.logger.error(f"pending msg is {self.sub.pending_msgs}, drop {drop_size}")
            for i in range(drop_size):
                try:
                    msg = self.sub._pending_queue.get_nowait()
                    self.sub._pending_size -= len(msg.data)
                except Exception as e:
                    loguru.logger.error(e)

    async def clear_msg(self):
        try:
            msg = self.sub._pending_queue.get_nowait()
            self.sub._pending_size -= len(msg.data)
        except Exception as e:
            loguru.logger.error(e)


    async def init(self, pending_msgs_limit=5, **kwargs):
        self.sub: ZmqSubscriber = await self._client.subscribe(self.topic, pending_msgs_limit=pending_msgs_limit, **kwargs)
        loguru.logger.debug(f"start sub topic={self.topic}")
        # async for msg in self.sub.messages:
        #     *msg, meta = msg.data
        #     print(meta, len(msg))
        return self.sub

    async def test_subscriber(self):
        async for msg in self.sub.messages:
            print(msg.data)