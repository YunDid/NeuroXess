import json
import random
import struct
from sdk.py_librecord.model import SectionInfo, CereCubeMeta, CereCubeFrameInfo, TTLInfo, CereCubeInfo

class RecordWrite:
    def __init__(self,out_file, megic_num=12, check_sum=12):
        self.megic_num = megic_num
        self.check_sum = check_sum
        self.mate:CereCubeMeta = None
        self.cerecube_info:CereCubeInfo = None
        self._out_fd = open(out_file, 'wb')
        self._write_offset = 0

    def __del__(self):
        self._out_fd.close()

    def set_meta_info(self, meta: CereCubeMeta):
        self.mate = meta

    def set_cerecube_info(self, cerecube_info: CereCubeInfo):
        self.cerecube_info = cerecube_info

    def write(self, buffer):
        ...

    def write_header(self):
        buffer = b''
        fmt = '<Q'
        megic_buf = struct.pack(fmt, self.megic_num)
        buffer += megic_buf
        fmt = '<I'
        check_sum_buf = struct.pack(fmt, self.check_sum)
        buffer += check_sum_buf
        fmt = '<HQQ'
        meta_section_buffer = struct.pack(fmt, self.mate.section.length,
                                          self.mate.section.offset,
                                          self.mate.section.data_len,
                                          )
        buffer += meta_section_buffer
        buffer += self.mate.data_type.encode() + self.mate.record_id.encode()
        fmt = '<HQQLHLH'
        cere_section_buffer = struct.pack(fmt, self.cerecube_info.section.length,
                                          self.cerecube_info.section.offset,
                                          self.cerecube_info.section.data_len,
                                          self.cerecube_info.version,
                                          self.cerecube_info.count_of_channels // 32,
                                          self.cerecube_info.sample_rate,
                                          self.cerecube_info.layout_length
                                          )
        buffer+=cere_section_buffer
        buffer +=self.cerecube_info.frame.type.encode()
        fmt='<H'
        buffer += struct.pack(fmt, self.cerecube_info.frame.size)
        buffer += self.cerecube_info.ttl.type.encode()
        fmt = '<H'
        buffer += struct.pack(fmt, self.cerecube_info.ttl.size)
        self._out_fd.seek(0)
        self._out_fd.write(buffer)

    def write_meta_json(self):
        self._out_fd.seek(4096+self.mate.section.offset)
        self._out_fd.write(json.dumps(self.mate.data).encode())

    def write_stream(self, buffer, buffer_offset):
        self._out_fd.seek(4096 + self.cerecube_info.section.offset+buffer_offset)
        self._out_fd.write(buffer)
        self._out_fd.flush()

    def write_data(self, buffer):
        self._out_fd.seek(4096 + self.cerecube_info.section.offset)
        self._out_fd.write(buffer)


if __name__ == '__main__':
    import numpy as np
    r_w = RecordWrite(r"D:\data\local\2\origin\eMouse_2048ch_30s.bin", check_sum=2139062143, megic_num=10517713973265394741)
    """
 version: int
    count_of_channels: int
    sample_rate: int
    layout_length: int
    frame: CereCubeFrameInfo
    ttl: TTLInfo
    
     length: int
    offset: int
    data_len: int
    """
    data = {
        "aa": 12
    }
    data_len = len(json.dumps(data).encode())
    sectioninfo = SectionInfo(offset=0, data_len=data_len, length=58, data=b'')
    meta = CereCubeMeta(data_type="JSON",
                        record_id="123456789012345678901234567890123456",
                        data=data,
                        section=sectioninfo)
    r_w.set_meta_info(meta)

    sectioninfo = SectionInfo(offset=data_len, data_len=data_len, length=46, data=b'')
    cere_info = CereCubeInfo(section=sectioninfo,
                             version=1,
                             count_of_channels=2048,
                             sample_rate=30000,
                             layout_length=16,
                             frame=CereCubeFrameInfo(size=256, type='dddd'),
                             ttl=TTLInfo(size=2, type='ttl0')
                             )
    r_w.set_cerecube_info(cere_info)
    r_w.write_header()
    d = r"D:\data\2048ch_eMouse\eMouse_2048ch_30s.bin"
    channel = 256
    size = channel * 2 * 30000
    with open(d, 'rb') as f:
        # buffer = b''
        offset = 0
        while True:
            data = f.read(size)
            if not data or len(data) < (channel*2):
                break
            d = np.ndarray((len(data)//(channel*2), channel), dtype=np.int16, buffer=data)
            n = random.randint(1, 10)
            if n == 3:
                # di = np.random.randint(0, 16, (len(data)//256, 1), dtype=np.int16)
                s = len(data)//(channel*2)
                d1 =  np.zeros((s - 10, 1), dtype=np.int16)
                d2 = np.random.randint(0, 16, (10, 1), dtype=np.int16)
                di = np.concatenate((d1,d2))
            else:
                di = np.zeros((len(data)//(channel*2), 1), dtype=np.int16)
            data = np.hstack((d,di))
            # buffer += data.tobytes()
            # print(len(buffer))
            r_w.write_stream(data.tobytes(), offset)
            offset += len(data.tobytes())
            print(offset)
            # if offset > 50 * 1024 * 1024 * 1024:
            #     break

        # r_w.write_data(buffer)

