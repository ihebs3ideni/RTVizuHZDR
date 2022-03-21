# TODO @Iheb: add logging instead of printing
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.FrontEnd.MPLGraphs import MPLLineGraph, MPLLevelGraph, MPLVectorGraph
from matplotlib.backend_bases import MouseButton
from Package.FrontEnd.factories import MPLFactory

import numpy as np
from Package.HelperTools.utils import coinFlip



def LineGraph(factory, spawning_pos: int):
    def update_(graph: MPLLineGraph):
        try:
            DS = factory.get_LineGraph_DataStructure()  # or graph.get_data_container()
            RB = DS.get_RB()
            data = DS(x_Data=RB(size_max=100), y_Data=dict(channel_0=RB(size_max=100),
                                                           channel_1=RB(size_max=100)))
            data.x_Data.append(list(np.arange(100)))
            for id_ in data.y_Data.keys():
                data.y_Data[id_].append(np.random.random(100))
            graph.update_signal.emit(data)
        except Exception as e:
            print(e)

    line_graph_struct = GraphStructure(ID="Line Graph Test",
                                       elements=dict(g1=ElementStructure(sensorID="channel_0", color="b", label="ch0"),
                                                     g2=ElementStructure(sensorID="channel_1", color="r", label="ch1")))
    g = factory.get_LineGraph(line_graph_struct, spawning_pos)
    g.set_onclicked_callback(lambda event: update_(g))
    return g


def LevelGraph(factory, spawning_pos: int):
    def update_(graph: MPLLevelGraph):
        DS = MPLLevelGraph.get_data_container()  # or factory.get_LevelGraph_DataStructure()
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


def filter_(data):
    shape = data.u_Data.shape
    data.u_Data *= np.random.random(shape)
    data.v_Data *= np.random.random(shape)
    if coinFlip(0.1):
        import time
        print("sleeping..")
        time.sleep(5)
    if coinFlip(0.15):
        raise Exception("The coin has decided")


def VectorGraph(factory, spawning_pos: int):
    def update_(event, graph: MPLVectorGraph):
        if event.button == MouseButton.LEFT:
            DS = graph.get_data_container()  # or factory.get_VectorGraph_DataStructure() or MPLVectorGraph.get_data_container()
            X, Y = np.meshgrid(np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30))  # create grid
            graph.updateFigure(
                DS(x_Data=X, y_Data=Y, u_Data=np.random.random(X.shape), v_Data=np.random.random(Y.shape)))
        elif event.button == MouseButton.RIGHT:
            graph.toggle_lines()

    X, Y = np.meshgrid(np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30))
    struct_vector = GraphStructure(ID="Vector Graph Test", colorMap="jet", asynchronous=True,
                                   elements=dict(q1=ElementStructure(X=X, Y=Y), ), blit=True)

    g = factory.get_VectorGraph(struct_vector, spawning_pos)
    g.add_postProcess(filter_)
    g.set_onclicked_callback(lambda event: update_(event, g))

    return g


def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    # Init global factory
    factory = MPLFactory()

    qapp = QApplication(sys.argv)
    line_graph = LineGraph(factory, 1)
    lvl_graph = LevelGraph(factory, 2)
    vector_graph = VectorGraph(factory,3)
    line_graph.show()
    lvl_graph.show()
    vector_graph.show()
    qapp.exec_()


if __name__ == '__main__':
    main()
