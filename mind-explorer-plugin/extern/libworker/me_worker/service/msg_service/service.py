import asyncio
import os.path

import aiohttp
import bson
import loguru
import nats
from me_worker.config.settings import setting
from me_worker.service.msg_service.msg_adapter import msg_adapter_producer
import abc

from me_worker.errors.my_errors import AnalysisError


class ReqErrors(Exception):
    ...

class Service(metaclass=abc.ABCMeta):
    topic = ''

    def __init__(self):
        self._client = None

    async def init(self):
        self._client = await nats.connect(setting.nats.nats_uri, error_cb=self.err_call)


    async def err_call(self, e, *args, **kwargs):
        loguru.logger.error(
            f"{e}")
        ...

    async def option_post_json(self, url, data, headers, retry=3):
        loguru.logger.debug(data)
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        # content = await resp.content
                        loguru.logger.error(f"{resp.status}-{await resp.content.read()}")
        except Exception as e:
            loguru.logger.error(e)

        if retry > 0:
            return await self.option_post_json(url, data, headers, retry=retry - 1)
        raise ReqErrors(f"Req[Response url={url}] fail")

    async def option_get_json(self, url, headers, retry=3):
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        # content = await resp.content
                        loguru.logger.error(f"{resp.status}-{await resp.content.read()}")
        except Exception as e:
            loguru.logger.error(e)

        if retry > 0:
            return await self.option_get_json(url, headers, retry=retry - 1)
        raise ReqErrors(f"Req[Response url={url}] fail")

    async def get_storage_from_path(self, data_uri):
        if setting.storage_service.storage_service_mock:
            loguru.logger.warning("mock storage_service_mock")
            return os.path.join(setting.storage_path, data_uri)
        url = setting.storage_service.STORAGE_SERVICE_URL
        url = f"{url}?path={data_uri}"
        loguru.logger.info(f"req url={url}")
        data = await  self.option_get_json(url, {})
        loguru.logger.info(f"get data={data}")
        if 'code' in data and data['code'] == 404:
            raise AnalysisError(data['message'])

        if 'code' in data and data['code'] == 200 and 'data' in data and 'abspath' in data['data']:
            return data['data']['abspath']

        raise AnalysisError("storage service error")


    async def publish(self, msg):
        await self._client.publish(self.topic, msg)

    @abc.abstractmethod
    async def sub_callback(self, msg):
        ...


    def get_chanmap_by_channel(self, channel):
        chmap_path = os.path.join(setting.chmap_dir, f'chanMap_3B_{channel}sites_py.mat')
        if not chmap_path or not os.path.isfile(chmap_path):
            raise AnalysisError(f"chmap file不存在；不支持的channel【{channel}】")
        return chmap_path

    async def subscribe(self):
        if self._client is None:
            await self.init()
        loguru.logger.info(f"current topic {self.topic}")
        sub = await self._client.subscribe(self.topic, cb=self.sub_callback)

    async def subscibe_loop(self):
        if self._client is None:
            await self.init()
        loguru.logger.info(f"current topic {self.topic}")
        sub = await self._client.subscribe(self.topic, pending_msgs_limit=setting.pending_task_num)
        try:
            async for msg in sub.messages:
                # loguru.logger.debug(f"get data from {msg.subject} {msg.reply}")
                # data = msg.data
                # message = bson.loads(data)
                await self.sub_callback(msg)
        except Exception as e:
            loguru.logger.exception(e)
            raise e

