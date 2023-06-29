import os

import loguru
from pydantic import BaseSettings

env_path = os.environ.get("ENV_PATH", '.env')
loguru.logger.info(f"env_path={env_path}")


class Base(BaseSettings):
    class Config:
        env_file = env_path
        case_sensitive = False  # 环境变量的名称大小写敏感(默认大小写不敏感)

class GameSetting(Base):
    zmq_uri: str = 'tcp://localhost:56010'


class ImuSetting(Base):
    zmq_uri: str = 'tcp://localhost:16490'

class EEGSetting(Base):
    zmq_uri: str = 'tcp://localhost:16480'


class Setting(Base):
    game_setting: GameSetting = GameSetting()
    eeg_setting: EEGSetting = EEGSetting()
    imu_setting: ImuSetting = ImuSetting()
    event_server: str = "tcp://localhost:8888"


setting = Setting()