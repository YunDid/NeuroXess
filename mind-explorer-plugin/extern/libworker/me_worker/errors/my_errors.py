

class BaseError(Exception):
    message = ""

    def __init__(self, message=None):
        self.message = message if message is not None else self.message

    def __str__(self):
        return self.message


class AnalysisError(BaseError):
    message = "分析异常"


class NoSpikeError(BaseError):
    message = "No spikes detected"


class ComputationError(BaseError):
    message = "原始数据异常"


class DiskNotEnoughError(BaseError):
    message = "磁盘空间不足"


class WorkerBusyError(BaseError):
    message = "worker繁忙，请稍后重试"
