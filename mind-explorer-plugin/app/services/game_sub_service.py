import asyncio

import loguru
from me_worker.service.msg_service.msg_adapter import msg_adapter_producer, ZmqSubscriber
from me_worker.service.zmq_subscriber_service import ZMQSubscriberService
from me_worker.service.msg_service.topic import SUB_PINGPONG, SUB_ZMQ_CC_HS_DATA

from app.config.setting import setting


class PingPongRecordSubService(ZMQSubscriberService):
    topic = SUB_PINGPONG
    ZMQ_URI = setting.game_setting.zmq_uri

    async def test_subscriber(self):
        if self.sub is None:
            await self.init()
        async for msg in self.sub.messages:
            print(msg.data)


class FlappyRecordSubService(ZMQSubscriberService):
    topic = SUB_PINGPONG
    ZMQ_URI = setting.game_setting.zmq_uri


if __name__ == '__main__':
    p = PingPongRecordSubService()
    asyncio.run(p.test_subscriber())