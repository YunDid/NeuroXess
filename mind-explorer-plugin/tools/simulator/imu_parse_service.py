"""
pip install pydantic==1.10.7
win-precise-time==1.4.1
"""

import csv
import glob
import json
import struct
from array import array
import win_precise_time as wpt
import loguru
from pydantic import BaseModel, Field


class XYZBaseModel(BaseModel):
    x: float
    y: float
    z: float
    w: float = None

class RecordModel(BaseModel):
    time: float = None
    device_time: float = None
    acceleration: XYZBaseModel = None  #  加速度
    gravity: XYZBaseModel = None  # 重力
    height: float = None
    xyz: XYZBaseModel = None  # 三维坐标
    angular_speed: XYZBaseModel = None # 角速度
    magnetic_field: XYZBaseModel = None  # 磁场
    navigation_a: XYZBaseModel = None # 导航加速度
    euler_angle: XYZBaseModel = None  # 欧拉角
    walk: bool = False
    walk_num: int = None
    run: bool = False
    run_num: int = None
    sys_time: int = Field(default_factory=wpt.time_ns)


class ImuHeader(BaseModel):
    sample_rate: int            # I  uint
    create_at: int              # Q  unsigned long long
    data_offset: int = 4096     # I  uint

    def to_bytes(self):
        return struct.pack('<IQI', self.sample_rate, self.create_at, self.data_offset)

    @classmethod
    def parse_bytes(cls, buffer):
        sample_rate, create_at, data_offset = struct.unpack('<IQI', buffer[:16])
        return cls(sample_rate=sample_rate, create_at=create_at, data_offset=data_offset)


