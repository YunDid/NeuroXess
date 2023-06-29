import abc
import asyncio
import sys
import time
import warnings
from asyncio import QueueFull, WindowsSelectorEventLoopPolicy
from typing import Dict, Type, Optional, AsyncIterator

import loguru
import nats
import zmq
import zmq.asyncio
from nats import errors
from nats.aio.msg import Msg
from nats.aio.subscription import _SubscriptionMessageIterator, DEFAULT_SUB_PENDING_BYTES_LIMIT, \
    DEFAULT_SUB_PENDING_MSGS_LIMIT
from nats.errors import SlowConsumerError
from zmq.sugar.context import ST

from me_worker.config.settings import setting
from me_worker.utilitys.async_run import async_qt


class AdapterErr(Exception):
    ...


class MsgAdapterImp(metaclass=abc.ABCMeta):
    def __init__(self,  *args, **kwargs):
        ...

    async def init(self, **kwargs):
        ...

    @abc.abstractmethod
    async def publish(self, topic, msg, **kwargs):
        ...

    @abc.abstractmethod
    async def subscribe(self, topic, **kwargs):
        ...


class NatsAdapter(MsgAdapterImp):
    NAT_URI = setting.nats.nats_uri

    def __init__(self, *args, **kwargs):
        self.nats_client = None

    def check_adapter(self):
        if self.nats_client is None:
            raise AdapterErr("nats adapter not init; please call adapter.init()")

    async def init(self, **kwargs):
        self.nats_client = await nats.connect(self.NAT_URI)

    async def publish(self, topic, msg):
        await self.nats_client.publish(topic, msg)

    async def subscribe(self, topic, **kwargs):
        sub = await self.nats_client.subscribe(topic, **kwargs)
        return sub

    async def error_cb(self, err, *args, **kwargs):
        # print(args, kwargs)
        loguru.logger.error(err)
        if isinstance(err, (QueueFull, SlowConsumerError)):
            loguru.logger.debug(err)


class ZmqSubscriber:
    def __init__(self, topic,
                 max_msgs: int = 0,
                 pending_msgs_limit: int = DEFAULT_SUB_PENDING_MSGS_LIMIT,
                 pending_bytes_limit: int = DEFAULT_SUB_PENDING_BYTES_LIMIT,
                 cb=None,
                 err_call=None,
                 future: Optional[asyncio.Future] = None
                 ):

        self._topic = topic
        self._max_msgs = max_msgs
        self._received = 0
        self._pending_size = 0
        self._cb = cb
        self._pending_queue: "asyncio.Queue[Msg]" = asyncio.Queue(maxsize=pending_msgs_limit)
        self._pending_bytes_limit = pending_bytes_limit
        self._pending_msgs_limit = pending_msgs_limit
        self._err_call = err_call
        self._future = future
        self._wait_for_msgs_task = None
        self._message_iterator = None
        # if self._cb:
        #     async_qt.async_run(self._wait_for_msgs(self._err_call))

    async def add(self, msg):
        try:
            err = None
            if not self._pending_queue.full():
                if self._pending_size >= self._pending_bytes_limit:
                    err = f"SlowConsumer [drop msg {self._topic}]：bytes over Threshold {self._pending_size} >= {self._pending_bytes_limit}"
                else:
                    await self._pending_queue.put(msg)
                    self._pending_size += len(msg.data)
            else:
                err = f"SlowConsumer [drop msg {self._topic}]：msg queue id full"
        except Exception as e:
            err = e

        if err:
            if self._err_call:
                if asyncio.iscoroutinefunction(self._err_call):
                    await self._err_call(err)
                else:
                    self._err_call(err)
            else:
                loguru.logger.error(err)

    async def __anext__(self):
        return await self.next_msg(timeout=1)

    @property
    def pending_msgs(self) -> int:
        """
        Number of delivered messages by the NATS Server that are being buffered
        in the pending queue.
        """
        return self._pending_queue.qsize()

    @property
    def messages(self) -> AsyncIterator['Msg']:
        """
        Retrieves an async iterator for the messages from the subscription.

        This is only available if a callback isn't provided when creating a
        subscription.
        """
        if not self._message_iterator:
            raise errors.Error(
                "cannot iterate over messages with a non iteration subscription type"
            )

        return self._message_iterator

    @property
    def pending_bytes(self) -> int:
        """
        Size of data sent by the NATS Server that is being buffered
        in the pending queue.
        """
        return self._pending_size

    def _start(self, error_cb):
        """
        Creates the resources for the subscription to start processing messages.
        """
        if self._cb:
            if not asyncio.iscoroutinefunction(self._cb) and \
                    not (hasattr(self._cb, "func") and asyncio.iscoroutinefunction(self._cb.func)):
                raise errors.Error(
                    "zmq: must use coroutine for subscriptions"
                )

            self._wait_for_msgs_task = asyncio.get_running_loop().create_task(
                self._wait_for_msgs(error_cb)
            )

        elif self._future:
            # Used to handle the single response from a request.
            pass
        else:
            self._message_iterator = _SubscriptionMessageIterator(self)

    async def _wait_for_msgs(self, error_cb) -> None:
        """
        A coroutine to read and process messages if a callback is provided.

        Should be called as a task.
        """
        assert self._cb, "_wait_for_msgs can be called only from _start"
        while True:
            try:
                msg = await self._pending_queue.get()
                self._pending_size -= len(msg.data)

                try:
                    # Invoke depending of type of handler.
                    await self._cb(msg)
                except asyncio.CancelledError:
                    # In case the coroutine handler gets cancelled
                    # then stop task loop and return.
                    break
                except Exception as e:
                    # All errors from calling a handler
                    # are async errors.
                    if error_cb:
                        await error_cb(e)
                finally:
                    # indicate the message finished processing so drain can continue
                    self._pending_queue.task_done()

                # Apply auto unsubscribe checks after having processed last msg.
                # if self._max_msgs > 0 and self._received >= self._max_msgs and self._pending_queue.empty:
                #     self._stop_processing()

            except asyncio.CancelledError:
                break

    async def next_msg(self, timeout=10):
        future = asyncio.Future()

        async def _next_msg() -> None:
            msg = await self._pending_queue.get()
            self._pending_size -= len(msg.data)
            future.set_result(msg)

        task = asyncio.get_running_loop().create_task(_next_msg())
        try:
            msg = await asyncio.wait_for(future, timeout)
            return msg
        except asyncio.TimeoutError:
            future.cancel()
            task.cancel()
            raise asyncio.TimeoutError
        except asyncio.CancelledError:
            future.cancel()
            task.cancel()
            # Call timeout otherwise would get an empty message.
            raise asyncio.TimeoutError

    async def unsubscribe(self, limit: int = 0):
        ...


