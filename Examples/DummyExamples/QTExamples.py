from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
# from Package.FrontEnd.QTGraphs import QTLineGraph, QTLevelGraph
from Package.FrontEnd.factories import QTFactory
import numpy as np


def LineGraph(factory, spawning_pos: int):
    def update_(graph):
        DS = graph.get_data_container()
        RB = DS.get_RB()
        data = DS(x_Data=RB(size_max=100), y_Data=dict(channel_0=RB(size_max=100),
                                                       channel_1=RB(size_max=100)))
        data.x_Data.append(list(range(100)))
        for id_ in data.y_Data.keys():
            data.y_Data[id_].append(np.random.random(100))
        graph.updateFigure(data)

    line_graph_struct = GraphStructure(ID="Line Graph Test", grid=True,
                                       elements=dict(g1=ElementStructure(sensorID="channel_0", color="b", label="ch0"),
                                                     g2=ElementStructure(sensorID="channel_1", color="r", label="ch1")))
    g = factory.get_LineGraph(line_graph_struct, spawning_pos)
    g.set_onclicked_callback(lambda event: update_(g))
    return g


def LevelGraph(factory, spawning_pos: int):
    def update_(graph):
        DS = graph.get_data_container()
        graph.updateFigure(DS(x_Data=dict(g1=np.array(range(20)), g2=np.random.uniform(0, 4, 20)),
                              y_Data=dict(g1=np.random.random(20), g2=np.array(range(20)))))

    struct_scatter = GraphStructure(ID="Level Graph Test", grid=True,
                                    elements=dict(
                                        g1=ElementStructure(Y=np.array(range(20)), X=np.array([0] * 20),
                                                            color="r", label="g1"),
                                        g2=ElementStructure(X=np.array(range(20)), Y=np.array([1] * 20),
                                                            color="b", label="g2"))
                                    )
    g = factory.get_LevelGraph(struct_scatter, spawning_pos)
    g.set_onclicked_callback(lambda event: update_(g))
    return g


def VectorGraph(factory, spawning_pos: int):
    raise NotImplementedError


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    # Init global factory
    factory = QTFactory()
    qapp = QApplication(sys.argv)
    line_graph = LineGraph(factory, 1)
    lvl_graph = LevelGraph(factory, 2)
    line_graph.show()
    lvl_graph.show()
    qapp.exec_()
