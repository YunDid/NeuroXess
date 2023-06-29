from pydantic import BaseModel

class SectionInfo(BaseModel):
    length: int
    offset: int
    data_len: int
    data: bytes

class CereCubeFrameInfo(BaseModel):
    type: str
    size: int


class TTLInfo(BaseModel):
    type: str
    size: int

class CereCubeInfo(BaseModel):
    version: int
    count_of_channels: int
    sample_rate: int
    layout_length: int
    frame: CereCubeFrameInfo
    ttl: TTLInfo
    section: SectionInfo = None



class CereCubeMeta(BaseModel):
    data_type: str
    record_id: str
    section: SectionInfo = None
    data: dict = None
