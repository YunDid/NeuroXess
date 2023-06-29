from pydantic import BaseModel


# 订阅的采集器的实时数据格式
class CollectRawDataSubModel(BaseModel):
    channels: int
    time: int
    buffer: bytes
    precision: int
    sample_rate: int