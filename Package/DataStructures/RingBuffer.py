import numpy as np
import threading
from dataclasses import dataclass
from typing import *
import json


class RingBuffer(object):
    def __init__(self, size_max, default_value=None, dtype=None, init_data: List[np.dtype] = None):
        """initialization"""
        self.__size_max = size_max
        self.__default_value = default_value

        self._data = np.empty(size_max, dtype=dtype)
        self._data.fill(default_value)
        self.size_ = 0
        if init_data is not None:
            for f in init_data:
                self.__append(f)

        self.lock = threading.Lock()

    def __append(self, value):
        self._data = np.roll(self._data, 1)
        self._data[0] = value
        if (self.size_ < self.__size_max):
            self.size_ += 1
        else:
            self.size_ = self.__size_max

    def append(self, value):
        """
        :param value:
        :return:

        """
        try:
            with self.lock:
                # put only the last elements of the provided array that can fill the buffer instead of unnecessary
                # rewriting
                if self.__size_max < len(value):
                    value = value[-self.__size_max-1: -1]
                self._data = np.roll(self._data, len(value))
                for v, j_ in zip(value, range(len(value) - 1, -1, -1)):
                    self._data[j_] = v
                if (self.size_ + len(value)) < self.__size_max:
                    self.size_ += len(value)
                else:
                    self.size_ = self.__size_max
        except TypeError:
            with self.lock:
                self.__append(value)

    def clear(self):
        self._data = np.empty(self.__size_max, dtype=None)
        self._data.fill(self.__default_value)

    def last(self):
        return self.data[0]

    def first(self):
        return self.data[-1]

    @property
    def data(self) -> np.ndarray:
        return self._data

    @property
    def rev(self) -> np.ndarray:
        return np.array(list(reversed(self._data)))

    @property
    def size(self) -> int:
        return self.size_

    def __getitem__(self, key):
        """get element"""
        return (self._data[key])

    def __repr__(self):
        """return string representation"""
        s = self._data.__repr__()
        s = s + '\t' + str(self.size) + "\t" + self.data[::-1].__repr__()

        return (s)


class RBEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        try:
            if isinstance(obj, RingBuffer):
                return obj.data.tolist()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return repr(obj)
        except TypeError:
            pass


if __name__ == "__main__":
    rb = RingBuffer(10)
    rb1 = RingBuffer(10)
    rb.append(list(range(10)))
    for i in range(10):
        rb1.append(i)
    print(rb.first(), rb.last())
    print(rb1.first(), rb1.last())
    # print(rb1)
    d = dict(r1=rb, r2=rb1)
    j = json.dumps(d, cls=RBEncoder)
    print(j)
