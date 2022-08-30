from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.FrontEnd.MayaviGraphs import MayaviDynamicGraph
from Package.FrontEnd.factories import MayaviFactory

import numpy as np
from Package.HelperTools.utils import coinFlip

factory = None



def LineGraph(factory, spawning_pos: int):
    raise NotImplementedError


def LevelGraph(factory, spawning_pos: int):
    raise NotImplementedError


def filter_(data):
    # shape = data.u_Data.shape
    data.u_Data *= np.random.uniform(-2, 2, data.u_Data.shape)
    data.v_Data *= np.random.uniform(-2, 2, data.v_Data.shape)
    data.w_Data *= np.random.uniform(-2, 2, data.w_Data.shape)

    # if coinFlip(0.4):
    #     import time
    #     print("sleeping..")
    #     time.sleep(0.5)
    # if coinFlip(0.15):
    #     raise Exception("The coin has decided")


def VectorGraph(factory, spawning_pos: int, c=""):
    def update_(graph: MayaviDynamicGraph):
        DS = factory.get_VectorGraph_DataStructure()
        X, Y, Z = np.mgrid[-10:10, -10:10, -4:4]
        graph.updateFigure(
            DS(x_Data=X, y_Data=Y, z_Data=Z,
               u_Data=np.random.random(X.shape),
               v_Data=np.random.random(Y.shape),
               w_Data=np.random.random(Z.shape)))

    x, y, z = np.mgrid[-10:10, -10:10, -4:4]  # create grid
    structure = GraphStructure(ID=f"Test Mayavi Dynamic graph {c}", blit=True, grid=True, yLim=(1, -1),
                               elements=dict(g1=ElementStructure(X_init=x, Y_init=y, Z_init=z, hasGrid=True,
                                                                 hasStreamLines=True, hasVectorField=True,
                                                                 hasCutPlane=True,
                                                                 )))
    g = factory.get_VectorGraph(structure, spawning_pos)
    g.add_postProcess(filter_)
    g.set_onclicked_callback(lambda event: update_(g))
    return g


def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    # init global factory
    global factory
    factory = MayaviFactory()

    qapp = QApplication(sys.argv)
    vector_graph = VectorGraph(factory, 1, "1")
    vector_graph2 = VectorGraph(factory, 2, "2")
    vector_graph.show()
    vector_graph2.show()
    qapp.exec_()


if __name__ == '__main__':
    main()
