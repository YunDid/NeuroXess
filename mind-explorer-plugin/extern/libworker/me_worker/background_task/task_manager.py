#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: task_manager.py
@time: 2022/01/11
@contact: 
@site:  
@software: PyCharm 
"""
import asyncio
import enum
import json
import dill as pickle
import time
import traceback
import uuid
from collections import deque
# from dataclasses import Field

from loguru import logger
from pydantic import BaseModel, validator, Field

from me_worker.background_task.config import setting
from me_worker.background_task.actor import BackgroundWorker
from me_worker.background_task.task_persisitance import TaskModel, TaskEnum, persistance


class NullWorkerError(Exception):
    ...


class MutilWorkerManager:
    def __init__(self, worker_num=2):
        self.work_pools = deque()  # 空闲worker
        self.working_pools = dict()  # 工作中的worker
        self.create_worker_pool(num=worker_num)
        if setting.TASK_RETRY:
            self.retry_running_and_create()

    def retry_running_and_create(self):
        self.retry_by_status(TaskEnum.running)
        self.retry_by_status(TaskEnum.create)

    def create_worker_pool(self, num=8):
        logger.info(f"create worker: {num}")
        for i in range(num):
            worker_ = BackgroundWorker()
            self.working_pools.setdefault(worker_, 0)
            self.work_pools.append(worker_)

    def get_worker(self) -> BackgroundWorker:
        if self.work_pools:
            worker_ = self.work_pools.popleft()
            self.working_pools[worker_] += 1
            return worker_
        else:
            logger.warning("all worker is busy, waiting ")
            if not self.working_pools: raise NullWorkerError("null working_pools")
            workers = sorted(self.working_pools.items(), key=lambda x: x[1])
            self.working_pools[workers[0][0]] += 1
            return workers[0][0]

    def update_task(self, task: TaskModel):
        persistance.update_task(task.task_id, task)

    def add_task(self, task: TaskModel):
        persistance.add_task(task)

    async def _work_run(self, func, task_model: TaskModel, worker, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                resp = await func(*args, **kwargs)
            else:
                resp = func(*args, **kwargs)
            task_model.status = TaskEnum.success
            self.update_task(task_model)
            return resp
        except Exception as e:
            info = f"{e.__class__.__name__}\n{traceback.format_exc()}"
            task_model.err_msg = info
            task_model.status = TaskEnum.fail
            self.update_task(task_model)
            raise e
        finally:
            self.release_worker(worker)

    def retry_by_status(self, status: TaskEnum):
        logger.info(f"retry {status}")
        tasks = persistance.query_by_status(status=status)
        for task in tasks:
            try:
                task = persistance.get_task_and_retry(task.task_id)
            except Exception as e:
                logger.warning(f"{e.__class__.__name__}\n{traceback.format_exc()}")
                continue
            self._retry_task(task)

    def _retry_task(self, task):
        logger.debug(task.__dict__)
        func = pickle.loads(task.func)
        args = pickle.loads(task.k_args) if task.k_args else []
        kwargs = pickle.loads(task.k_kwargs)
        task_model = TaskModel(task_id=task.task_id, status=TaskEnum.running)
        worker_ = self.get_worker()
        future = worker_.submit(self._work_run, func, task_model, worker_, *args, **kwargs)
        return future

    def retry_by_id(self, task_id):
        """
        重试任务
        :param task_id: 任务id
        :return:
        """
        task = persistance.get_task_and_retry(task_id)
        # logger.debug(task.func)
        return self._retry_task(task)

    def worker_submit(self, func, *args, trace_id=None, **kwargs):
        func_pickle = pickle.dumps(func, protocol=pickle.HIGHEST_PROTOCOL)

        k_args = pickle.dumps(args, protocol=pickle.HIGHEST_PROTOCOL) if args else None
        k_kwargs = pickle.dumps(kwargs, protocol=pickle.HIGHEST_PROTOCOL)

        task_id = uuid.uuid3(uuid.NAMESPACE_DNS, time.time().hex()).hex
        task_model = TaskModel(task_id=task_id,
                               trace_id=trace_id,
                               func=func_pickle,
                               k_args=k_args,
                               k_kwargs=k_kwargs
                               )
        self.add_task(task_model)
        worker_ = self.get_worker()
        future = worker_.submit(self._work_run, func, task_model, worker_, *args, **kwargs)
        return task_model.task_id

    def release_worker(self, worker_):
        self.working_pools[worker_] -= 1
        if self.working_pools[worker_] <= 0:
            self.work_pools.append(worker_)


task_manager = MutilWorkerManager()
