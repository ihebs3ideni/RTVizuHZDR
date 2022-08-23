from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
# from Package.FrontEnd.QTGraphs import QTLineGraph, QTLevelGraph
from Package.FrontEnd.factories import QTFactory
import numpy as np


def LineGraph(factory, spawning_pos: int):
    DS = factory.get_LineGraph_DataStructure()
    RB = DS.get_RB()
    data = DS(Data=dict(channel_0=(RB(size_max=300), RB(size_max=300)),
                        channel_1=(RB(size_max=300), RB(size_max=300))))
    def update_(graph):
        for id_, dpair in data.Data.items():
            size = np.random.randint(80, 120, 1)[0]
            dpair[1].append(np.random.random(size))
            last_x = 0
            if not np.isnan(dpair[0].data[0]):
                last_x = dpair[0].data[0]
            dpair[0].append(list(np.arange(last_x, last_x + size)))
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
                                        g1=ElementStructure(Y_init=np.array(range(20)), X_init=np.array([0] * 20),
                                                            color="r", label="g1"),
                                        g2=ElementStructure(X_init=np.array(range(20)), Y_init=np.array([1] * 20),
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
