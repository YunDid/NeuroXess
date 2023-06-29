import json
import struct

from sdk.py_librecord.model import SectionInfo, CereCubeMeta, CereCubeFrameInfo, TTLInfo, CereCubeInfo


class RecordRead:
    def __init__(self, file_path):
        self.megic_num = None
        self.check_sum = None
        self.meta_info:CereCubeMeta = None
        self.cerecube_info:CereCubeInfo = None
        self.section_length = 18
        self.meta_length = 12
        self.f_reader = open(file_path, 'rb')

    def _read_file_info(self, header_buffer):
        fmt = '<QI'
        rest = struct.unpack(fmt, header_buffer[:12])
        self.megic_num, self.check_sum = rest

    def __del__(self):
        self.f_reader.close()

    def _read_metainfo(self, section):
        buffer = section.data
        self.meta_info = CereCubeMeta(
            data_type=buffer[:4].decode(),
            record_id=buffer[4:40],
            section=section
        )

    def _read_cerecube_info(self, section: SectionInfo):
        # fmt = "=LHLHccccLccccL"
        cere_info_fmt = "<LHLH"
        buffer = section.data
        rest = struct.unpack(cere_info_fmt, buffer[:12])
        frame = CereCubeFrameInfo(
            type=buffer[12:16].decode(),
            size=struct.unpack("<H", buffer[16:18])[0]
        )
        ttl = TTLInfo(
            type=buffer[18:22].decode().strip(),
            size=struct.unpack("<H", buffer[22:24])[0]
        )
        self.cerecube_info = CereCubeInfo(version=rest[0],
                            count_of_channels=rest[1] * 32,
                            sample_rate=rest[2],
                            layout_length=rest[3],
                            section=section,
                            frame=frame,
                            ttl=ttl)

    def get_section(self, buffer):
        fmt = '<HQQ'
        rest = struct.unpack(fmt, buffer[:18])
        data = buffer[18:rest[0]]
        return SectionInfo(length=rest[0], offset=rest[1], data_len=rest[2], data=data)

    def get_meta_info(self):
        return self.meta_info

    def get_cerecube_info(self):
        return self.cerecube_info

    def read_header(self):
        self.f_reader.seek(0)
        header_buffer = self.f_reader.read(4096)
        self._read_file_info(header_buffer)
        current_offset = self.meta_length
        section = self.get_section(header_buffer[current_offset:])
        self._read_metainfo(section)

        current_offset = current_offset + section.length
        section = self.get_section(header_buffer[current_offset:])
        self._read_cerecube_info(section)

    def _read_meta_data_info(self):
        if self.cerecube_info is None:
            self.read_header()
        offset = self.meta_info.section.offset + 4096
        self.f_reader.seek(offset)
        buffer = self.f_reader.read(self.meta_info.section.data_len)
        # self.meta_info.data = json.loads(buffer)

    def run(self):
        self.read_header()
        self._read_meta_data_info()

    def trans_to_ttl_and_raw(self, raw_data_path, ttl_data_path, callback=None):
        offset = self.cerecube_info.section.offset + 4096
        end_offset = self.cerecube_info.section.data_len + offset if self.cerecube_info.section.data_len!=0 else None
        self.f_reader.seek(offset)
        frame_size = self.cerecube_info.frame.size
        ttl_size = self.cerecube_info.ttl.size
        reader_len = frame_size + ttl_size
        with open(raw_data_path, 'wb') as f_bin, open(ttl_data_path, 'wb') as f_ttl:
            current_len = 0
            flush_tag = 0
            while True:
                # if self.cerecube_info.section.data_len < current_len: break
                frame = self.f_reader.read(reader_len)
                if len(frame) < reader_len:
                    break
                flush_tag += 1
                current_len += reader_len
                f_bin.write(frame[:self.cerecube_info.frame.size])
                f_ttl.write(frame[self.cerecube_info.frame.size:])
                if flush_tag % 100 == 0:
                    f_bin.flush()
                    if callback:
                        callback(0.1)
                if flush_tag % 10000 == 0:
                    f_ttl.flush()

    def get_frame(self):
        offset = self.cerecube_info.section.offset + 4096
        end_offset = self.cerecube_info.section.data_len + offset if self.cerecube_info.section.data_len != 0 else None
        self.f_reader.seek(offset)
        frame_size = self.cerecube_info.frame.size
        ttl_size = self.cerecube_info.ttl.size
        reader_len = frame_size + ttl_size
        while True:
            # if self.cerecube_info.section.data_len < current_len: break
            frame = self.f_reader.read(reader_len)
            if len(frame) < reader_len:
                break
            yield frame[:self.cerecube_info.frame.size]




if __name__ == '__main__':
    data_path = r"D:\data\local\2\origin\test-17-32-35.mex"
    raw_data_path = r"D:\data\local\2\origin\test_17-32-35_raw.bin"
    ttl_path = r"D:\data\local\2\origin\test_17-32-35_ttl.bin"
    record = RecordRead(data_path)
    record.run()
    import numpy as np
    # record.trans_to_ttl_and_raw(raw_data_path=raw_data_path, ttl_data_path=ttl_path)
    for frame in record.get_frame():
        print(frame)
        data = np.ndarray(record.cerecube_info.count_of_channels, dtype=np.int16, buffer=frame)
        print(data)
        break