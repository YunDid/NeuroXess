
import asyncio

import loguru
import numpy as np
import scipy.io
import matplotlib.pyplot as ply
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

        with open('output.txt', 'a') as file:
            # 设置输出分隔符为英文逗号
            separator = ','
            print(x, file=file)


def loadData(Right,Left):

    with open('Max.txt', 'r') as file:
        for line in file:
            # 去除每行末尾的换行符
            line = line.strip()
            # 检查内容是否为空或只包含空白字符
            if line:
                # 将内容转换为浮点数类型，并添加到列表中
                Right.append(float(line))

    with open('Min.txt', 'r') as file:
        for line in file:
            # 去除每行末尾的换行符
            line = line.strip()
            # 检查内容是否为空或只包含空白字符
            if line:
                # 将内容转换为浮点数类型，并添加到列表中
                Left.append(float(line))

    # loguru.logger.debug(Right)
    # loguru.logger.debug(Left)

def TestloadData():

    with open('Max.txt', 'r') as file:
        for line in file:
            # 去除每行末尾的换行符
            line = line.strip()
            # 检查内容是否为空或只包含空白字符
            if line:
                # 将内容转换为浮点数类型，并添加到列表中
                with open('output.txt', 'a') as file:
                    # 设置输出分隔符为英文逗号
                    separator = ','
                    print(float(line) / 40 * 33 + 2, file=file)

    # with open('Min.txt', 'r') as file:
    #     for line in file:
    #         # 去除每行末尾的换行符
    #         line = line.strip()
    #         # 检查内容是否为空或只包含空白字符
    #         if line:
    #             # 将内容转换为浮点数类型，并添加到列表中
    #             Left.append(float(line))
def TestCycle(CacheTime_data):

    # 获取预测周期时间点
    sum = 0
    TimePoint = []
    TimePoint.append(0)
    for each in CacheTime_data:
        sum2 = sum + (each * 0.1 / 2)
        sum = sum + each * 0.1
        TimePoint.append(sum2)
        TimePoint.append(sum)
    # 获取 Imu 真实时间点
    ImuRight = []
    ImuLeft = []
    loadData(ImuRight, ImuLeft)

    # 对齐时间 1s
    ImuRight = [x * 0.0025 for x in ImuRight]
    ImuLeft = [x * 0.0025 for x in ImuLeft]

    loguru.logger.debug(TimePoint)
    loguru.logger.debug(ImuRight)
    loguru.logger.debug(ImuLeft)

    # 绘制平行线
    ply.axhline(y=0, c='red', label='ImuLine')
    # Imu 右腿周期界
    y = [0] * len(ImuRight)  # 创建与结果列表长度相同的全为 0 的列表
    ply.scatter(ImuRight, y, marker='x')  # 绘制离散点，标记为 'x'
    # 绘制垂线
    for i in range(len(ImuRight)):
        x = ImuRight[i]
        y = 0.1

        ply.plot([x, x], [y, 0], color='gray', linestyle='--')

    # Imu 左腿周期界
    y = [0] * len(ImuLeft)  # 创建与结果列表长度相同的全为 0 的列表
    ply.scatter(ImuLeft, y, marker='o')  # 绘制离散点，标记为 'x'
    # 绘制垂线
    for i in range(len(ImuLeft)):
        x = ImuLeft[i]
        y = 0.1

        # ply.plot([x, x], [y, 0], color='orange', linestyle='--')

    # 预测周期界
    # 平行线
    ply.axhline(y=0.1, c='blue', label='PredictLine')
    # 绘制点

    for i, data in enumerate(TimePoint):
        # 根据索引的奇偶性选择标记类型
        marker = 'x' if i % 2 == 0 else 'o'
        color = 'gray' if i % 2 == 0 else 'orange'
        # 绘制离散点
        ply.scatter(data, 0.1, marker=marker,color=color)

    # 设置图例
    ply.legend()

    # 显示
    ply.show()

def TestCycle2(CacheTime_data):
    loguru.logger.debug(CacheTime_data)


    # 获取预测周期时间点
    sum = 0
    TimePoint = []
    TimePoint.append(0)
    for each in CacheTime_data:
        sum = sum + each
        TimePoint.append(sum)
    # 获取 Imu 真实时间点
    ImuRight = []
    ImuLeft = []
    loadData(ImuRight, ImuLeft)

    # 对齐时间 1s
    ImuRight = [x * 0.025 for x in ImuRight]
    ImuLeft = [x * 0.025 for x in ImuLeft]

    loguru.logger.debug(TimePoint)
    loguru.logger.debug(ImuRight)
    loguru.logger.debug(ImuLeft)

    # 绘制平行线
    ply.axhline(y=0, c='red', label='ImuLine')
    # Imu 右腿周期界
    y = [0] * len(ImuRight)  # 创建与结果列表长度相同的全为 0 的列表
    ply.scatter(ImuRight, y, marker='x')  # 绘制离散点，标记为 'x'
    # 绘制垂线
    for i in range(len(ImuRight)):
        x = ImuRight[i]
        y = 0.1

        ply.plot([x, x], [y, 0], color='gray', linestyle='--')

    # Imu 左腿周期界
    y = [0] * len(ImuLeft)  # 创建与结果列表长度相同的全为 0 的列表
    ply.scatter(ImuLeft, y, marker='o')  # 绘制离散点，标记为 'x'
    # 绘制垂线
    for i in range(len(ImuLeft)):
        x = ImuLeft[i]
        y = 0.1

        # ply.plot([x, x], [y, 0], color='orange', linestyle='--')

    # 预测周期界
    # 平行线
    ply.axhline(y=0.1, c='blue', label='PredictLine')
    # 绘制点

    for i, data in enumerate(TimePoint):
        # 根据索引的奇偶性选择标记类型
        marker = 'x' if i % 2 == 0 else 'o'
        color = 'gray' if i % 2 == 0 else 'orange'
        # 绘制离散点
        ply.scatter(data, 0.1, marker=marker, color=color)

    # 设置图例
    ply.legend()

    # 显示
    ply.show()

