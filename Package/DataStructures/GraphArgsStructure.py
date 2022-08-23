from pydantic import BaseModel, ValidationError, validator, root_validator, dataclasses
from typing import List, Dict, Optional, Tuple, Any, Mapping
from numpy import ndarray
from pydantic.color import Color

SUPPORTED_COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']


# SUPPORTED_GRAPH_TYPES = ['line', 'scatter', 'quiver', 'bar']


class GraphConfigStructureException(Exception):
    """Base High level exception for errors in the graph configs"""

    def __init__(self, error, message: str):
        self.error = error
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error.__repr__())


class ColorNotSupportedException(GraphConfigStructureException):
    """High level exception raised when the color specified is not supported"""
    pass


class ColorNotProvidedException(GraphConfigStructureException):
    """High level exception raised when the color is not specified"""
    pass


class LabelNotProvidedException(GraphConfigStructureException):
    """High level exception raised when the label is not specified"""
    pass


class DuplicatedSensorIdException(GraphConfigStructureException):
    """High level exception raised when two graph elements are responsible for the same sensor"""
    pass


class QuiverDensityOutOfRange(GraphConfigStructureException):
    """High level exception raised when the density provided for the quiver Graph is out of range"""
    pass


# class GraphTypeNotSupportedException(GraphConfigStructureException):
#     """High level exception raised when the graph type specified is not supported"""
#     pass

class ElementStructure(BaseModel):
    color: Optional[str] = "k"
    label: Optional[str]
    """For quiver or Scatter Graphs"""
    zorder: Optional[int] = 1
    scale: Optional[float] = 3
    units: Optional[str] = 'xy'
    density: Optional[float] = 0.5
    X_init: Optional[ndarray]  # S/Q
    Y_init: Optional[ndarray]  # S/Q
    Z_init: Optional[ndarray]  # S/Q
    sensorIDs: Optional[List[int]]
    """For line Graphs"""
    sensorID: Optional[int]
    """for mayavi Graphs"""
    hasVectorField: Optional[bool] = False
    hasGrid: Optional[bool] = False
    hasStreamLines: Optional[bool] = False
    hasCutPlane: Optional[bool] = False

    class Config:
        arbitrary_types_allowed = True

    @validator("density")
    def check_density(cls, density):
        if density in [0, 1]:
            return density
        raise QuiverDensityOutOfRange(error=density, message="The provided Density needs to be in [0,1]")

    # @root_validator()
    # def check_Quiver(cls, attributes):
    #     return attributes

    # @root_validator(pre=True)
    # def check_args(cls, attributes):
    #     print("color= ", attributes.get("color"))
    #     print("label= ", attributes.get("label"))
    #     if attributes.get("color") is None:
    #         raise ColorNotProvidedException(error=None, message="There is no color specified for the line corresponding to SensorID: $s"%attributes.get("sensorID"))
    #     if attributes.get("label") is None:
    #         raise LabelNotProvidedException(error=None,
    #                                         message="There is no Label specified for the line corresponding to SensorID: $s" % attributes.get(
    #                                             "sensorID"))
    #     return attributes
    # @validator("color")
    # @classmethod
    # def color_supported(cls, color):
    #     # print("color= ", color)
    #     if color is None:
    #         if color not in SUPPORTED_COLORS:
    #             raise ColorNotSupportedException(error=color, message="Only the Following colors are supported %s" % str(
    #                 SUPPORTED_COLORS))
    #     return color or "r"
    #


#     @validator("label")
#     @classmethod
#     def label_provided(cls, label):
#         # print("label= ", label)
#         if label is None:
#             raise LabelNotProvidedException(error=label, message="There is no color specified")
#         return label or " "
# #
#
import numpy as np


class GraphStructure(BaseModel):
    elements: Dict[str, ElementStructure]
    xLim: Optional[Tuple[float, float]]
    yLim: Optional[Tuple[float, float]]
    grid: Optional[bool]

    # updateIntervalMs: Optional[int]  # only needed when using the built in timer to drive the plot update
    blit: Optional[
        bool]  # a flag to control wheather the graph uses blitting or not (only needed for Matplotlib based graphs)
    ID: Optional[str] = ""  # an optional ID to keep track of graphs from within
    colorMap: Optional[str] = "jet"  # relevant for quivers
    with_lines: Optional[bool] = True  # relevant for level plots

    # relevant for postprocessing before plotting to avoid blocking the eventloop.
    # !!! IN CASE NEEDED USE FOR ALL WINDOWS BECAUSE THEY SHARE THE SAME EVENTLOOP
    asynchronous: Optional[bool] = False

    @validator("blit")
    def checkBlit(cls, blit):
        if blit is None:
            return False
        return blit

    @validator("xLim")
    def checkXLim(cls, xlim):
        if xlim is None:
            return (0, 100)
        return xlim

    @validator("yLim")
    def checkYLim(cls, ylim):
        if ylim is None:
            return (-1.2, 1.2)
        return ylim

    # @root_validator
    # @classmethod
    # def check_unique_ids(cls, attributes):
    #
    #     def all_unique(x: List):
    #         return len(x) == np.unique(x).size
    #
    #     elements = attributes.get("elements")
    #     if elements is not None:
    #         ids = [e.sensorID for _, e in elements.items()]
    #         if not all_unique(ids):
    #             raise DuplicatedSensorIdException(ids, message="Some IDs are duplicated")
    #     return attributes

    def get_SensorIds(self) -> List[int]:
        return [e.sensorID for _, e in self.elements.items()]


if __name__ == "__main__":
    import mayavi2

    # import time
    # a = "A B C D E F G A G F H S J A A A B C D E F G A G F H S J A A, A B C D E F G A G F H S J A A A B C D E F G A G F H S J A A A B C D E F G A G F H S J A A A B C D E F G A G F H S J A A A B C D E F G A G F H S J A A"
    # a = a.split()
    # start = time.time_ns()
    # len(a) == len(set(a))
    # print("duration = ", time.time_ns()-start)
    # start = time.time_ns()
    # len(a) == np.unique(a).size
    # print("duration = ", time.time_ns() - start)
    # print(ElementStructure(sensorID="channel 1", color="b", label="test"))
    #
    # gs = GraphStructure(elements=dict(line_1=ElementStructure(sensorID="channel_1", color="r", label="this is a test"),
    #                                   line_2=ElementStructure(sensorID="channel_2", color="r", label="this is a test")))
    # print(gs)