class ZmqAdapter(MsgAdapterImp):
    msg_class: Type[Msg] = Msg
    ZMQ_URI = setting.zmq_setting.zmq_uri

    def __init__(self, uri:str = None):
        self._zmq_uri = uri if uri is not None else self.ZMQ_URI
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        self._ctx = zmq.asyncio.Context()
        self._zmq_client: ST = None
        self._zmq_topic_map: Dict[str, ZmqSubscriber] = {}
        self._reading_task: Optional[asyncio.Task] = None

    async def init(self, **kwargs):
        loguru.logger.info(f"start connect zmq {self._zmq_uri}")
        self._zmq_client = self._ctx.socket(zmq.SUB)
        self._zmq_client.connect(self._zmq_uri)
        # async_qt.async_run(self.run(), errcall=self._err_call)
        self._reading_task = asyncio.get_running_loop().create_task(self.run())

    async def _err_call(self, e):
        loguru.logger.error(e)

    async def subscribe(self, topic, **kwargs):
        if not self._zmq_client:
            await self.init()

        if topic not in self._zmq_topic_map:
            sub = ZmqSubscriber(topic, **kwargs)
            self._zmq_topic_map[topic] = sub
            self._zmq_client.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))
            sub._start(kwargs.get('cb'))
        else:
            sub = self._zmq_topic_map[topic]
        return sub

    def unsubscribe(self, topic):
        sub = self._zmq_topic_map.pop(topic)

    async def run(self):
        loguru.logger.debug("runing zmq")
        while True:
            topic, *msg = await self._zmq_client.recv_multipart()
            loguru.logger.trace(f"get data from {topic}")
            topic = topic.decode()
            if topic in self._zmq_topic_map:
                msg = self.msg_class(subject=topic,
                                     reply=b'',
                                     data=msg,
                                     headers={},
                                     _client=self,
                                     )
                await self._zmq_topic_map[topic].add(msg)

    async def publish(self, topic, msg, **kwargs):
        warnings.warn("not imp")


class MsgAdapterProducer:
    def __init__(self):
        ...

    def get_msg_adapter(self, adapter='nats', *args, uri:str=None, **kwargs):
        """

        :param adapter: zmq or nats
        :param args:
        :param uri: zmq addr. exemple: "tcp://127.0.0.1:5555"
        :param kwargs:
        :return:
        """
        if adapter == 'zmq':
            return ZmqAdapter(uri)
        return NatsAdapter()


msg_adapter_producer = MsgAdapterProducer()

if __name__ == '__main__':
    msg_client = msg_adapter_producer.get_msg_adapter('zmq')

    async def call(msg):
        print(msg)

    async def run():
        sub: ZmqSubscriber = await msg_client.subscribe('test',pending_msgs_limit=5)
        i = 0
        # time.sleep(6)
        # while True:
        #     print(i, await sub.next_msg(2))
        #     i+=1
        #     if i == 5:
        #         msg_client.unsubscribe('test')
        async for msg in sub.messages:
            print(msg)


    asyncio.run(run())