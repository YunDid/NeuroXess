import enum
from me_worker.config.settings import setting

topic_environment_tag = ""
if setting.environment != 'prod':
    setting.environment = setting.environment if setting.environment else 'dev'
    topic_environment_tag = '.'+ setting.environment


# 订阅的topic常量
SUB_DATA_CC_RAW_RT = f'D.CC.RAW.RT{topic_environment_tag}'  # 订阅的采集器的实时数据

SUB_ZMQ_CC_HS_DATA = f"cc-hs-data{topic_environment_tag}"  # 脑电数据

SUB_ANALYSIS_SORTING_ALGO = f'A.ALGO.SORT{topic_environment_tag}'  # 订阅的sorting分析指令

SUB_ANALYSIS_PEVENT_RASTER_ALGO = f'A.ALGO.PEVENT{topic_environment_tag}'  # 订阅的sorting分析指令

SUB_ANALYSIS_METRICS_ALGO = f'A.ALGO.METRICS{topic_environment_tag}'  # 订阅的sorting分析指令

SUB_EVENT = f'D.CC.EVENT.RT{topic_environment_tag}'  # 事件worker

SUB_IMU = f'D.CC.IMU.RT{topic_environment_tag}' # 运动
SUB_PINGPONG = f"D.CC.PINGPONG.RT{topic_environment_tag}" # 游戏乒乓
SUB_FLAPPY_BIRD = f"D.CC.FLAPPY.RT{topic_environment_tag}" # 游戏flappy bird

# 发布的topic常量
PUB_DATA_SPIKE = f'D.ALGO.SPIKE.RT{topic_environment_tag}'  # spike算法产生的数据
# PUB_DATA_WAVE = 'D.ALGO.DATAWAVE.RT'  # DATAWAVE算法产生的数据


if __name__ == '__main__':
    print()