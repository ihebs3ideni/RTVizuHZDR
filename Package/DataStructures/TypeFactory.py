from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.requestBody import ChannelData, Request, RequestStatus, RequestBody, RequestData, \
    RequestMetaData
from Package.DataStructures.plotDataFormat import LineGraphData, VectorGraphData
from Package.DataStructures.RingBuffer import RingBuffer

from abc import ABC, abstractmethod
from typing import Any, Dict, Type


class BaseTypeFactoryException(Exception):
    """Base High Level Exception for exceptions related to type generation"""

    def __init__(self, error, message: str):
        self.error = error
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error.__repr__())


class TypeNotSupportedException(BaseTypeFactoryException):
    """High level exception raised when the requested type is not supported"""
    pass


class BaseObjectFactory(ABC):
    """Base class for an object factory that returns custom data structure classes to create objectswithout importing every Module"""

    @abstractmethod
    def get_main_object(self) -> Type[Any]:
        """returns the main object for the specific tasks"""
        pass

    @abstractmethod
    def get_sub_objects(self) -> Dict[str, Type[Any]]:
        """returns a map of the sub objects needed to create the main class"""
        pass

    @abstractmethod
    def get_structure(self) -> str:
        """returns a representation on how the object should be structured"""
        pass


class GraphStructureFactory(BaseObjectFactory):
    def get_main_object(self) -> Type[GraphStructure]:
        """Graphstructure class taking the following arguments:
         elements: Dict[str, ElementStructure]
         xLim: Optional[Tuple[float, float]]
         yLim: Optional[Tuple[float, float]]
         grid: Optional[bool]
        updateIntervalMs: Optional[int]"""

        return GraphStructure

    def get_sub_objects(self) -> Type[ElementStructure]:
        """LineElementStructure class taking the following arguments:
         sensorID: str
         color: Optional[str]
         label: Optional[str]
         QuiverElementStructure class taking the following arguments:
         X: List[float]
         Y: List[float]
         Z: Optional[List[float]]
         """
        return ElementStructure

    def get_structure(self) -> str:
        return "GraphStructure: {elements: {element_id: ElementStructure=sub_obj, ..}, " \
               "optional(x_lim, y_lim, grid, updateIntervalMs) }"


class LinePlotDataFormatFactory(BaseObjectFactory):
    def get_main_object(self) -> Type[LineGraphData]:
        """LineGraphData class taking the following arguments:
         x_Data: RingBuffer
         y_Data: List[CustomTuple]"""
        return LineGraphData

    def get_sub_objects(self) -> Dict[str, Type[Any]]:
        """RingBuffer Class taking the following atguments:
                size_max : int
                default_value :  Optional[Any],
                dtype : Optional[Type]
                init_data: List[Any]"""
        return dict(RingBuffer=RingBuffer)

    def get_structure(self) -> str:
        return "LineGraphData(x_Data=RingBuffer(size_max=sm, optional(init_data=..), " \
               "y_Data={id_ : RingBuffer(size_max=sm, optional(init_data=..) for id_ in range(n_Graphs)])"


class VectorGraphDataFormatFactory(BaseObjectFactory):
    def get_main_object(self) -> Type[VectorGraphData]:
        """VectorGraphData class taking the following arguments:
         x_Data: RingBuffer
        y_Data: RingBuffer
        u_Data: RingBuffer
        v_Data: RingBuffer

        z_Data: Optional[RingBuffer]
        w_Data: Optional[RingBuffer]"""
        return VectorGraphData

    def get_sub_objects(self) -> Dict[str, Type[Any]]:
        """RingBuffer Class taking the following atguments:
                size_max : int
                default_value :  Optional[Any],
                dtype : Optional[Type]
                init_data: List[Any]"""
        return dict(RingBuffer=RingBuffer)

    def get_structure(self) -> str:
        return "LineGraphData(x_Data=RingBuffer(size_max=sm, optional(init_data=..), " \
               "y_Data=RingBuffer(size_max=sm, optional(init_data=..), u_Data=RingBuffer(size_max=sm, optional(" \
               "init_data=..), v_Data=RingBuffer(size_max=sm, optional(init_data=..),"



