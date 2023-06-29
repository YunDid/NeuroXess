import asyncio

import loguru

from me_worker.service.msg_service.msg_adapter import msg_adapter_producer, ZmqSubscriber
from me_worker.service.msg_service.topic import SUB_PINGPONG, SUB_ZMQ_CC_HS_DATA
#  uri="tcp://127.0.0.1:56010"

class PingpongSub:

    def __init__(self):
        self._client = msg_adapter_producer.get_msg_adapter("zmq",uri="tcp://127.0.0.1:56010")

    async def init(self):
        ...

    async def sub(self):
        loguru.logger.debug(f"topic={SUB_PINGPONG}")
        sub: ZmqSubscriber = await self._client.subscribe(SUB_PINGPONG, pending_msgs_limit=5)
        i = 0
        # time.sleep(6)
        # while True:
        #     print(i, await sub.next_msg(2))
        #     i+=1
        #     if i == 5:
        #         msg_client.unsubscribe('test')
        loguru.logger.debug("start sub")
        async for msg in sub.messages:
            print(msg)


if __name__ == '__main__':
    p = PingpongSub()
    asyncio.run(p.sub())
