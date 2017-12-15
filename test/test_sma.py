# -*- coding: utf-8 -*-

# @Time    : 2017/12/10 3:33
# @Author  : Zhongyu
# @File    : test_sma.py


"""
sma函数与talib的sma函数对比
"""


import numpy
import talib
import time
from dmwTrader.technical import ma
from dmwTrader import dataseries


close = numpy.random.random(100)
print(close)
print()

# talib
start1 = time.time()
output1 = talib.SMA(close, 30)
end1 = time.time()
# print(output1)


# dmwTrader
start2 = time.time()
seqDS = dataseries.SequenceDataSeries()
output2 = ma.SMA(seqDS, 30)
for ele in close:
    seqDS.append(ele)
    # print(output2[-1])
end2 = time.time()


# 检查是否一致
# for i in range(100):
#     if numpy.isnan(output1[i]) and output2[i] is None:
#         print('neither')
#     elif not numpy.isnan(output1[i]) and output2[i] is not None:
#         print(round(output1[i] - output2[i], 10))
#     else:
#         print("error")


print("talib time: " + str(end1 - start1))
print("pyalgotrade time: " + str(end2 - start2))
