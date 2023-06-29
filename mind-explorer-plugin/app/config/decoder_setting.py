import enum
import os
from typing import List, Tuple

import loguru
from pydantic import BaseSettings, Field


env_path = os.environ.get("ENV_PATH", '.env')
loguru.logger.info(f"env_path={env_path}")


class TargetTypeEnum(str, enum.Enum):
    pos = 'pos'
    vel = 'vel'
    acc = 'acc'


class MotionInputTypeEnum(str, enum.Enum):
    pos = 'pos'
    acc = 'acc'


class Base(BaseSettings):
    class Config:
        env_file = env_path
        case_sensitive = False  # 环境变量的名称大小写敏感(默认大小写不敏感)


class NeuroSetting(Base):
    neuro_sample_rate: int = Field(4000, description=" Sampling rate of neural signal.")
    neuro_freq_notch_filter: List[int] = Field(default=[50, 100, 200],
                                               description="Frequencies to be eliminated in notch filter")
    neuro_quality_notch_filter: List[int] = Field(default=[50, 35, 50],
                                               description="Quality factor of notch filter. Note the length of qnotch should")

    neuro_freq_bandpass_filter: List[float] = Field([0.3, 500],
                                                              description="Frequency ranges of bandpass filter the neural signal.")

    neural_fbands:List[List[int]] = Field([[70, 200]],description=".")

    neuro_order_bandp_lowp_filter: int = Field(4, description="Filter order of the bandpass and lowpass filter (For LMP feature).")
    neuro_bad_channels: List[int] = Field([], description=" Bad channels to be removed before preprocessing.")

    neuro_time_half_bandwidth: float = Field(2.5, description="Time half bandwidth parameter for pmtm")

    neuro_car: bool = True
    neuro_lmp: bool = Field(True, description="Computing LMP as one of neural feature or not")


class BehaviorSetting(Base):
    behavior_inp_type: MotionInputTypeEnum = Field( MotionInputTypeEnum.acc, description="输入运动数据类型")
    behavior_target_type: List[TargetTypeEnum] = Field([TargetTypeEnum.pos, TargetTypeEnum.vel], description="解码目标类型")
    behavior_sample_rate: int = Field(40, description="Samping frequency of motion data.")
    behavior_input_filter: str =  Field(None)
    behavior_freq_cutoff:List[int] =  Field([1, 5], description="""The cutoff frequency of inp_filter. If the inp_filter is "low" or
            "high", the inp_fc should be a scalar. If the inp_filter is
            "bandpass", the inp_fc should be a list.""")
    behavior_target_filter: str = Field("high", description="""The type of filter applied to the target motion data. Can be either
            of "low", "high", "bandpass" or None. Default: None.""")
    behavior_target_freq_cutoff: int = Field(1, description="""The cutoff frequency of trg_filter. If the trg_filter is "low" or
            "high", the trg_fc should be a scalar. If the trg_filter is
            "bandpass", the trg_fc should be a list. Default: None.""")
    behavior_order_filter: int = Field(4, description="The order of the preprocessing filters.")  #  阶数


class DecoderSetting(Base):
    bin_size: float = Field(0.1, description="解码窗宽")
    nbins_train: int= Field(1000, description="训练数据时长")
    ncomponents: int = Field(50, description="解码特征数")
    cross_validation_kfold: int = Field(5, description="k-Fold cross validation")
    neuro: NeuroSetting
    behavior: BehaviorSetting


class DogWalkDecodeSetting(BaseSettings):
    motion_field: str = "x"

