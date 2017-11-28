# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

import warnings


class PyAlgoTradeDeprecationWarning(DeprecationWarning):
    pass

warnings.simplefilter("default", PyAlgoTradeDeprecationWarning)


# Deprecation warnings are disabled by default in Python 2.7, so this helper function enables them back.
def deprecation_warning(msg, stacklevel=0):
    warnings.warn(msg, category=PyAlgoTradeDeprecationWarning, stacklevel=stacklevel+1)
