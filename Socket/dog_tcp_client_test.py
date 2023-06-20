
import asyncio

import loguru
import numpy as np
from decoder.fitting import MotionPreprocess

from app.services.tcp_client import DogWorkerClient
from app.config.decoder_setting import DecoderSetting, BehaviorSetting, MotionInputTypeEnum, TargetTypeEnum

motion_fs = 40
behavior=BehaviorSetting(behavior_inp_type=MotionInputTypeEnum.acc,
                               behavior_target_type=[TargetTypeEnum.pos, TargetTypeEnum.vel],
                               behavior_sample_rate=motion_fs,
                               behavior_input_filter="bandpass",
                               behavior_freq_cutoff=[1, 5],
                               behavior_target_filter="high",
                               behavior_target_freq_cutoff=1,
                               behavior_order_filter=4
                               )
# decode_conf = DecoderSetting()
dog_tcp_client = DogWorkerClient()
mprocessor: MotionPreprocess = MotionPreprocess(inp_type=behavior.behavior_inp_type.value,
                                                trg_type="-".join(behavior.behavior_target_type),
                                                fs=np.array(behavior.behavior_sample_rate),
                                                             inp_filter=behavior.behavior_input_filter,
                                                             inp_fc=behavior.behavior_freq_cutoff,
                                                             trg_filter=behavior.behavior_target_filter,
                                                             trg_fc=behavior.behavior_target_freq_cutoff,
                                                             order=behavior.behavior_order_filter
                                                             )

def parse_imu(inp):
    from tools.simulator.imu_parse_service import imu_parser_service, ImuHeader

    with open(inp, 'rb') as fr:
        h_data = fr.read(4096)
        a = ImuHeader.parse_bytes(h_data)
        print(a.create_at)
        sys_time = 0
        data = []
        times = []
        while True:

            d = fr.read(1)
            if d:
                # print(d)
                if list(d) == [0x11]:
                    d2 = fr.read(72 + 8)
                    if not d2: break
                    out = imu_parser_service.parse_imu(bytearray(d + d2))
                    data.extend([out.acceleration.x])
                    if not sys_time:
                        sys_time = out.sys_time
                    times.append(int((out.sys_time - sys_time) * 10e-7))
                    # print(out)
                else:
                    loguru.logger.error(d)
            else:
                break
        data = np.asarray(data)
        return data, np.asarray(times)


# 获取鼠标点击位置的坐标
def onclick(event):
    if event.ydata is not None:
        x = event.xdata
        print("鼠标点击的横坐标:", x)


CacheSpeed_data = []
async def run():
    await dog_tcp_client.init()
    imp = "D:/Yundid/Data/subjects_1.exps_81.origin.20230616150527_246013.g2_dog1_day37.imu"
    imu_data, times = parse_imu(imp)
    imu_data = imu_data.reshape((imu_data.shape[0], 1))
    out = mprocessor.bin_data(imu_data, timestamp=times / 1000, bin_size=0.1, dim=[0])
    # print(out)
    # speeds = out[0, :]
    loguru.logger.debug(out.shape)

    count = 0
    for each in out:
        count = count + 1
        anidata = [each]
        await dog_tcp_client.send(anidata)
        await asyncio.sleep(0.1)
        # if count == 10:
        #     break

    # import matplotlib.pyplot as ply
    # ply.plot(out[:1000, 0])
    # x = [0,1000]
    # y = [0,0]
    # ply.plot(0)
    # ply.plot(x,y)
    # ply.gcf().canvas.mpl_connect('button_press_event', onclick)
    # ply.show()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    # asyncio.run(run())
