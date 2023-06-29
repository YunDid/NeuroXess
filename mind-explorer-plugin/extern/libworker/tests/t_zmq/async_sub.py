import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

import bson
import zmq
import zmq.asyncio

context = zmq.asyncio.Context()
# 'tcp://*:56010'
async def run():
    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://localhost:56010')

    #  Do 10 requests, waiting each time for a response
    # for request in range(10):
    #     print("Sending request %s …" % request)
    #     socket.send(b"Hello")
    #
    #     #  Get the reply.
    #     message = socket.recv()
    #     print("Received reply %s [ %s ]" % (request, message))
    socket.setsockopt(zmq.SUBSCRIBE, "".encode('utf-8'))
    print("dddd")
    while True:
        topic, *msg = await socket.recv_multipart()
        print(topic, msg)
        # await socket.send_multipart([b'tr', b'/ddd'])


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
asyncio.run(run())