def Test2(imu_data,Brain_Data_Pri,Brain_Data_Act,Post_imu_data):

    # 测试起始位移点
    # draw(Brain_Data, 1, 0, 400, 'green', 'actual', 0)
    # draw(Post_imu_data, 1, 3600, 4000, 'blue', 'imu', 0)

    # loguru.logger.debug(len(imu_data))

    draw(Brain_Data_Pri, 1, 600, 1200, 'green', 'prediction', 0, 0.1, 100)
    draw(imu_data, 0, 16800, 19200, 'blue', 'imu', 0, 0.025, 1)
    draw(Post_imu_data, 1, 4200, 4800, 'red', 'Imu_x', 0, 0.1, 200)


    # 绘制加速度离散点+直线，一同绘制时需要设置0.25倍的x轴缩放 40hz
    # draw(imu_data, 0, 0, 4800, 'green', 'A', 0, 0.025, 1)
    # draw(imu_data, 0, 0, 2400, 'green', 'A', 0, 1, 1)

    # 绘制速度离散点+直线 10hz
    # draw(Post_imu_data,0, 0, 100,'black', 'V', 0, 0.1, 10)
    # 绘制位移离散点+直线 10hz
    # draw(Post_imu_data, 1, 0, 1200, 'red', 'X', 0, 0.1, 200)
    # loguru.logger.debug(out[0:1000, 1])

    # draw(Post_imu_data, 1, 3600, 4000, 'black', 'Imu', 0)
    # loguru.logger.debug(out2[3000:4000, 1])

    # # 绘制人工计算的周期界限 - 测试用
    # result =[0, 3.203, 6.242, 9.685, 12.751, 16.221, 19.502, 23.375, 26.011, 29.696]
    #
    # y = [-0.01] * len(result)  # 创建与结果列表长度相同的全为 0 的列表
    #
    # ply.scatter(result, y, marker='x')  # 绘制离散点，标记为 'x'
    # for i, point in enumerate(result):
    #     if i % 2 == 0:
    #         color = 'red'  # 奇数位的垂线颜色为红色
    #     else:
    #         color = 'purple'  # 偶数位的垂线颜色为紫色
    #     ply.axvline(x=point, color=color, linestyle='--', alpha=0.5)  # 绘制垂直于 x 轴的直线

    # 添加点击事件
    ply.gcf().canvas.mpl_connect('button_press_event', onclick)
    #
    # 显示
    ply.show()

def draw(data,type,datarangel,dataranger,color,lables,linepoint,scalex=1,scaley=1):

    # datarange：绘制范围 scale：y值缩放 linepoint:平行线绘制所需y值

    x_values_scale = x_values = range(len(data[datarangel:dataranger, type]))
    y_values_scale = y_values = data[datarangel:dataranger, type]
    # 设置缩放
    if scalex!=1:
        x_values_scale = [x * scalex for x in x_values]
    if scaley!=1:
        y_values_scale = [y * scaley for y in y_values]
    # 绘制离散点
    ply.scatter(x_values_scale, y_values_scale, c=color, marker='o', label=lables)
    # 绘制折线
    ply.plot(x_values_scale,y_values_scale)
    # 绘制平行线
    ply.axhline(y=linepoint, c='red', label='Line')
    # 绘制垂线
    for i in range(len(x_values_scale)):
        x = x_values_scale[i]
        y = y_values_scale[i]

        ply.plot([x, x], [y, linepoint], color='gray', linestyle='--')

    # 设置图例
    ply.legend()

async def run():
    await dog_tcp_client.init()

    # 加载预测数据
    predata = scipy.io.loadmat("D:/Yundid/Data/DogWalkingPrediction_0616.mat")
    # loguru.logger.debug(predata)

    # out = predata['actual']
    Brain_Data_Act = predata['actual']
    Brain_Data_Pri = predata['prediction']

    # out = out[0:1000, 1]

    imp = "D:/Yundid/Data/subjects_1.exps_81.origin.20230616150527_246013.g2_dog1_day37.imu"
    imu_data, times = parse_imu(imp)
    imu_data = imu_data.reshape((imu_data.shape[0], 1))
    # 含积分操作，0 速度 ，1 相对位移 - 全局初始位置(但是位置不确定)
    # imu_data = imu_data[0:24000]
    Post_imu_data = mprocessor.bin_data(imu_data, timestamp=times / 1000, bin_size=0.1, dim=[0])

    Index = 0
    # out = Post_imu_data[4201:4800]
    out = Brain_Data_Pri[626:1200]
    CacheTime_data = []
    for each in out:
        anidata = [each]
        # loguru.logger.debug(anidata)
        # loguru.logger.debug(anidata[0][1])
        await dog_tcp_client.sendEnd(anidata,CacheTime_data,Index)
        await asyncio.sleep(0.05)
        Index = Index + 1

    # TestCycle(CacheTime_data)
    # Test2(imu_data,Brain_Data_Pri,Brain_Data_Act,Post_imu_data)

    # TestloadData()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    # asyncio.run(run())
