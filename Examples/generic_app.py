from Package.FrontEnd.CustomizableControlPanel import BaseControlPanel
from Package.FrontEnd.factories import MPLFactory, QTFactory, BaseFactory
from Package.FrontEnd.BaseInterface import BaseGraphCanvas
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.requestBody import Request, InitResponse
from Package.BackEnd.TCP_Client import BaseTcpClient, QT_TCPClient
import numpy as np

from PyQt5.QtCore import QTimer

import json
from typing import List, Tuple, Any, Optional, Dict
from dataclasses import dataclass
from enum import Enum
from Package.HelperTools.json_check import is_json
from Package.HelperTools.RequestParser import RequestParser, LineGraphParser, LevelGraphParser, VectorGraphParser
from queue import Queue

INIT_CMD = "*IDN?"
GET_CMD = ":DATA?"
BYE_CMD = "end."


@dataclass
class graphConfig:
    structure: GraphStructure
    factory: BaseFactory
    spawning_position: int
    x_axis_id: str = "timestamp"
    y_axis_id: str = "real"
    z_axis_id: Optional[str] = None
    history: Optional[int] = 5000


@dataclass
class AppConfig:
    LevelGraphs: List[graphConfig] = None  # dict(graphs: [GraphStructure,..], factory: BaseFactory, spawning_position)
    LineGraphs: List[graphConfig] = None  # dict(graphs: [GraphStructure,..], factory: BaseFactory...)
    VectorGraphs: List[graphConfig] = None  # dict(graphs: [GraphStructure,..], factory: BaseFactory...)


def click_callback(graph):
    print(f"graph {graph} clicked\n")
    graph.autoscale_trigger(not graph.autoscale_flag)
    # for list_ in [self.line_graphs_list, self.level_graph_list, self.vector_graph_list]:
    #     if list_:
    #         for g in list_:
    #             g.autoscale_trigger(not g.autoscale_flag)


