# !pip install pysnowflake


import time
import logging
from datetime import datetime

import snowflake.client

# 定义常量
del_flag = 0

# 链接服务端并初始化一个pysnowflake客户端
host = 'localhost'
port = 8910
snowflake.client.setup(host, port)

    

    


# # 64位ID的划分
# WORKER_ID_BITS = 5
# DATACENTER_ID_BITS = 5
# SEQUENCE_BITS = 12

# # 最大取值计算
# MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
# MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

# # 移位偏移计算
# WOKER_ID_SHIFT = SEQUENCE_BITS
# DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
# TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# # 序号循环掩码
# SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# # Twitter元年时间戳
# TWEPOCH = 1288834974657


# logger = logging.getLogger('flask.app')


# class IdWorker(object):
#     """
#     用于生成IDs
#     """

#     def __init__(self, datacenter_id, worker_id, sequence=0):
#         """
#         初始化
#         :param datacenter_id: 数据中心（机器区域）ID
#         :param worker_id: 机器ID
#         :param sequence: 其实序号
#         """
#         # sanity check
#         if worker_id > MAX_WORKER_ID or worker_id < 0:
#             raise ValueError('worker_id值越界')

#         if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
#             raise ValueError('datacenter_id值越界')

#         self.worker_id = worker_id
#         self.datacenter_id = datacenter_id
#         self.sequence = sequence

#         self.last_timestamp = -1  # 上次计算的时间戳

#     def _gen_timestamp(self):
#         """
#         生成整数时间戳
#         :return:int timestamp
#         """
#         return int(time.time() * 1000)

#     def get_id(self):
#         """
#         获取新ID
#         :return:
#         """
#         timestamp = self._gen_timestamp()

#         # 时钟回拨
#         if timestamp < self.last_timestamp:
#             logging.error('clock is moving backwards. Rejecting requests until {}'.format(self.last_timestamp))
#             raise

#         if timestamp == self.last_timestamp:
#             self.sequence = (self.sequence + 1) & SEQUENCE_MASK
#             if self.sequence == 0:
#                 timestamp = self._til_next_millis(self.last_timestamp)
#         else:
#             self.sequence = 0

#         self.last_timestamp = timestamp

#         new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
#                  (self.worker_id << WOKER_ID_SHIFT) | self.sequence
#         return new_id

#     def _til_next_millis(self, last_timestamp):
#         """
#         等到下一毫秒
#         """
#         timestamp = self._gen_timestamp()
#         while timestamp <= last_timestamp:
#             timestamp = self._gen_timestamp()
#         return timestamp


# 主键id生成器
def generate_id(worker_id = 1, data_center_id = 1, sequence = 0):
    return snowflake.client.get_guid()
    # worker = IdWorker(worker_id, data_center_id, sequence)
    # return worker.get_id()
    
    # # 获取当前时间戳
    # current_timestamp = int(time.time_ns())
    # return current_timestamp

    # # # 将时间戳转换为16进制字符串,并删除前两个字符"0x"
    # # id_str = hex(current_timestamp)[2:]
    # # # 如果长度不足16位,则在前面补0
    # # id_str = id_str.zfill(20)
    # # return int(id_str, 20)


# 时间戳生成器
def generate_time():
    # 格式: YY-MM-DD HH:MM:SS
    form_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # print(form_time)
    return form_time



# 数据插入前预处理
def pre_insert(item):
    item.id, item.create_time, item.del_flag = generate_id(), generate_time(), del_flag
    return item


# 将datetime类型的数据转换为字符串，以便后续json格式化
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    