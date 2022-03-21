from Package.FrontEnd.BaseInterface import BaseFactory, BaseGraphException
from Package.FrontEnd.MPLGraphs import MPLLineGraph, MPLVectorGraph, MPLLevelGraph
from Package.FrontEnd.QTGraphs import QTLineGraph, QTLevelGraph
from Package.FrontEnd.MayaviGraphs import MayaviDynamicGraph

from Package.DataStructures.GraphArgsStructure import GraphStructure

# TODO: linegraph-> lineovertime, Lvlgraph -> lineOverSpace
class LibraryDoesntSupportException(BaseGraphException):
    """Base High level exception to be raised when requested Graph type isn't supported by the requested Library"""
    pass


class MPLFactory(BaseFactory):
    def get_LineGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return MPLLineGraph(setup, spawning_position)

    def get_LineGraph_DataStructure(self):
        return MPLLineGraph.get_data_container()

    def get_LevelGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return MPLLevelGraph(setup, spawning_position)

    def get_LevelGraph_DataStructure(self):
        return MPLLevelGraph.get_data_container()

    def get_VectorGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return MPLVectorGraph(setup, spawning_position)

    def get_VectorGraph_DataStructure(self):
        return MPLVectorGraph.get_data_container()




class QTFactory(BaseFactory):
    def get_LineGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return QTLineGraph(setup, spawning_position)

    def get_LineGraph_DataStructure(self):
        return QTLineGraph.get_data_container()

    def get_LevelGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return QTLevelGraph(setup, spawning_position)

    def get_LevelGraph_DataStructure(self):
        return QTLevelGraph.get_data_container()

    def get_VectorGraph(self, setup: GraphStructure, spawning_position: int = 1):
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Pyqtgraphs doesn't support vector graphs")

    def get_VectorGraph_DataStructure(self):
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Pyqtgraphs doesn't support vector graphs")


class MayaviFactory(BaseFactory):
    def get_LineGraph(self, setup: GraphStructure, spawning_position: int = 1):
        # TODO: @iheb: see if you should implement surface graphs
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Mayavi graphs doesn't support line graphs")

    def get_LineGraph_DataStructure(self):
        # TODO: @iheb: see if you should implement surface graphs
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Mayavi graphs doesn't support line graphs")

    def get_LevelGraph(self, setup: GraphStructure, spawning_position: int = 1):
        # TODO: @iheb: see if you should implement surface/scatter graphs
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Mayavi graphs doesn't support Level graphs")

    def get_LevelGraph_DataStructure(self):
        # TODO: @iheb: see if you should implement surface/scatter graphs
        raise LibraryDoesntSupportException(ID="None", obj=None, message="Mayavi graphs doesn't support Level graphs")

    def get_VectorGraph(self, setup: GraphStructure, spawning_position: int = 1):
        return MayaviDynamicGraph(setup, spawning_position)

    def get_VectorGraph_DataStructure(self):
        return MayaviDynamicGraph.get_data_container()
