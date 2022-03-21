from Package.FrontEnd.CustomizableControlPanel import BaseControlPanel
from Package.FrontEnd.factories import MPLFactory, QTFactory
from Package.FrontEnd.BaseInterface import BaseGraphCanvas
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.requestBody import Request
from Package.DataStructures.RingBuffer import RingBuffer
from Package.BackEnd.TCP_Client import AsyncTCP_Client, BaseTcpClient, QT_TCPClient
from Package.HelperTools.ExcThread import EventLoopThread
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
import json
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class PegelApp:
    refresh_rate: int
    groups: List[range]
    host: str
    port: int
    graph_list: List[BaseGraphCanvas] = None
    line_graphs_list: List[Tuple[BaseGraphCanvas, object]] = None
    client: BaseTcpClient = None

    timer: QTimer = QTimer()
    controlPanel: BaseControlPanel = None


    def connect_cb(self, *args):
        icon = self.controlPanel.icons.get("CONNECTION_STATUS")
        # print(self.controlPanel.icons)
        if icon is None:
            print("No Icon to update")
            return
        icon.update_Icon(r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\connected.png")

    def disconnect_cb(self, *arg):
        icon = self.controlPanel.icons.get("CONNECTION_STATUS")
        if icon is None:
            print("No Icon to update")
            return
        icon.update_Icon(r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\no_connection.png")

    def error_cb(self, *args):
        for e in args:
            print(f"Client Error: - {e}")


    def create_client(self):
        if self.client is None:
            self.client = QT_TCPClient(self.host, self.port)
            self.client.on_receive(self.received_callback)
            self.client.on_connect(self.connect_cb)
            self.client.on_disconnect(self.disconnect_cb)
            self.client.on_error(self.error_cb)
        self.client.create_connection()

    def close_connection(self, *args):
        if self.timer.isActive():
            self.controlPanel.push_buttons.get("REQUEST").click()

        if self.client is None:
            print("No connection to close")
            return
        self.client.close_connection()


    def received_callback(self, raw_data: bytes):
        """Callback triggered on data received by the connection class"""
        try:
            data = str(raw_data, encoding='ascii')
            request = Request.parse_obj(json.loads(data)[0])
            i = 0
            for g, d in self.line_graphs_list:
                d.x_Data.append(request.Body.data.timesteps[-1])
                for j in range(7):
                    sid = f"channel_{i}"
                    i+=1
                    if request.Body.data.channels.get(sid) is None:
                        print(f"This Sensor ID doesn't exist in the request Body: {sid}")
                    else:
                        d.y_Data[sid].append(request.Body.data.channels.get(sid).real)
                g.updateFigure(d)
                g.autoscale_trigger(False)
                g.show()

            for graph, grp in zip(self.graph_list, self.groups):

                r = np.array([request.Body.data.channels[f"channel_{i}"].real for i in grp])
                DS = graph.get_data_container()
                graph.updateFigure(DS(x_Data=dict(g1=np.array(range(len(r)))),
                                      y_Data=dict(g1=r)))
                g.autoscale_trigger(False)
                graph.show()

        except Exception as e:
            import traceback
            # print(e.obj)
            print(traceback.format_exc())

    def requesting_callback(self, *args):
        b = self.controlPanel.push_buttons.get("REQUEST")
        if self.timer.isActive():
            b.setText("Request")
            self.timer.stop()
            return
        b.setText("Stop")
        self.timer.start(self.refresh_rate)

    def create_lvl_graphs(self):
        self.graph_list = []

        factory = MPLFactory()
        # for i in range(n_graphs):
        structure = GraphStructure(ID=f"Pegel Viewer {0}", grid=True, #blit=True,
                                   elements=dict(g1=ElementStructure(X=np.array(range(7)), Y=np.array([0] * 7),
                                                                     color="b", label=f"real ch0-ch6"),
                                                 # g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                 #                     color="r", label=f"Imaginary ch0-ch3")
                                                 ), )
        self.graph_list.append(factory.get_LevelGraph(structure, spawning_position=1))
        structure = GraphStructure(ID=f"Pegel Viewer {1}", grid=True, #blit=True,
                                   elements=dict(g1=ElementStructure(X=np.array(range(7)), Y=np.array([0] * 7),
                                                                     color="b", label=f"real ch7-ch14"),
                                                 # g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                 #                     color="r", label=f"Imaginary ch4-ch7")
                                                                     ))
        self.graph_list.append(factory.get_LevelGraph(structure, spawning_position=2))

        # structure = GraphStructure(ID=f"Pegel Viewer {3}", grid=True, #blit=True,
        #                            elements=dict(g1=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
        #                                                              color="b", label=f"real ch8-ch11"),
        #                                          g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
        #                                                              color="r", label=f"Imaginary ch8-ch11")))
        # self.graph_list.append(factory.get_LevelGraph(structure, spawning_position=3))
        #
        # structure = GraphStructure(ID=f"Pegel Viewer {4}", grid=True, #blit=True,
        #                            elements=dict(g1=ElementStructure(X=np.array(range(3)), Y=np.array([0] * 3),
        #                                                              color="b", label=f"real ch12-ch14"),
        #                                          g2=ElementStructure(X=np.array(range(3)), Y=np.array([0] * 3),
        #                                                              color="r", label=f"Imaginary ch12-ch14")))
        # self.graph_list.append(factory.get_LevelGraph(structure, spawning_position=4))


    def create_line_graphs(self):
        self.line_graphs_list = []
        factory = QTFactory()
        line_graph_struct = GraphStructure(ID="Line Graph Test 0", grid=True, blit=True,
                                           elements=dict(
                                               g1=ElementStructure(sensorID="channel_0", color="b", label="ch0"),
                                               g2=ElementStructure(sensorID="channel_1", color="r", label="ch1"),
                                               g3=ElementStructure(sensorID="channel_2", color="r", label="ch2"),
                                               g4=ElementStructure(sensorID="channel_3", color="r", label="ch3"),
                                               g5=ElementStructure(sensorID="channel_4", color="r", label="ch4"),
                                               g6=ElementStructure(sensorID="channel_5", color="r", label="ch5"),
                                               g7=ElementStructure(sensorID="channel_6", color="r", label="ch6"),)
                                               # g7=ElementStructure(sensorID="channel_7", color="r", label="ch7")),

                                           )
        DS = factory.get_LineGraph_DataStructure()
        RB = DS.get_RB()
        data = DS(x_Data=RB(size_max=100), y_Data=dict(channel_0=RB(size_max=100),
                                                       channel_1=RB(size_max=100),
                                                       channel_2=RB(size_max=100),
                                                       channel_3=RB(size_max=100),
                                                       channel_4=RB(size_max=100),
                                                       channel_5=RB(size_max=100),
                                                       channel_6=RB(size_max=100),
                                                       ))
        self.line_graphs_list.append((factory.get_LineGraph(line_graph_struct, spawning_position=3), data))

        line_graph_struct = GraphStructure(ID="Line Graph Test 1", grid=True, blit=True,
                                           elements=dict(
                                               g1=ElementStructure(sensorID="channel_7", color="b", label="ch7"),
                                               g2=ElementStructure(sensorID="channel_8", color="r", label="ch8"),
                                               g3=ElementStructure(sensorID="channel_9", color="r", label="ch9"),
                                               g4=ElementStructure(sensorID="channel_10", color="r", label="ch10"),
                                               g5=ElementStructure(sensorID="channel_11", color="r", label="ch11"),
                                               g6=ElementStructure(sensorID="channel_12", color="r", label="ch12"),
                                               g7=ElementStructure(sensorID="channel_13", color="r", label="ch13"),)
                                               # g7=ElementStructure(sensorID="channel_7", color="r", label="ch7")),

                                           )
        DS = factory.get_LineGraph_DataStructure()
        RB = DS.get_RB()
        data = DS(x_Data=RB(size_max=100), y_Data=dict(channel_7=RB(size_max=100),
                                                       channel_8=RB(size_max=100),
                                                       channel_9=RB(size_max=100),
                                                       channel_10=RB(size_max=100),
                                                       channel_11=RB(size_max=100),
                                                       channel_12=RB(size_max=100),
                                                       channel_13=RB(size_max=100),
                                                       ))
        self.line_graphs_list.append((factory.get_LineGraph(line_graph_struct, spawning_position=4), data))


    def close_graphs(self, *args):
        for g in self.graph_list:
            g.close()

        for g in self.line_graphs_list:
            g[0].close()

    def take_screenshot(self, event, path=r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\screenshots"):
        if self.graph_list is None:
            print("No graphs to screenshot")
            return
        # print(self.graph_list)
        for i, g in enumerate(self.graph_list):
            g.take_screenshot(path=path, ID=i)
        for i, g in zip(range(2,4), self.line_graphs_list):
            g[0].take_screenshot(path=path, ID=i)

    def init_server(self, *args):
        if self.client is None:
            print("No Connection")
            return
        self.client.write("*IDN? demodulated")

    def request_data(self, *args):
        if self.client is None:
            print("No Connection")
        self.client.write(":DATA? demodulated 1")

    def create_controlPanel(self):
        self.timer.timeout.connect(self.request_data)
        self.controlPanel = BaseControlPanel("Pegel Viewer")
        self.controlPanel.on_close(self.close_graphs)
        self.controlPanel.on_close(self.close_connection)

        self.controlPanel.add_push_button("Connect", (0, 0), callback=self.create_client, UID="CONNECT")
        self.controlPanel.add_push_button("Init", (1, 0), callback=self.init_server, UID="INIT")
        request_b = self.controlPanel.add_push_button("Request", (2, 0), UID="REQUEST")
        request_b.clicked.connect(self.requesting_callback)

        disconnect_b = self.controlPanel.add_push_button("Disconnect", (3, 0), callback=self.close_connection,
                                                         UID="DISCONNECT")
        # disconnect_b.clicked.connect(lambda event: request_b.click())

        self.controlPanel.add_Icon("Connection", r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\no_connection.png",
                                   (0, 1, 3, 1), UID="CONNECTION_STATUS")
        self.controlPanel.add_push_button("Screenshot", (3, 1), self.take_screenshot, UID="SCREENSHOT")
        self.controlPanel.show()


if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    pegelApp = PegelApp(refresh_rate=500, groups=[range(7), range(7, 14)],
                        host="localhost", port=5400)
    pegelApp.create_controlPanel()
    pegelApp.create_lvl_graphs()
    pegelApp.create_line_graphs()
    qapp.exec_()