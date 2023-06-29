import asyncio

import loguru
from me_worker.service.zmq_subscriber_service import ZMQSubscriberService
from me_worker.service.msg_service.topic import SUB_PINGPONG, SUB_ZMQ_CC_HS_DATA

from app.config.setting import setting


class EEGSubService(ZMQSubscriberService):
    topic = SUB_ZMQ_CC_HS_DATA
    ZMQ_URI = setting.eeg_setting.zmq_uri

    async def test_subscriber(self):
        if self.sub is None:
            await self.init()

        async for msg in self.sub.messages:
            print(msg.data)


eeg_subservice = EEGSubService()


async def test_sub():
    p = EEGSubService()
    # await p.init()
    await p.test_subscriber()


if __name__ == '__main__':
    p = EEGSubService()
    asyncio.run(p.test_subscriber())