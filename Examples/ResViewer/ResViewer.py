import numpy as np

from Examples.generic_app import GENERICApp, AppConfig, GraphStructure, ElementStructure, graphConfig, QTFactory, MPLFactory
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    l1 = graphConfig(structure=GraphStructure(ID=f"Demodulated Line Graph Test 0", grid=True, blit=True,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=0, color="b", label="ch0"),
                                                  g2=ElementStructure(sensorID=1, color="g", label="ch1"),
                                                  g3=ElementStructure(sensorID=2, color="k", label="ch2"),
                                                  g4=ElementStructure(sensorID=3, color="r", label="ch3"),
                                                  g5=ElementStructure(sensorID=4, color="c", label="ch4"),
                                                  g6=ElementStructure(sensorID=5, color="m", label="ch5"),
                                                  g7=ElementStructure(sensorID=6, color="k", label="ch6"), )
                                              ), factory=MPLFactory(), spawning_position=1, history=500)
    l2 = graphConfig(structure=GraphStructure(ID="Demodulated Line Graph Test 1", grid=True, blit=True,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=7, color="b", label="ch7"),
                                                  g2=ElementStructure(sensorID=8, color="g", label="ch8"),
                                                  g3=ElementStructure(sensorID=9, color="k", label="ch9"),
                                                  g4=ElementStructure(sensorID=10, color="r", label="ch10"),
                                                  g5=ElementStructure(sensorID=11, color="c", label="ch11"),
                                                  g6=ElementStructure(sensorID=12, color="m", label="ch12"),
                                                  g7=ElementStructure(sensorID=13, color="k", label="ch13"), )
                                              ), factory=QTFactory(), spawning_position=2, history=500)
    lvl1 = graphConfig(
        structure=GraphStructure(ID=f"Demodulated Level Graph Test {0}", grid=True, blit=True,  # with_lines=False,
                                 elements=dict(
                                     g1=ElementStructure(X_init=np.array(range(7)), Y_init=np.array([0] * 7),
                                                         sensorIDs=list(range(7)),
                                                         color="b", label=f"real ch0-ch6"),
                                     g2=ElementStructure(X_init=np.array(range(7)), Y_init=np.array([0] * 7),
                                                         sensorIDs=list(range(7, 14)),
                                                         color="r", label=f"real ch7-ch14"),
                                 ), ), factory=MPLFactory(), spawning_position=3, x_axis_id="range",
        y_axis_id="real")
    lvl2 = graphConfig(
        structure=GraphStructure(ID=f"Demodulated Level Graph Test {1}", grid=True, blit=True,  # with_lines=False,
                                 elements=dict(
                                     g1=ElementStructure(X_init=np.array(range(7)), Y_init=np.array([0] * 7),
                                                         sensorIDs=list(range(7)),
                                                         color="b", label=f"imag ch0-ch6"),
                                     g2=ElementStructure(X_init=np.array(range(7)), Y_init=np.array([0] * 7),
                                                         sensorIDs=list(range(7, 14)),
                                                         color="r", label=f"imag ch7-ch14"),
                                 ), ), factory=QTFactory(), spawning_position=4, x_axis_id="imag",
        y_axis_id="range")

    conf = AppConfig(LineGraphs=[l1, l2], LevelGraphs=[lvl1, lvl2])

    qapp = QApplication(sys.argv)
    resApp = GENERICApp(refresh_rate=500, groups=[range(7), range(7, 14)],
                        host="localhost", port=5400, request_processed=True, reference_ids=[15], slice_size=1)
    resApp.create_controlPanel("Result Viewer")
    resApp.create_from_config(conf)

    # resApp.create_lvl_graphs("demodulated")
    # resApp.create_line_graphs("demodulated")
    qapp.exec_()
