import unittest, json
import logging

logging.basicConfig(format='%(asctime)s %(message)s')

from Package.FrontEnd.MPLGraphs import *
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from PyQt5.QtWidgets import QApplication
import sys


class TestGraphs(unittest.TestCase):
    def test_base_graph(self) -> None:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        struct = GraphStructure(ID="test Graph", blit=True, grid=False, xLim=(0., 10.), yLim=(-1., 1.),
                                elements=dict(g1=ElementStructure()))
        qapp = QApplication(sys.argv)
        bg = MPLBasedGraph(structure=struct, spawning_position=1)
        bg.create_canvas()

        logging.warning("Checking canvas type")
        self.assertEqual(type(bg.dynamic_canvas), FigureCanvas)
        logging.warning("Checking Arguments passed")

    def test_Line_Graphs(self) -> None:
        pass

    def test_Vector_Graphs(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
