from abc import ABC, abstractmethod
from typing import List, Type, Dict

import numpy as np

from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.RingBuffer import RingBuffer
from Package.DataStructures.plotDataFormat import LineGraphData, LevelGraphData, VectorGraphData
from Package.DataStructures.requestBody import Request
from Package.FrontEnd.BaseInterface import BaseFactory
from Package.FrontEnd.factories import QTFactory, MPLFactory, MayaviFactory


class RequestParser(ABC):

    def __init__(self, x_axis_id: str, y_axis_id: str, z_axis_id: str = None):
        self.x_axis_id = x_axis_id
        self.y_axis_id = y_axis_id
        self.z_axis_id = z_axis_id
        self.parsed_data = None

    @property
    def data(self):
        return self.parsed_data


class LineGraphParser(RequestParser):
    def __init__(self, graph_structure: GraphStructure, factory_: BaseFactory, Buffer_size_: int,
                 x_axis_id: str, y_axis_id: str, slice_size_=10):
        super().__init__(x_axis_id, y_axis_id)
        self.slices_size = slice_size_
        DS: Type[LineGraphData] = factory_.get_LineGraph_DataStructure()
        RB: Type[RingBuffer] = DS.get_RB()
        dummy_dict = dict()
        for gid, struct in graph_structure.elements.items():
            dummy_dict[struct.sensorID] = (
                RB(size_max=Buffer_size_, default_value=np.nan), RB(size_max=Buffer_size_, default_value=np.nan))
        self.parsed_data = DS(Data=dummy_dict)

    def __call__(self, request: Request, **kwargs):
        for sid, data_ in self.parsed_data.Data.items():
            if request.Body.data.channels.get(sid) is None:
                continue
            x = request.Body.data.channels.get(sid).get_by_name(self.x_axis_id)
            starting_index = 0
            for i, v in enumerate(x):
                if v > data_[0][-1]:
                    starting_index = i
                    break

            data_[0].append(x[starting_index:][::self.slices_size])
            data_[1].append(
                request.Body.data.channels.get(sid).get_by_name(self.y_axis_id)[starting_index:][::self.slices_size])


class LevelGraphParser(RequestParser):
    def __init__(self, graph_structure: GraphStructure, factory_: BaseFactory, x_axis_id: str, y_axis_id: str):
        super().__init__(x_axis_id, y_axis_id)
        # x_id: "real" or "imag" or "timestamp"
        # y_id: "real" or "imag" or "timestamp"
        DS: Type[LevelGraphData] = factory_.get_LevelGraph_DataStructure()
        dummy_x = dict()
        dummy_y = dict()
        self.sensor_ids: Dict[str, List[int]] = dict()
        for gid, struct in graph_structure.elements.items():
            self.sensor_ids[gid] = struct.sensorIDs
            dummy_x[gid] = struct.X_init
            dummy_y[gid] = struct.Y_init
        print(self.sensor_ids)
        self.parsed_data = DS(x_Data=dummy_x, y_Data=dummy_y)

    def __call__(self, request: Request, **kwargs):
        for gid in self.parsed_data.x_Data.keys():
            sids = self.sensor_ids[gid]

            if self.x_axis_id == "range":
                x = np.array(range(len(self.parsed_data.x_Data[gid])))
            else:
                x = np.array([request.Body.data.channels.get(sid).get_by_name(self.x_axis_id)[-1]
                              for sid in sids])
            if self.y_axis_id == "range":
                y = np.array(range(len(self.parsed_data.y_Data[gid])))
            else:
                y = np.array([request.Body.data.channels.get(sid).get_by_name(self.y_axis_id)[-1]
                              for sid in sids])

            self.parsed_data.x_Data[gid] = x
            self.parsed_data.y_Data[gid] = y


class VectorGraphParser(RequestParser):
    def __init__(self, graph_structure: GraphStructure, factory_: BaseFactory, x_axis_id: str, y_axis_id: str,
                 z_axis_id: str = None):
        super().__init__(x_axis_id, y_axis_id, z_axis_id)
        self.parsed_data = factory_.get_VectorGraph_DataStructure()

    def __call__(self, request: Request, **kwargs):
        ...


if __name__ == "__main__":
    import json


    def import_examples(path=r"C:\Users\User\Desktop\HZDR\hzdr_visu_tool\Package\Tests\Test_Requests.json") -> dict:
        """function responsible for importing the test jsons from a file"""
        with open(path, "r") as test_file:
            test = json.load(test_file)
        return test


    # 'b': QtGui.QColor(0,0,255,255),
    # 'g': QtGui.QColor(0,255,0,255),
    # 'r': QtGui.QColor(255,0,0,255),
    # 'c': QtGui.QColor(0,255,255,255),
    # 'm': QtGui.QColor(255,0,255,255),
    # 'y': QtGui.QColor(255,255,0,255),
    # 'k': QtGui.QColor(0,0,0,255),
    # 'w': QtGui.QColor(255,255,255,255),
    # 'd': QtGui.QColor(150,150,150,255),
    # 'l': QtGui.QColor(200,200,200,255),
    # 's': QtGui.QColor(100,100,150,255),

    prefix = "omek"
    structure = GraphStructure(ID=f"{prefix} Line Graph Test 0", grid=True, blit=True,
                               elements=dict(
                                   g1=ElementStructure(sensorID=0, color="b", label="ch0"),
                                   g2=ElementStructure(sensorID=1, color="g", label="ch1"),
                                   g3=ElementStructure(sensorID=2, color="k", label="ch2"),
                                   g4=ElementStructure(sensorID=3, color="r", label="ch3"),
                                   g5=ElementStructure(sensorID=4, color="c", label="ch4"),
                                   g6=ElementStructure(sensorID=5, color="m", label="ch5"),
                                   g7=ElementStructure(sensorID=6, color="k", label="ch6"), )
                               )
    parser = LineGraphParser(graph_structure=structure, factory_=QTFactory(), Buffer_size_=5, x_axis_id="timestamp",
                             y_axis_id="real")

    data: dict = import_examples().get("correct")
    #
    auto_obj = Request.parse_obj(data)
    input("\nhey")
    parser(auto_obj)

    structure = GraphStructure(ID=f"{prefix} Level Graph Test {0}", grid=True, blit=True,  # with_lines=False,
                               elements=dict(g1=ElementStructure(X_init=np.array(range(2)), Y_init=np.array([0] * 2),
                                                                 sensorIDs=[0, 1],
                                                                 color="b", label=f"real ch0-ch1"),
                                             g2=ElementStructure(X_init=np.array(range(2)), Y_init=np.array([0] * 2),
                                                                 sensorIDs=[2, 3],
                                                                 color="r", label=f"real ch2-ch3"),
                                             ), )
    parser = LevelGraphParser(graph_structure=structure, factory_=QTFactory(), x_axis_id="range",
                              y_axis_id="real")

    input("\nhey2")
    parser(auto_obj)
