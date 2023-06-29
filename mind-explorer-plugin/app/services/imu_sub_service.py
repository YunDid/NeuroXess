import asyncio

import loguru
from me_worker.service.msg_service.msg_adapter import ZmqSubscriber, msg_adapter_producer
from me_worker.service.msg_service.topic import SUB_IMU
from me_worker.service.zmq_subscriber_service import ZMQSubscriberService
from app.config.setting import setting


class IMURecordSubService(ZMQSubscriberService):
    topic = SUB_IMU
    ZMQ_URI = setting.imu_setting.zmq_uri

    async def test_subscriber(self):
        if self.sub is None:
            await self.init()
        async for msg in self.sub.messages:
            print(msg.data)

imu_subservice = IMURecordSubService()

if __name__ == '__main__':
    p = IMURecordSubService()
    asyncio.run(p.test_subscriber())