@dataclass
class GENERICApp:
    refresh_rate: int
    host: str
    port: int
    slice_size: int
    request_processed: bool
    reference_ids: Optional[List[int]] = None  # only when request_processed = true
    level_graph_list: List[BaseGraphCanvas] = None
    level_graph_parsers: List[LevelGraphParser] = None
    vector_graph_list: List[BaseGraphCanvas] = None
    vector_graph_parsers: List[VectorGraphParser] = None
    line_graphs_list: List[BaseGraphCanvas] = None
    line_graph_parsers: List[LineGraphParser] = None
    client: BaseTcpClient = None
    sample_size: int = None
    request_timer: QTimer = QTimer()
    init_timer: QTimer = QTimer()
    controlPanel: BaseControlPanel = None
    current_cmd = INIT_CMD
    cmds_queue: Queue = Queue()
    data_type: str = "-raw"
    max_sample_request = 1
    paused_: bool = False

    def create_from_config(self, config: AppConfig):
        # create_line graphs and their parsers
        if config.LineGraphs:
            self.line_graphs_list = []  # overwrite class member
            self.line_graph_parsers = []
            for line_graph_config in config.LineGraphs:
                if self.max_sample_request < line_graph_config.history:
                    self.max_sample_request = line_graph_config.history
                factory = line_graph_config.factory
                if factory is None:
                    factory = QTFactory()
                struct = line_graph_config.structure
                g = factory.get_LineGraph(struct, spawning_position=line_graph_config.spawning_position)
                g.set_onclicked_callback(lambda event, graph_=g: click_callback(graph_))
                self.line_graphs_list.append(g)
                self.line_graph_parsers.append(LineGraphParser(graph_structure=struct, factory_=factory,
                                                               Buffer_size_=line_graph_config.history,
                                                               x_axis_id=line_graph_config.x_axis_id,
                                                               y_axis_id=line_graph_config.y_axis_id))
                # self.line_graphs_list[-1].set_onclicked_callback(lambda event: self.click_callback(self.line_graphs_list[-1]))
        if config.LevelGraphs:
            self.level_graph_list = []
            self.level_graph_parsers = []
            for lvl_graph_config in config.LevelGraphs:
                factory = lvl_graph_config.factory
                if factory is None:
                    factory = QTFactory()
                struct = lvl_graph_config.structure
                g = factory.get_LevelGraph(struct, spawning_position=lvl_graph_config.spawning_position)
                g.set_onclicked_callback(lambda event, graph_=g: click_callback(graph_))
                self.level_graph_list.append(g)
                self.level_graph_parsers.append(
                    LevelGraphParser(graph_structure=struct, factory_=factory, x_axis_id=lvl_graph_config.x_axis_id,
                                     y_axis_id=lvl_graph_config.y_axis_id))
                # self.level_graph_list[-1].set_onclicked_callback(lambda event: self.click_callback(self.level_graph_list[-1]))

        if config.VectorGraphs:
            self.vector_graph_list = []
            self.vector_graph_parsers = []
            for vector_graph_config in config.VectorGraphs:
                factory = vector_graph_config.factory
                if factory is None:
                    factory = MPLFactory()
                struct = vector_graph_config.structure
                g = factory.get_VectorGraph(struct, spawning_position=vector_graph_config.spawning_position)
                g.set_onclicked_callback(lambda event, graph_=g: click_callback(graph_))
                self.vector_graph_list.append(g)
                self.vector_graph_parsers.append(
                    VectorGraphParser(graph_structure=struct, factory_=factory, x_axis_id=vector_graph_config.x_axis_id,
                                      y_axis_id=vector_graph_config.y_axis_id, z_axis_id=vector_graph_config.z_axis_id))
                # self.vector_graph_list[-1].set_onclicked_callback(lambda event: self.click_callback(self.vector_graph_list[-1]))

    def connect_cb(self, *args):
        if self.request_processed:
            if self.reference_ids is None:
                print("REFERENCE ID NEEDS TO BE PROVIDED AT INITIALISATION IF PROCESSED DATA IS REQUESTED\n")
                return
            self.data_type = "-p " + "".join([str(ref_id) for ref_id in self.reference_ids])
        else:
            self.data_type = "-raw"
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
        if self.request_timer.isActive():
            self.controlPanel.push_buttons.get("REQUEST").click()

        if self.client is None:
            print("No connection to close")
            return
        # self.current_cmd = BYE_CMD

        # self.client.write(BYE_CMD)
        # self.cmds_queue.put_nowait(BYE_CMD)
        self.client.close_connection()

    def received_callback(self, raw_data: bytes):  # use app config to parse data
        """Callback triggered on data received by the connection class"""
        try:
            data = str(raw_data, encoding='ascii')
            cmd = self.cmds_queue.get(
                block=False)  # if the callback is called then a cmd already exists in the FIFO Queue
            # print("latest cmd: ", cmd)
            self.client.is_free = False
            if is_json(data):  # only handle json if its a json format
                request = Request.parse_obj(json.loads(data))
                if self.line_graphs_list:
                    for p, g in zip(self.line_graph_parsers, self.line_graphs_list):
                        # print("sample size: ", self.sample_size)
                        p(request)
                        if not self.paused_:
                            g.updateFigure(p.data)
                            if not g.isVisible():
                                g.show()
                if self.level_graph_list:
                    for p, g in zip(self.level_graph_parsers, self.level_graph_list):
                        p(request)
                        if not self.paused_:
                            g.updateFigure(p.data)
                            if not g.isVisible():
                                g.show()
                if self.vector_graph_list:
                    for p, g in zip(self.vector_graph_parsers, self.vector_graph_list):
                        p(request)
                        if not self.paused_:
                            g.updateFigure(p.data)
                            if not g.isVisible():
                                g.show()

            else:
                # cmd == INIT_CMD:
                d = data.split()
                try:
                    freq_begin = d.index("Frequency:") + 1
                    freq_end = d.index("Hz")
                    id_begin = d.index("Channels:") + 1
                    # raw_Res = dict(SamplingFrequency= d[d.])
                    res = InitResponse(SamplingFrequency=list(float(f) for f in d[freq_begin:freq_end]),
                                       ChannelIDs=list(int(id_) for id_ in d[
                                                                           id_begin:]), )  # can be handy for more complicated applications
                    ratio = round(self.refresh_rate / 1000)
                    self.sample_size = max(ratio, ratio * round(min(res.SamplingFrequency)))
                    # self.sample_size = min(self.sample_size, self.max_sample_request)
                    if (self.sample_size / self.slice_size) > self.max_sample_request:
                        raise Exception(
                            f"Requested sample size is greater than the buffer size: {self.sample_size / self.slice_size} > {self.max_sample_request}")
                    print(f"INIT RESPONSE LOOKS LIKE THIS: {res}")
                    print(f"NEW SAMPLE RATE: {self.sample_size}")
                except Exception as e:
                    print(f"UNKNOWN RESPONSE FORMAT: {data}")
                # list(map(int, "42 0".split()))
            # elif cmd == BYE_CMD:
            #     print(f"BYE RESPONSE LOOKS LIKE THIS: {data}")
            # else:
            #     print(f"UNKNOWN RESPONSE FORMAT: {len(data)}")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
        self.client.is_free = True

    def requesting_callback(self, *args):
        b = self.controlPanel.push_buttons.get("REQUEST")
        if self.request_timer.isActive():
            b.setText("Request")
            self.request_timer.stop()
            self.init_timer.stop()
            return
        b.setText("Stop")
        self.request_timer.start(self.refresh_rate)
        self.init_timer.start(10000)

    def clear_callbacks(self, *args):
        if self.line_graphs_list:
            for g, p in zip(self.line_graphs_list, self.line_graph_parsers):
                g.clearPlot()
                p.clear_buffer(np.nan)
        if self.level_graph_list:
            for g in self.level_graph_list:
                g.clearPlot()
        if self.vector_graph_list:
            for g in self.vector_graph_list:
                g.clearPlot()

    def pausing_callback(self, *args):
        b = self.controlPanel.push_buttons.get("PAUSE")
        if self.paused_ and b:
            b.setText("Pause")
        else:
            b.setText("Play")
        self.paused_ = not self.paused_

    def close_graphs(self, *args):
        if self.level_graph_list:
            for g in self.level_graph_list:
                g.close()
        if self.line_graphs_list:
            for g in self.line_graphs_list:
                g.close()
        if self.vector_graph_list:
            for g in self.vector_graph_list:
                g.close()

    def take_screenshot(self, event, path=r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\screenshots"):
        if self.level_graph_list is None:
            print("No graphs to screenshot")
            return
        # print(self.graph_list)
        if self.level_graph_list:
            for i, g in enumerate(self.level_graph_list):
                g.take_screenshot(path=path, ID=i)
        if self.line_graphs_list:
            for i, g in zip(range(2, 4), self.line_graphs_list):
                g[0].take_screenshot(path=path, ID=i)
        if self.vector_graph_list:
            for i, g in enumerate(self.vector_graph_list):
                g.take_screenshot(path=path, ID=i)

    def init_server(self, *args):
        if self.client is None:
            print("No Connection")
            return
        if self.client.is_free:
            print(f"{INIT_CMD} {self.data_type}\n")
            self.client.write(f"{INIT_CMD} {self.data_type}\n")
            self.cmds_queue.put(INIT_CMD, block=False)

    def request_data(self, *args):
        if self.client is None:
            print("No Connection")
            return
        if self.sample_size == 0:
            print("0 SAMPLES REQUESTED, ADJUST THE REFRESH RATE\n")
            return
        if self.slice_size < 1:
            print(f"Slice size must be great or equal to 1, {self.slice_size} provided\n")
        if self.client.is_free:
            self.client.write(f"{GET_CMD} {self.data_type} -json {self.sample_size} -sliced {self.slice_size}\n")
            self.cmds_queue.put(GET_CMD, block=False)

    def create_controlPanel(self, title):
        self.request_timer.timeout.connect(self.request_data)
        self.init_timer.timeout.connect(self.init_server)
        self.controlPanel = BaseControlPanel(title)
        self.controlPanel.on_close(self.close_graphs)
        self.controlPanel.on_close(self.close_connection)

        # example of using a UID to keep track of the object added while also providing a callback function at creation
        self.controlPanel.add_push_button("Connect", (0, 0), callback=self.create_client, UID="CONNECT")
        self.controlPanel.add_push_button("Init", (1, 0), callback=self.init_server, UID="INIT")

        # example of using the provided objet to directly link it to a callback
        request_b = self.controlPanel.add_push_button("Request", (2, 0), UID="REQUEST")
        request_b.clicked.connect(self.requesting_callback)
        pause_b = self.controlPanel.add_push_button("Pause", (2, 1), UID="PAUSE")
        pause_b.clicked.connect(self.pausing_callback)

        self.controlPanel.add_push_button("Disconnect", (3, 0), callback=self.close_connection,
                                          UID="DISCONNECT")
        self.controlPanel.add_Icon("Connection", r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\no_connection.png",
                                   (0, 1, 1, 1), UID="CONNECTION_STATUS")
        self.controlPanel.add_push_button("Screenshot", (3, 1), self.take_screenshot, UID="SCREENSHOT")
        self.controlPanel.add_push_button("Clear", (1, 1), self.clear_callbacks, UID="CLEAR")
        self.controlPanel.show()


    def add_line_graphs_task(self, func):
        if self.line_graphs_list:
            for g in self.line_graphs_list:
                g.add_postProcess(func)

"""                request = Request.parse_obj(json.loads(data))
                sid = 0
                for g, d in self.line_graphs_list:
                    # TODO: WRITE PARSERS FOR DIFFERENT TYPES OF DATA GRAPHS AND DATA STRUCTURES
                    for j in range(7):  # use sensor ids instead
                        if request.Body.data.channels.get(sid) is None:
                            print(f"This Sensor ID doesn't exist in the request Body: {sid}")
                        else:
                            d.Data[sid][0].append(request.Body.data.channels.get(sid).timestamp)
                            d.Data[sid][1].append(request.Body.data.channels.get(sid).real)
                        sid += 1
                    d.slice_size = 10
                    g.updateFigure(d)
                    # g.autoscale_trigger(False)
                    g.show()

                DS = self.level_graph_list[0].get_data_container()

                for j, graph in enumerate(self.level_graph_list):
                    xD = dict()
                    yD = dict()
                    # for grp in np.array([request.Body.data.channels[i].real[-1] for i in grp]):
                    if (j):  # imag
                        ims = np.array(
                            [[request.Body.data.channels[i].imag[-1] for i in grp] for grp in self.groups])
                        # im1 = np.array([request.Body.data.channels[i].imag[-1] for i in self.groups[1]])
                        for i, im in enumerate(ims):
                            yD[f"g{i + 1}"] = np.array(range(len(im)))
                            xD[f"g{i + 1}"] = im
                    else:  # real
                        rs = np.array(
                            [[request.Body.data.channels[i].real[-1] for i in grp] for grp in self.groups])
                        for i, r in enumerate(rs):
                            xD[f"g{i + 1}"] = np.array(range(len(r)))
                            yD[f"g{i + 1}"] = r

                    graph.updateFigure(DS(x_Data=xD,
                                          y_Data=yD,
                                          slice_size=1))
                    # graph.autoscale_trigger(False)
                    graph.show()"""
