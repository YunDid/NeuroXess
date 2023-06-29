#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: task_persisitance.py 
@time: 2022/01/11
@contact: 
@site:  
@software: PyCharm 
"""
import abc
import datetime
import enum
import traceback
import uuid

import sqlalchemy
from loguru import logger
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, create_engine, Integer, Enum, Text, BLOB, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from me_worker.background_task.config import setting, DBType

# 创建对象的基类:
Base = declarative_base()


class TaskEnum(str, enum.Enum):
    create = "create"
    running = "running"
    success = 'success'
    complete = 'complete'
    fail = 'fail'
    retry = 'retry'


# 定义对象:
class Task(Base):
    # 表的名字:
    __tablename__ = setting.TASK_TB_NAME
    
    # 表的结构:
    task_id = Column(String(127), primary_key=True, comment="主键，唯一id")
    trace_id = Column(String(511), comment="")
    status = Column(Enum(*list(TaskEnum.__members__.values())))
    info = Column(String(511), comment="")
    func = Column(BLOB(), comment="")
    k_args = Column(BLOB(), comment="")
    k_kwargs = Column(BLOB(), comment="")
    err_msg = Column(Text(), comment="")
    create_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    update_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")
    
    # def __getstate__(self):
    #     d = self.__dict__.copy()
    #     d.pop('_parents', None)
    #     return d


class TaskModel(BaseModel):
    task_id: str = Field(None, description="任务id")
    trace_id: str = Field(None, description="trace_id")
    status: TaskEnum = Field(TaskEnum.create)
    info: str = Field(None, description="其他信息")
    func: bytes = Field(None, description="序列化后的方法")
    k_args: bytes = Field(None, description="参数")
    k_kwargs: bytes = Field(None, description="关键字参数")
    err_msg: str = Field(None)
    
    @validator("task_id")
    def gen_task_id(cls, val):
        # logger.debug("dddddddd")
        if val is None:
            val = uuid.uuid4().hex
        return val


class BasePersistance(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def add_task(self, task: TaskModel):
        ...
    
    @abc.abstractmethod
    def update_task(self, task_id, task: TaskModel):
        ...
    
    @abc.abstractmethod
    def query_by_status(self, status: TaskEnum):
        ...
    
    def query_by_task_id(self, task_id):
        ...
    
    def query_by_trace_id(self, task_id):
        ...
    
    def get_task_and_retry(self, task_id):
        ...


class NoPersistance(BasePersistance):
    
    def add_task(self, task: TaskModel):
        logger.warning("Not Persistance, return None")
    
    def update_task(self, task_id, task: TaskModel):
        logger.warning("Not Persistance, return None")
    
    def query_by_status(self, status: TaskEnum):
        logger.warning("Not Persistance, return None")
    
    def query_by_task_id(self, task_id):
        logger.warning("Not Persistance, return None")
    
    def query_by_trace_id(self, task_id):
        logger.warning("Not Persistance, return None")
    
    def get_task_and_retry(self, task_id):
        logger.warning("Not Persistance, return None")


class MysqlPersistance(BasePersistance):
    def __init__(self):
        sql_uri = f'mysql+pymysql://{setting.TASK_DB_USER}:{setting.TASK_DB_PASSWD}@{setting.TASK_DB_HOST}:{setting.TASK_DB_PORT}/{setting.TASK_DB_NAME}'
        logger.debug(sql_uri)
        self._engine = create_engine(sql_uri, pool_recycle=1)
        # 创建DBSession类型
        self.DBSession = sessionmaker(bind=self._engine)
        self.create_all()
    
    def create_all(self):
        Base.metadata.create_all(self._engine)
    
    def add_task(self, task: TaskModel):
        task_dict = task.dict(exclude_none=True)
        logger.debug(task.task_id)
        task_dict['status'] = task_dict['status'].value
        # logger.debug(task_dict)
        task_tb = Task(**task_dict)
        session = self.DBSession()
        try:
            session.add(task_tb)
            # 提交即保存到数据库:
            session.commit()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()
    
    def update_task(self, task_id, task: TaskModel):
        logger.debug(task_id)
        session = self.DBSession()
        try:
            task_model = session.query(Task).filter(Task.task_id == task_id).one()
            for k, v in task.dict(exclude={"task_id"}, exclude_none=True).items():
                setattr(task_model, k, v)
            # 提交即保存到数据库:
            session.commit()
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()
    
    def _excute(self, session, func, *args, retry=2, **kwargs):
        try:
            data = func(args, kwargs)
            return data
        except sqlalchemy.exc.OperationalError as err:
            logger.error(f"{err.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
            if retry > 0:
                return self._excute(session, func, *args, retry=retry - 1, **kwargs)
            else:
                raise err
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
            raise e
        finally:
            session.close()
    
    def query_by_status(self, status: TaskEnum):
        session = self.DBSession()
        try:
            data = session.query(Task).filter(Task.status == status.value).all()
            return data
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()
    
    def query_all(self, limit=10, offset=0):
        session = self.DBSession()
        try:
            data = session.query(Task).limit(limit).offset(offset).all()
            return data
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()
    
    def get_task_and_retry(self, task_id):
        """
        获取任务并重试
        :param task_id:
        :return:
        """
        session = self.DBSession()
        try:
            with session.begin_nested():
                task = session.query(Task).filter(Task.task_id == task_id).with_for_update()
                # task = session.query(Task).filter(Task.task_id == task_id)
                if not task:
                    raise RuntimeError
                task = task.one()
                task.status = TaskEnum.retry.value
                session.commit()
                logger.debug(task.status)
                return task
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
            raise e
        finally:
            session.close()
    
    def query_by_task_id(self, task_id) -> Task:
        session = self.DBSession()
        try:
            data = session.query(Task).filter(Task.task_id == task_id).one()
            return data
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()
    
    def query_by_trace_id(self, trace_id):
        session = self.DBSession()
        try:
            data = session.query(Task).filter(Task.trace_id == trace_id).order_by(Task.update_at.desc()).all()
            return data
        except Exception as e:
            logger.error(f"{e.__class__.__name__}\n{traceback.format_exc()}")
            session.rollback()
        finally:
            session.close()


persistance_dict = {
    DBType.mysql: MysqlPersistance,
    DBType.not_persistance: NoPersistance
}


def persistance_factory():
    logger.debug(f"{setting.TASK_DB_TYPE}")
    return persistance_dict[setting.TASK_DB_TYPE]()


persistance = persistance_factory()
