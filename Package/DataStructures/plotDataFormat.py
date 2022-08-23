from pydantic import BaseModel, validator, root_validator
from typing import List, Dict, Any, Optional, Iterable, Tuple, Type
from Package.DataStructures.RingBuffer import RingBuffer, RBEncoder
from numpy import ndarray
from threading import Lock


############# EXCEPTIONS DEFINITIONS ###########################
class plotDataException(Exception):
    """Base High level exception to notify user to errors in the data passed to the graph to update it"""

    def __init__(self, error, message: str):
        self.error = error
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error)


class DataShapeException(plotDataException):
    """High level exception raised when at least on array has a different shape than the others"""
    pass


class DataNotProvidedException(plotDataException):
    """High level exception raised when some data is missing at the validation stage"""
    pass


class UnorderedXDataException(plotDataException):
    """High level exception raised when the timeserie provided isn't in ascending ordered"""
    pass


class IndexOutOfRangeExeption(plotDataException):
    """High level exception raised when index provided to custom subscribable class is out of range"""


############# CLASS DEFINITIONS ###########################
# class CustomTuple(BaseModel):
#     """a custom tuple representing a pair of ID and value used to update a specific element in the graph"""
#     ID: str
#     DATA: RingBuffer
#
#     class Config:
#         arbitrary_types_allowed = True

LGDMap = {0: "x_Data", 1: "y_Data"}


class LineGraphData(BaseModel):
    """a custom object representing the data needed to update a line graph
     !!!LINE GRAPHS ASSUME ALL LINES SHARE THE SAME X AXIS DATA"""
    Data: Dict[int, Tuple[RingBuffer, RingBuffer]]
    @staticmethod
    def get_RB() -> Type[RingBuffer]:
        return RingBuffer

    # def __getitem__(self, item):
    #     try:
    #         assert item == "data"
    #         return getattr(self, LGDMap[item])
    #     except AssertionError:
    #         raise IndexOutOfRangeExeption(error=item, message="Index Muss be in {0}, however {1} provided".format(
    #             list(LGDMap.keys()), item))

    class Config:
        arbitrary_types_allowed = True

        json_encoders = {RingBuffer: RBEncoder}

    @root_validator(pre=True, skip_on_failure=True)
    def shape_validator(cls, attributes):
        """a validator to check the sanity in the data provided"""
        data = attributes.get("Data")
        if data is not None:
            for _, d in data.items():
                if d[0].size != d[1].size:
                    raise DataShapeException(error=d, message="a shape error in the data provided to update the plot")
            return attributes

    # @validator("data", pre=True)
    # def ascending_order_validator(cls, data):
    #     def is_ascending(data_):
    #         from numpy import nan
    #         for k in range(data_.size - 1):
    #             if k is not nan:
    #                 if (data_[k + 1] - data_[k]) < 0:
    #                     return False
    #         return True
    #
    #     if not is_ascending(data[0]):
    #         raise UnorderedXDataException(error=x_Data,
    #                                       message="x axe data is not in ascending order!")
    #
    #     return x_Data


VGDMap = {0: "x_Data", 1: "y_Data", 2: "u_Data", 3: "v_Data"}


class VectorGraphData(BaseModel):
    x_Data: ndarray
    y_Data: ndarray
    u_Data: ndarray
    v_Data: ndarray

    z_Data: Optional[ndarray]
    w_Data: Optional[ndarray]
    c_Data: Optional[ndarray]  # color data
    GraphID: Optional[str] = None
    slice_size: Optional[int] = 1

    def __getitem__(self, item) -> ndarray:
        try:
            assert item in VGDMap.keys()
            return getattr(self, VGDMap[item])
        except AssertionError:
            raise IndexOutOfRangeExeption(error=item, message="Index Muss be in {0}, however {1} provided".format(
                list(VGDMap.keys()), item))

        # if item == 0:
        #     return self.x_Data
        # if item == 1:
        #     return self.
        # return self.Fruits[item]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ndarray: RBEncoder}


SGDMap = {0: "x_Data", 1: "y_Data", 2: "z_Data"}


class LevelGraphData(BaseModel):
    x_Data: Dict[str, ndarray]
    y_Data: Dict[str, ndarray]
    z_Data: Optional[Dict[str, ndarray]]
    slice_size: Optional[int] = 1
    def __getitem__(self, item) -> Dict[str, ndarray]:
        try:
            assert item in SGDMap.keys()
            return getattr(self, SGDMap[item])
        except AssertionError:
            raise IndexOutOfRangeExeption(error=item, message="Index Muss be in {0}, however {1} provided".format(
                list(SGDMap.keys()), item))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ndarray: RBEncoder}


if __name__ == "__main__":
    import numpy as np
    import datetime, pathlib

    graph_data = LineGraphData(x_Data=RingBuffer(size_max=10, default_value=0.),
                               y_Data={str(id_): RingBuffer(size_max=10, default_value=1.) for id_ in range(3)})
    vector_data = VectorGraphData(x_Data=np.array(range(100)), y_Data=np.array(range(100)), z_Data=np.array(range(100)),
                                  u_Data=np.random.random(100), v_Data=np.random.random(100),
                                  w_Data=np.random.random(100))

    data = dict(line_data=graph_data, vector_data=vector_data)
    # print(graph_data)
    now = datetime.datetime.now()
    name = "\data__" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    path = "D:\HZDR\HZDR_VISU_TOOL\Package\Export_Test"
    pathlib.Path(path).mkdir(exist_ok=True)
    with open(path + name, "w") as f:
        j = graph_data.json()
        f.write(j)
        f.write("\n")
        data.json
        print(j)
        j = vector_data.json()
        f.write(j)
