#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: config.py 
@time: 2022/01/11
@contact: 
@site:  
@software: PyCharm 
"""
import os

# os.environ.setdefault("TASK_RETRY", "yes")
from pydantic import BaseSettings, Field
import enum


@enum.unique
class DBType(str, enum.Enum):
    mysql = 'mysql'
    not_persistance = 'not_persistance'


class TaskSetting(BaseSettings):
    TASK_DB_TYPE: DBType = DBType.mysql
    TASK_DB_HOST: str = "localhost"
    TASK_DB_PORT: int = 3306
    TASK_DB_USER: str = "root"
    TASK_DB_PASSWD: str = "root"
    TASK_DB_NAME: str = "test"
    TASK_TB_NAME: str = "tb_crawler_task"
    TASK_RETRY: bool = False


setting = TaskSetting()

if __name__ == '__main__':
    print(setting.dict(exclude={"TASK_DB_NAME"}))
