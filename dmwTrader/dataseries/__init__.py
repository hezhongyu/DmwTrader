# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

import abc

from dmwTrader import observer
from dmwTrader.utils import collections

DEFAULT_MAX_LEN = 1024


def get_checked_max_len(maxLen):
    if maxLen is None:
        maxLen = DEFAULT_MAX_LEN
    if not maxLen > 0:
        raise Exception("Invalid maximum length")
    return maxLen


# It is important to inherit object to get __getitem__ to work properly.
# Check http://code.activestate.com/lists/python-list/621258/
class DataSeries(abc.ABC):
    """Base class for data series.

    .. note::
        This is a base class and should not be used directly.
    """

    @abc.abstractmethod
    def __len__(self):
        """Returns the number of elements in the data series."""
        raise NotImplementedError()

    def __getitem__(self, key):
        """Returns the value at a given position/slice. It raises IndexError if the position is invalid,
        or TypeError if the key type is invalid."""
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key >= len(self) or key < 0:
                raise IndexError("Index out of range")
            return self.getValueAbsolute(key)
        else:
            raise TypeError("Invalid argument type")

    # This is similar to __getitem__ for ints, but it shouldn't raise for invalid positions.
    @abc.abstractmethod
    def getValueAbsolute(self, pos):
        raise NotImplementedError()

    @abc.abstractmethod
    def getDateTimes(self):
        """Returns a list of :class:`datetime.datetime` associated with each value."""
        raise NotImplementedError()


class SequenceDataSeries(DataSeries):
    """A DataSeries that holds values in a sequence in memory.

    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, maxLen=None):
        super(SequenceDataSeries, self).__init__()
        maxLen = get_checked_max_len(maxLen)

        self.__newValueEvent = observer.Event()
        self.__values = collections.ListDeque(maxLen)
        self.__dateTimes = collections.ListDeque(maxLen)

    def __len__(self):
        return len(self.__values)

    def __getitem__(self, key):
        return self.__values[key]

    def setMaxLen(self, maxLen):
        """Sets the maximum number of values to hold and resizes accordingly if necessary."""
        self.__values.resize(maxLen)
        self.__dateTimes.resize(maxLen)

    def getMaxLen(self):
        """Returns the maximum number of values to hold."""
        return self.__values.getMaxLen()

    # Event handler receives:
    # 1: Dataseries generating the event
    # 2: The datetime for the new value
    # 3: The new value
    def getNewValueEvent(self):
        return self.__newValueEvent

    def getValueAbsolute(self, pos):
        ret = None
        if pos >= 0 and pos < len(self.__values):
            ret = self.__values[pos]
        return ret

    def append(self, value):
        """Appends a value."""
        self.appendWithDateTime(None, value)

    def appendWithDateTime(self, dateTime, value):
        """
        Appends a value with an associated datetime.

        .. note::
            If dateTime is not None, it must be greater than the last one.
        """

        if dateTime is not None and len(self.__dateTimes) != 0 and self.__dateTimes[-1] >= dateTime:
            raise Exception("Invalid datetime. It must be bigger than that last one")

        assert(len(self.__values) == len(self.__dateTimes))
        self.__dateTimes.append(dateTime)
        self.__values.append(value)

        self.getNewValueEvent().emit(self, dateTime, value)

    def getDateTimes(self):
        return self.__dateTimes.data()
