import numpy as np

from Examples.generic_app import GENERICApp, AppConfig, GraphStructure, ElementStructure, graphConfig, QTFactory, \
    MPLFactory
from PyQt5.QtWidgets import QApplication
import sys

from Package.DataStructures.plotDataFormat import LineGraphData


def centre_data(data_: LineGraphData):
    for id_, data_pair in data_.Data.items():
        data_[id_][1] -= np.nanmean(data_pair[1])

if __name__ == '__main__':
    l1 = graphConfig(structure=GraphStructure(ID=f"Raw Line Graph Test 0", grid=True, blit=False,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=0, color="b", label="ch1"),
                                                  g2=ElementStructure(sensorID=1, color="g", label="ch2"),
                                                  # g3=ElementStructure(sensorID=10, color="k", label="ch10"),
                                                  # g4=ElementStructure(sensorID=11, color="r", label="ch11"),
                                              )
                                              ), factory=MPLFactory(), spawning_position=1, history=20000)
    l2 = graphConfig(structure=GraphStructure(ID="Raw Line Graph Test 1", grid=True, blit=True,
                                              elements=dict(
                                                  g1=ElementStructure(sensorID=2, color="b", label="ch3"),
                                                  g2=ElementStructure(sensorID=3, color="g", label="ch4"),
                                                  g3=ElementStructure(sensorID=4, color="k", label="ch5"),
                                                  # g4=ElementStructure(sensorID=15, color="r", label="ch15"),
                                              )
                                              ), factory=QTFactory(), spawning_position=2, history=20000)

    l3 = graphConfig(
        structure=GraphStructure(ID="Raw Line Graph Test 1", grid=True, blit=True,
                                 elements=dict(
                                     g1=ElementStructure(sensorID=5, color="b", label="ref2"), )
                                 ), factory=QTFactory(), spawning_position=3, history=20000)
    lvl1 = graphConfig(
        structure=GraphStructure(ID=f"Raw Level Graph Test {0}", grid=True, blit=False,  #
                                 elements=dict(
                                     g1=ElementStructure(X_init=np.array([0, 1]), Y_init=np.array([0] * 2),
                                                         sensorIDs=[0, 1],
                                                         color="b", label=f"real ch1-ch2"),
                                     g2=ElementStructure(X_init=np.array([2, 3, 4]), Y_init=np.array([0] * 3),
                                                         sensorIDs=[2, 3, 4],
                                                         color="r", label=f"real ch3-ch5"),
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
    pegelApp.add_line_graphs_task(centre_data)
    pegelApp.create_controlPanel("Pegel Viewer")
    pegelApp.create_from_config(conf)
    qapp.exec_()
