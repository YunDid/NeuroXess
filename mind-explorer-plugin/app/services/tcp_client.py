import asyncio
import json
import socket
from urllib.parse import urlparse

import loguru
import numpy as np

from app.config.setting import setting


class TcpClient:
    def __init__(self):
        self._connect = False
        self.reader = None
        self.writer = None

    def is_connected(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        try:
            s.connect((host, port))
            return True
        except:
            return False
        finally:
            s.close()

    async def init(self):
        try:
            _url_parser = urlparse(setting.event_server)
            loguru.logger.info(f"tcp url is {setting.event_server}")
            if not self.is_connected(_url_parser.hostname, _url_parser.port):
                loguru.logger.info(f"{setting.event_server} is not connect ")
                return

            self.reader, self.writer = await asyncio.open_connection(
                _url_parser.hostname, _url_parser.port)
            self._connect = True
        except Exception as e:
            loguru.logger.error("connect fail")

    async def _send_data(self, data:dict):
        if not self._connect:
            loguru.logger.debug("not connect")
            return
        self.writer.write(json.dumps(data).encode())
        await self.writer.drain()

    async def send(self, data:dict):
        await self._send_data(data)

class DogWorkerClient(TcpClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CacheSpeed_data = []

    # 基于相对位移
    async def send(self, predict_data):
        location = predict_data[0][1]
        # loguru.logger.debug(location)

        # 延时处理指令
        # 基本逻辑 :
        # 以缓存为单位进行指令的发送，满半个周期才发送一次指令
        if len(self.CacheSpeed_data) == 0:
            # 缓存为空，直接存储当前指令
            self.CacheSpeed_data.append(location)
        else:
            # 非同类指令，说明缓存中上半个周期已经结束，开始发送
            if (location < -0.01 and self.CacheSpeed_data[-1] >= -0.01) or (location >= -0.01 and self.CacheSpeed_data[-1] < -0.01):
                location2 = np.max(self.CacheSpeed_data)
                # 清空缓存
                self.CacheSpeed_data.clear()
                # 存储下半个周期的指令
                self.CacheSpeed_data.append(location)

                # 基于梯度计算速度，发送指令
                gradient = 0

                if location2 >= -0.01:
                    leg = "RightLeg"
                    # 设置一个梯度界限,分5个梯度,0.3 - 0.7
                    gradient = (location2 - 0.03) / 0.008
                else:
                    leg = "LeftLeg"
                    # 设置一个梯度界限,分5个梯度,-0.7 - -0.3
                    gradient = abs((location2 + 0.03) / 0.008)

                time = (9 + gradient) / 33
                speed = 0.4167 / time

                data = {
                    "AnimationName": leg,
                    "Speed": speed,
                    "NeedReturnStateFlag": False
                }

                loguru.logger.debug(data)
                await self._send_data(data)
            # 同类指令，说明当前指令仍属于当前周期，直接存储
            if (location < -0.01 and self.CacheSpeed_data[-1] < -0.01) or (location >= -0.01 and self.CacheSpeed_data[-1] >= -0.01):
                self.CacheSpeed_data.append(location)
                return

# class DogWorkerClient(TcpClient):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.CacheSpeed_data = []
#
#     async def send(self, predict_data):
#         speed = predict_data[0][0]
#         loguru.logger.debug(speed)
#
#         if len(self.CacheSpeed_data) == 0:
#             self.CacheSpeed_data.append(speed)
#         else:
#             if speed * self.CacheSpeed_data[-1] < 0:
#                 speed2 = np.max(self.CacheSpeed_data)
#                 self.CacheSpeed_data.clear()
#                 self.CacheSpeed_data.append(speed)
#
#                 gradient = 0
#                 time = 9
#
#                 if speed2 < 0:
#                     leg = "RightLeg"
#                     # 设置一个梯度界限
#                     if speed2 >= 0.5:
#                         gradient = (1 - speed2) // 0.125
#                     else:
#                         gradient = 2
#                 else:
#                     leg = "LeftLeg"
#                     # 设置一个梯度界限
#                     if speed2 <= -0.2:
#                         gradient = (0.6 - speed2) // 0.1
#                     else:
#                         gradient = 2
#
#                 time = (8 + gradient) / 33
#                 speedc = 0.4617 / time
#
#                 data = {
#                     "AnimationName": leg,
#                     "Speed": speedc,
#                     "NeedReturnStateFlag": False
#                 }
#
#                 loguru.logger.debug(data)
#                 await self._send_data(data)
#             else:
#                 self.CacheSpeed_data.append(speed)
#                 return

    # async def _sendAnidata(self,speed):
    #
    #     if speed > 0:
    #         leg = "RightLeg"
    #     else:
    #         leg = "LeftLeg"
    #
    #     data = {
    #         "AnimationName": leg,
    #         "Speed": abs(speed) * 1,
    #         "NeedReturnStateFlag": False
    #     }
    #
    #     loguru.logger.debug(data)
    #     await self._send_data(data)