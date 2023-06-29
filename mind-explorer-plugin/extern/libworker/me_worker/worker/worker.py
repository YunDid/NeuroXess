import time

import loguru
import asyncio

class Worker:

    async def prepare(self):
        ...

    async def do(self):
        ...

    async def done(self):
        ...

    async def run(self):
        loguru.logger.info("worker start")
        await self.prepare()
        await self.do()
        await self.done()
        loguru.logger.info("worker finished")


if __name__ == '__main__':
    w = Worker()
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(w.run())