class TCPRequestObjectFactory(BaseObjectFactory):
    def get_main_object(self) -> Type[Request]:
        """Request class taking the following arguments:
         Status: RequestStatus
         Body: RequestBody"""
        return Request

    def get_sub_objects(self) -> Dict[str, Type[Any]]:
        """RequestStatus Class taking the following atguments:
                code : int
                message :  str
            RequestBody Class taking the following atguments:
                data : RequestData
                metaData :  RequestMetaData
            RequestData Class taking the following atguments:
                dataSize : int
                timesteps :  List[float]
                channels :  Dict[str, ChannelData]
            RequestMetaData Class taking the following atguments:
                comment : Optional[str]
                dataNature: Optional[str]
            ChannelData Class taking the following atguments:
                real : List[float]
                imag :  List[float]"""
        return dict(status=RequestStatus, body=RequestBody, data=RequestData, metadata=RequestMetaData,
                    channelData=ChannelData)

    def get_structure(self) -> str:
        return """{"Status": {"code": 100, "message": "No Errors"},
         "Body": {"metaData": {"comment": "This data is generated just for plot testing purposes",
                               "dataNature": "Mannually generated Data"},
                  "data": {
                      "dataSize": 10,
                      "timesteps": list(range(10)),
                      "channels": {
                          "channels_1": {"real": list(np.random.random(10)),
                                         "imag": list(np.random.random(10))},
                          "channels_2": {"real": list(np.random.random(10)),
                                         "imag": list(np.random.random(10))},
                          "channels_3": {"real": list(np.random.random(10)),
                                         "imag": list(np.random.random(10))},
                          "channels_4": {"real": list(np.random.random(10)),
                                         "imag": list(np.random.random(10))},
                          "channels_5": {"real": list(np.random.random(10)),
                                         "imag": list(np.random.random(10))},
                      }
                  }
                  }
         }"""


from dataclasses import dataclass


@dataclass
class TypeFactories:
    graphStructureFactory: Type[GraphStructureFactory] = GraphStructureFactory
    linePlotArgFormatFactory: Type[LinePlotDataFormatFactory] = LinePlotDataFormatFactory
    tcpRequestFormatFactory: Type[TCPRequestObjectFactory] = TCPRequestObjectFactory

    def getByName(self, name: str):
        typ = getattr(self, name, 0)
        if typ == 0:
            raise TypeNotSupportedException(error=name, message="The requested Type is not supported")
        return typ

    def get_supported_names(self):
        return vars(self)


if __name__ == "__main__":
    #### Graph structure Factory Basic Test
    gsFactory = GraphStructureFactory()
    main_type = gsFactory.get_main_object()
    sub_types = gsFactory.get_sub_objects()
    es = sub_types["ElementStructure"]
    graph_structure = main_type(elements=dict(l1=es(sensorID="ch1", color="r", label="channel 1"),
                                              l2=es(sensorID="ch2", color="b")),
                                xLim=100, yLim=(-1, 1), grid=True, updateIntervalMs=100)

    print(gsFactory.get_structure())
    print(graph_structure.__repr__())

    #### plotData format Factory Basic Test
    ldFFactory = LinePlotDataFormatFactory()
    main_type = ldFFactory.get_main_object()
    sub_types = ldFFactory.get_sub_objects()
    ringBuffer = sub_types["RingBuffer"]
    line_data_Structure = main_type(x_Data=ringBuffer(size_max=1),
                                    y_Data={str(id_): RingBuffer(size_max=1) for id_ in range(3)})
    print(ldFFactory.get_structure())
    print(line_data_Structure.__repr__())

    ### TypeFactories Basic Example
    TF = TypeFactories()
    print(TF.getByName("graphStructureFactory"))
    print(TF.get_supported_names())
