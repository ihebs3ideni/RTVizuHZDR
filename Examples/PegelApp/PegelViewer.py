import numpy as np

from Examples.generic_app import GENERICApp, AppConfig, GraphStructure, ElementStructure, graphConfig, QTFactory, MPLFactory
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    l1 = graphConfig(structure=GraphStructure(ID=f"Raw Line Graph Test 0", grid=True, blit=False,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=8, color="b", label="ch8"),
                                                  g2=ElementStructure(sensorID=9, color="g", label="ch9"),
                                                  g3=ElementStructure(sensorID=10, color="k", label="ch10"),
                                                  g4=ElementStructure(sensorID=11, color="r", label="ch11"),
                                              )
                                              ), factory=MPLFactory(), spawning_position=1, history=5000)
    l2 = graphConfig(structure=GraphStructure(ID="Raw Line Graph Test 1", grid=True, blit=True,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=12, color="b", label="ch12"),
                                                  g2=ElementStructure(sensorID=13, color="g", label="ch13"),
                                                  g3=ElementStructure(sensorID=14, color="k", label="ch14"),
                                                  g4=ElementStructure(sensorID=15, color="r", label="ch15"), )
                                              ), factory=QTFactory(), spawning_position=2, history=5000)

    l3 = graphConfig(
        structure=GraphStructure(ID="Raw Line Graph Test 1", grid=True, blit=True,
                                 elements=dict(
                                     g1=ElementStructure(sensorID=1, color="b", label="ref2"), )
                                 ), factory=QTFactory(), spawning_position=3, history=5000)
    lvl1 = graphConfig(
        structure=GraphStructure(ID=f"Raw Level Graph Test {0}", grid=True, blit=False,  #
                                 elements=dict(
                                     g1=ElementStructure(X_init=np.array([8, 9, 10, 11]), Y_init=np.array([0] * 4),
                                                         sensorIDs=[8, 9, 10, 11],
                                                         color="b", label=f"real ch0-ch6"),
                                     g2=ElementStructure(X_init=np.array([12, 13, 14, 15]), Y_init=np.array([0] * 4),
                                                         sensorIDs=[12, 13, 14, 15],
                                                         color="r", label=f"real ch7-ch14"),
                                 ), ), factory=MPLFactory(), spawning_position=4, x_axis_id="range",
        y_axis_id="real")
    # lvl2 = graphConfig(
    #     structure=GraphStructure(ID=f"Raw Level Graph Test {1}", grid=True,with_lines=False,
    #                              elements=dict(
    #                                  g1=ElementStructure(X_init=np.array([1,2,3,4]), Y_init=np.array([0] * 4),
    #                                                      sensorIDs= [1,2,3,4],
    #                                                      color="b", label=f"imag ch0-ch6"),
    #                                  g2=ElementStructure(X_init=np.array([5,6,7,8]), Y_init=np.array([0] * 4),
    #                                                      sensorIDs=[5,6,7,8],
    #                                                      color="r", label=f"imag ch7-ch14"),
    #                              ), ), factory=MPLFactory(), spawning_position=4, x_axis_id="range",
    #     y_axis_id="imag")

    conf = AppConfig(LineGraphs=[l1, l2, l3], LevelGraphs=[lvl1])
    qapp = QApplication(sys.argv)
    pegelApp = GENERICApp(refresh_rate=1000,
                          host="localhost", port=5400, request_processed=False, slice_size=1)
    pegelApp.create_controlPanel("Pegel Viewer")
    pegelApp.create_from_config(conf)
    qapp.exec_()