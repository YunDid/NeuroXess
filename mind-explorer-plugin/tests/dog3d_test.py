import asyncio
import json

import loguru


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8889)

    # print(f'Send: {message!r}')
    print("connect success")
    i = 0
    while True:
        leg = "LeftLeg"
        if i%2 == 0:
            leg = 'RightLeg'

        data = {
            "AnimationName": leg,
            "Speed": 2.0,
            "NeedReturnStateFlag": False
        }
        loguru.logger.debug(data)
        writer.write(json.dumps(data).encode())
        await writer.drain()
        await asyncio.sleep(0.1)
        i+=1

    # data = await reader.read(100)
    # print(f'Received: {data.decode()!r}')
    #
    # print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client('Hello World!'))