import loguru
from pydantic import BaseSettings, validator, root_validator
import os, sys

def pyinstaller_cwd():
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        return sys._MEIPASS
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        return os.environ['_MEIPASS2']
    return None

def chdir():
    wd = pyinstaller_cwd()
    if wd is not None:
        loguru.logger.info(f"chdir: {wd}")
        os.chdir(wd)

chdir()

env_path = os.environ.get("ENV_PATH", '.env')

# nats 配置信息
class NatsSetting(BaseSettings):
    nats_uri: str = 'nats://192.168.50.224:4222'
    pending_msgs_limit: int = 100

    class Config:
        env_file = env_path
        case_sensitive = False # 环境变量的名称大小写敏感(默认大小写不敏感)


class ZmqSetting(BaseSettings):
    zmq_uri: str = 'tcp://127.0.0.1:16480'

    class Config:
        env_file = env_path
        case_sensitive = False  # 环境变量的名称大小写敏感(默认大小写不敏感)


class StorageServiceSetting(BaseSettings):
    STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL","http://192.168.50.57:18081/api/v1/storage/meta/file")
    COLD_BASEPATH=os.getenv("COLD_BASEPATH","")
    storage_path: str = r"E:\data\mind-explore-sorting\out"
    storage_service_mock: bool = False

    class Config:
        env_file = env_path
        case_sensitive = False # 环境变量的名称大小写敏感(默认大小写不敏感)

# 配置信息
class Settings(BaseSettings):
    algo_config_path: str = r'D:\develop\py\mind-explorer-sorting\eMouse\config_eMouse_drift.ini' # 算法所需配置文件路径
    rez_temp_path: str = r"E:\data\mind-explore-sorting\out\rez_final.mat"
    storage_path: str = r"E:\data\mind-explore-sorting\out"
    chmap_path: str = r"E:\data\mind-explore-sorting\chanMap_3B_256sites_py.mat"
    spike_read_times: int = 10   # 每次计算的数据量大小，默认10ms
    nats: NatsSetting = NatsSetting()  # nats 相关配置
    zmq_setting: ZmqSetting = ZmqSetting()
    mock_algo: bool = False  # 是否mock算法模块
    environment: str = "prod"  # 工作环境 prod, dev, test
    timeout_cutter: bool = True  # 算法超时，丢弃部分超时数据
    loguru_level: str = "TRACE"
    loguru_path: str = ""
    temp_train_time: int = 1
    ttl_size: int = 2
    storage_service: StorageServiceSetting = StorageServiceSetting()
    pending_task_num: int = 1000
    RESOURCE_ROOT_PATH: str = ''
    rt_pending_num: int = 1000  # 实时分析最大冗余数， 超过一半，会丢弃10%
    rt_pending_bytes: int = 4 * 1024 * 1024 * 1024

    @root_validator(pre=True)
    def check_sum(cls, values):
        # loguru.logger.debug(cls)
        # if values.get('RESOURCE_ROOT_PATH'):
        #     for each in ['rez_temp_path', 'algo_config_path']:
        #         values[each] = os.path.join(values['RESOURCE_ROOT_PATH'], values[each])
        return values


    class Config:
        env_file = env_path
        case_sensitive = False


setting = Settings()
loguru.logger.debug(setting)
