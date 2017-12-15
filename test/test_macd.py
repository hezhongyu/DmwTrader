# -*- coding: utf-8 -*-

# @Time    : 2017/12/10 2:57
# @Author  : Zhongyu
# @File    : test_macd.py

"""
macd模块与talib的macd函数对比
"""


import numpy
import talib
import time
from dmwTrader.technical import macd
from dmwTrader import dataseries


close = numpy.random.random(100)
print(close)
print()

# talib
start1 = time.time()
output1_macd, output1_macdsignal, output1_macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
end1 = time.time()
# print(output1_macd)
# print(output1_macdsignal)
# print(output1_macdhist)


# dmwTrader
start2 = time.time()
seqDS = dataseries.SequenceDataSeries()
output2 = macd.MACD(seqDS)
for ele in close:
    seqDS.append(ele)
    # print(output2[-1])
end2 = time.time()


# # 检查MACD是否一致
# for i in range(100):
#     if numpy.isnan(output1_macd[i]) and output2[i] is None:
#         print('neither')
#     elif not numpy.isnan(output1_macd[i]) and output2[i] is not None:
#         print(output1_macd[i] - output2[i])
#     else:
#         print("error")
#
# # 检查MACD_signal是否一致
# for i in range(100):
#     if numpy.isnan(output1_macdsignal[i]) and output2.getSignal()[i] is None:
#         print('neither')
#     elif not numpy.isnan(output1_macdsignal[i]) and output2.getSignal()[i] is not None:
#         print(output1_macdsignal[i] - output2.getSignal()[i])
#     else:
#         print("error")

# 检查MACD_hist是否一致
for i in range(100):
    if numpy.isnan(output1_macdhist[i]) and output2.getHistogram()[i] is None:
        print('neither')
    elif not numpy.isnan(output1_macdhist[i]) and output2.getHistogram()[i] is not None:
        print(output1_macdhist[i] - output2.getHistogram()[i])
    else:
        print("error")



print("talib time: " + str(end1 - start1))
print("pyalgotrade time: " + str(end2 - start2))