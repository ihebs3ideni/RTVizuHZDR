from abc import abstractmethod, ABC
from pydantic import BaseModel, ValidationError, validator, root_validator, dataclasses
from typing import List, Dict, Optional


class RequestException(Exception):
    """Base High level exception to notify user to errors in parsing the request"""

    def __init__(self, error, message: str):
        self.error = error
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error.__repr__())


class UnorderedTimeSerieException(RequestException):
    """High level exception raised when the time serie provided isn't in ascending ordered"""
    pass


class DataShapeException(RequestException):
    """High level exception raised when at least on array has a different shape than the others"""
    pass


class EmptyRequestException(RequestException):
    """High level exception raised when the request is empty"""
    pass


class RequestStatus(BaseModel):
    """Class representing the status field of the request"""
    code: int
    message: str


class ChannelData(BaseModel):
    """Class representing the basic channel data"""
    timestamp: List[float]
    real: List[float]
    imag: List[float]
    # data needed for vector graphs
    U: Optional[List[float]]
    V: Optional[List[float]]

    def get_by_name(self, member_name: str):
        return self.__dict__.get(member_name)


class RequestData(BaseModel):
    """Class representing the data in the request body"""
    channels: Dict[int, ChannelData]

    class Config:
        validation = False

    # @root_validator
    # @classmethod
    # def timesteps_check(cls, attributes) -> dict:
    #     """validator to make sure the time serie is in the right shape and in ascending order"""
    #     timesteps_ = attributes.get("timesteps")
    #     if not ([(timesteps_[k + 1] - timesteps_[k]) > 0 for k in range(len(timesteps_) - 1)].count(True) == len(
    #             timesteps_) - 1):
    #         raise UnorderedTimeSerieException(error=timesteps_,
    #                                           message="timesteps are not in ascending order!")
    #     if len(timesteps_) != attributes.get("dataSize"):
    #         DataShapeException(error=timesteps_,
    #                            message="timesteps have a different shape than %d" % attributes.get("dataSize"))
    #     return attributes
    #
    # @root_validator
    # @classmethod
    # def data_shape_check(cls, attributes) -> dict:
    #     """root validator to make sure all data sets have the same shape"""
    #     channels = attributes.get("channels")
    #     for id, c in channels.items():
    #         if len(c.real) != attributes.get("dataSize") or (len(c.imag) != attributes.get("dataSize") and len(c.imag)!=0):
    #             print(id)
    #             raise DataShapeException(error=c,
    #                                      message="Data set with id \"%s\" has a different size than the time serie" % id)
    #
    #     return attributes
    #
    # @validator("channels")
    # @classmethod
    # def non_empty_channels(cls, channels) -> dict:
    #     """validator to make sure channel data is not an empty set"""
    #     if not channels:
    #         raise EmptyRequestException(error=channels,
    #                                     message="The proessed request has no channel Data!")
    #     return channels


class RequestMetaData(BaseModel):
    """Class representing the data in the request body"""
    dataNature: str
    serialNumbers: List[int]
    comment: Optional[str]


class RequestBody(BaseModel):
    """Class representing the request body"""
    data: RequestData
    metaData: RequestMetaData


class Request(BaseModel):
    """Class representing the request body"""
    Status: RequestStatus
    Body: RequestBody


class InitResponse(BaseModel):
    SamplingFrequency: List[float]
    ChannelIDs: List[int]

if __name__ == "__main__":
    import json

    path = r"D:\HZDR\HZDR_VISU_TOOL\Package\Tests\Test_Requests.json"
    with open(path, "r") as test_file:
        test = json.load(test_file)
        data = test.get(r"wrongDatasize")
    r = Request.parse_obj(data)
    print(r)
