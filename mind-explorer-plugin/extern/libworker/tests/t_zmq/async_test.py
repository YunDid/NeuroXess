import asyncio

import loguru
import zmq
import zmq.asyncio

ctx = zmq.asyncio.Context()

url="tcp://127.0.0.1:5555"

async def async_process(msg):
    loguru.logger.debug(msg)
    return msg

async def recv_and_process():
    sock = ctx.socket(zmq.REQ)
    sock.connect(url)
    for i in range(10):
        reply = b"dddddd"
        await sock.send(reply)
        msg = await sock.recv_multipart() # waits for msg to be ready
        print(msg)
    # reply = await async_process(msg)


asyncio.run(recv_and_process())