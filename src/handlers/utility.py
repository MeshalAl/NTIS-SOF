from datetime import datetime


def get_epoch_time() -> int:
    return int(datetime.now().timestamp())