class ImuParseService:
    def __init__(self):
        self.start = None

    def parse_imu(self, buf):
        scaleAccel = 0.00478515625  # 加速度 [-16g~+16g]    9.8*16/32768
        scaleQuat = 0.000030517578125  # 四元数 [-1~+1]         1/32768
        scaleAngle = 0.0054931640625  # 角度   [-180~+180]     180/32768
        scaleAngleSpeed = 0.06103515625  # 角速度 [-2000~+2000]    2000/32768
        scaleMag = 0.15106201171875  # 磁场 [-4950~+4950]   4950/32768
        scaleTemperature = 0.01  # 温度
        scaleAirPressure = 0.0002384185791  # 气压 [-2000~+2000]    2000/8388608
        scaleHeight = 0.0010728836  # 高度 [-9000~+9000]    9000/8388608

        imu_dat = array('f', [0.0 for i in range(0, 34)])

        if buf[0] == 0x11:
            ctl = (buf[2] << 8) | buf[1]
            # print(" subscribe tag: 0x%04x" % ctl)
            # print(" ms: ", ((buf[6] << 24) | (buf[5] << 16) | (buf[4] << 8) | (buf[3] << 0)))
            device_time = ((buf[6] << 24) | (buf[5] << 16) | (buf[4] << 8) | (buf[3] << 0))
            if self.start is None:
                self.start = device_time

            record = RecordModel(device_time=device_time, time=device_time-self.start)
            if len(buf) == 73 + 8:
                sys_time = struct.unpack("<q", buf[-8:])
                record.sys_time = sys_time[0]

            L = 7  # 从第7字节开始根据 订阅标识tag来解析剩下的数据
            if ((ctl & 0x0001) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\taX: %.3f" % tmpX);  # x加速度aX
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\taY: %.3f" % tmpY);  # y加速度aY
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\taZ: %.3f" % tmpZ);  # z加速度aZ

                imu_dat[0] = float(tmpX)
                imu_dat[1] = float(tmpY)
                imu_dat[2] = float(tmpZ)
                record.acceleration = XYZBaseModel(x=tmpX, y=tmpY, z=tmpZ)

            #
            if ((ctl & 0x0002) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tAX: %.3f" % tmpX)  # x加速度AX
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tAY: %.3f" % tmpY)  # y加速度AY
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tAZ: %.3f" % tmpZ)  # z加速度AZ

                imu_dat[3] = float(tmpX)
                imu_dat[4] = float(tmpY)
                imu_dat[5] = float(tmpZ)

                record.gravity = XYZBaseModel(x=tmpX, y=tmpY, z=tmpZ)

            #
            if ((ctl & 0x0004) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngleSpeed;
                L += 2
                # print("\tGX: %.3f" % tmpX)  # x角速度GX
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngleSpeed;
                L += 2
                # print("\tGY: %.3f" % tmpY)  # y角速度GY
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngleSpeed;
                L += 2
                # print("\tGZ: %.3f" % tmpZ)  # z角速度GZ

                imu_dat[6] = float(tmpX)
                imu_dat[7] = float(tmpY)
                imu_dat[8] = float(tmpZ)
                angular_speed = XYZBaseModel(x=tmpX,y=tmpY,z=tmpZ)
                record.angular_speed = angular_speed
            # print(" ")
            if ((ctl & 0x0008) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleMag;
                L += 2
                # print("\tCX: %.3f" % tmpX);  # x磁场CX
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleMag;
                L += 2
                # print("\tCY: %.3f" % tmpY);  # y磁场CY
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleMag;
                L += 2
                # print("\tCZ: %.3f" % tmpZ);  # z磁场CZ

                imu_dat[9] = float(tmpX)
                imu_dat[10] = float(tmpY)
                imu_dat[11] = float(tmpZ)

            # print(" ")
            if ((ctl & 0x0010) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleTemperature;
                L += 2
                # print("\ttemperature: %.2f" % tmpX)  # 温度

                tmpU32 = np.uint32(((np.uint32(buf[L + 2]) << 16) | (np.uint32(buf[L + 1]) << 8) | np.uint32(buf[L])))
                if ((tmpU32 & 0x800000) == 0x800000):  # 若24位数的最高位为1则该数值为负数，需转为32位负数，直接补上ff即可
                    tmpU32 = (tmpU32 | 0xff000000)
                tmpY = np.int32(tmpU32) * scaleAirPressure;
                L += 3
                # print("\tairPressure: %.3f" % tmpY);  # 气压

                tmpU32 = np.uint32((np.uint32(buf[L + 2]) << 16) | (np.uint32(buf[L + 1]) << 8) | np.uint32(buf[L]))
                if ((tmpU32 & 0x800000) == 0x800000):  # 若24位数的最高位为1则该数值为负数，需转为32位负数，直接补上ff即可
                    tmpU32 = (tmpU32 | 0xff000000)
                tmpZ = np.int32(tmpU32) * scaleHeight;
                L += 3
                # print("\theight: %.3f" % tmpZ);  # 高度

                imu_dat[12] = float(tmpX)
                imu_dat[13] = float(tmpY)
                imu_dat[14] = float(tmpZ)
                record.height = tmpZ

            # print(" ")
            if ((ctl & 0x0020) != 0):
                tmpAbs = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleQuat;
                L += 2
                # print("\tz: %.3f" % tmpAbs);  # w
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleQuat;
                L += 2
                # print("\tw: %.3f" % tmpX);  # x
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleQuat;
                L += 2
                # print("\tx: %.3f" % tmpY);  # y
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleQuat;
                L += 2
                # print("\ty: %.3f" % tmpZ);  # z

                imu_dat[15] = float(tmpAbs)
                imu_dat[16] = float(tmpX)
                imu_dat[17] = float(tmpY)
                imu_dat[18] = float(tmpZ)

            # print(" ")
            if ((ctl & 0x0040) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngle;
                L += 2
                # print("\tangleX: %.3f" % tmpX);  # x角度
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngle;
                L += 2
                # print("\tangleY: %.3f" % tmpY);  # y角度
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAngle;
                L += 2
                # print("\tangleZ: %.3f" % tmpZ);  # z角度

                imu_dat[19] = float(tmpX)
                imu_dat[20] = float(tmpY)
                imu_dat[21] = float(tmpZ)

            # print(" ")
            if ((ctl & 0x0080) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) / 1000.0;
                L += 2
                # print("\toffsetX: %.3f" % tmpX);  # x坐标
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) / 1000.0;
                L += 2
                # print("\toffsetY: %.3f" % tmpY);  # y坐标
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) / 1000.0;
                L += 2
                # print("\toffsetZ: %.3f" % tmpZ);  # z坐标

                imu_dat[22] = float(tmpX)
                imu_dat[23] = float(tmpY)
                imu_dat[24] = float(tmpZ)
                record.xyz = XYZBaseModel(x=float(tmpX), y=float(tmpY), z=float(tmpZ))

            # print(" ")
            if ((ctl & 0x0100) != 0):
                tmpU32 = ((buf[L + 3] << 24) | (buf[L + 2] << 16) | (buf[L + 1] << 8) | (buf[L] << 0));
                L += 4
                # print("\tsteps: %u" % tmpU32);  # 计步数
                record.walk_num = tmpU32
                tmpU8 = buf[L];
                L += 1
                if (tmpU8 & 0x01):  # 是否在走路
                    # print("\t walking yes")
                    record.walk = True
                    imu_dat[25] = 100
                else:
                    # print("\t walking no")
                    record.walk = False
                    imu_dat[25] = 0
                if (tmpU8 & 0x02):  # 是否在跑步
                    # print("\t running yes")
                    record.run = True
                    imu_dat[26] = 100
                else:
                    # print("\t running no")
                    record.run = False
                    imu_dat[26] = 0
                if (tmpU8 & 0x04):  # 是否在骑车
                    # print("\t biking yes")
                    imu_dat[27] = 100
                else:
                    # print("\t biking no")
                    imu_dat[27] = 0
                if (tmpU8 & 0x08):  # 是否在开车
                    # print("\t driving yes")
                    imu_dat[28] = 100
                else:
                    # print("\t driving no")
                    imu_dat[28] = 0

            # print(" ")
            if ((ctl & 0x0200) != 0):
                tmpX = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tasX: %.3f" % tmpX);  # x加速度asX
                tmpY = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tasY: %.3f" % tmpY);  # y加速度asY
                tmpZ = np.short((np.short(buf[L + 1]) << 8) | buf[L]) * scaleAccel;
                L += 2
                # print("\tasZ: %.3f" % tmpZ);  # z加速度asZ

                imu_dat[29] = float(tmpX)
                imu_dat[30] = float(tmpY)
                imu_dat[31] = float(tmpZ)

            # print(" ")
            if ((ctl & 0x0400) != 0):
                tmpU16 = ((buf[L + 1] << 8) | (buf[L] << 0));
                L += 2
                # print("\tadc: %u" % tmpU16);  # adc测量到的电压值，单位为mv
                imu_dat[32] = float(tmpU16)

            # print(" ")
            if ((ctl & 0x0800) != 0):
                tmpU8 = buf[L];
                L += 1
                # print("\t GPIO1  M:%X, N:%X" % ((tmpU8 >> 4) & 0x0f, (tmpU8) & 0x0f))
                imu_dat[33] = float(tmpU8)
            loguru.logger.trace(f"{record.time} {imu_dat}")
            return record
        else:
            loguru.logger.error("[error] data head not define")


imu_parser_service = ImuParseService()

import numpy as np

def translate_to_bin(filepath):
    save_path = filepath + '.acceleration.bin'

    data = []
    with open(filepath, 'rb') as fr, open(save_path, 'wb') as fw:
        h_data = fr.read(16)
        a = ImuHeader.parse_bytes(h_data)
        print(a.create_at)
        while True:

            d = fr.read(1)
            if d:
                # print(d)
                if list(d) == [0x11]:
                    d2 = fr.read(72 + 8)
                    if not d2: break
                    out = imu_parser_service.parse_imu(bytearray(d + d2))

                    data.extend([out.sys_time, out.acceleration.x, out.acceleration.y, out.acceleration.z])
                    # print(out)
                else:
                    loguru.logger.error(d)
            else:
                break
        data = np.asarray(data)
        fw.write(data)


def translate_to_csv(filepath):
    save_path = filepath + '.csv'
    with open(filepath, 'rb') as fr, open(save_path, 'w', newline='') as fw:
        h_data = fr.read(16)
        a = ImuHeader.parse_bytes(h_data)
        print(a)
        writer = None
        while True:

            d = fr.read(1)
            if d:
                # print(d)
                if list(d) == [0x11]:
                    d2 = fr.read(72+8)
                    if not d2: break
                    out = imu_parser_service.parse_imu(bytearray(d+d2))
                    if writer is None:
                        writer = csv.DictWriter(fw, fieldnames=list(out.dict().keys()))
                        writer.writeheader()
                    tmp = out.dict()
                    for k,v in tmp.items():
                        if isinstance(v, dict):
                            tmp[k] = json.dumps(v, ensure_ascii=False)
                    writer.writerow(tmp)

                    # print(out)
                else:
                    loguru.logger.error(d)
            else:
                break


if __name__ == '__main__':

    file_dir = r'D:\data\mex-data'
    for each in glob.glob(f"{file_dir}/*.imu"):
        print(each)
        translate_to_bin(each)

