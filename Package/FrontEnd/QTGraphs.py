from Package.FrontEnd.BaseInterface import BaseGraphCanvas, BaseGraphException
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.plotDataFormat import LineGraphData, LevelGraphData
from Package.DataStructures.RingBuffer import RingBuffer

import pyqtgraph as pg

PS = pg.QtCore.Qt.PenStyle
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from typing import List, Any, Dict, Callable, Tuple

import numpy as np


class QTBasedGraph(BaseGraphCanvas):
    line_syles = dict(solid=PS(1), dashed=PS(2), dashdot=PS(4), dotted=PS(3))
    _dynamic_ax: Any = None

    def create_canvas(self):
        # self.dynamic_canvas = pg.PlotWidget()
        self.dynamic_canvas = pg.plot()
        self._dynamic_ax = self.dynamic_canvas.getPlotItem()
        self._dynamic_ax.addLegend(colCount=int(len(self.structure.elements) / 2))
        # self.add_hLine([0.5,0.6,0.7], linestyle=["dashdot", "dotted", "solid"], color=["r", "b", "k"], label=["r", "b", "k"] )
        layout = QHBoxLayout(self)
        layout.addWidget(self.dynamic_canvas)
        self.setLayout(layout)
        self.set_xy_lim()

    def set_x_lim(self, downtLim, upLim):
        try:
            self._dynamic_ax.setXRange(downtLim, upLim)
        except Exception as e:
            print(e)

    def set_y_lim(self, downtLim, upLim):
        try:
            self._dynamic_ax.setYRange(downtLim, upLim)
        except Exception as e:
            print(e)

    def add_vLine(self, coordinates: List[float], ymin: List[float] = None, ymax: List[float] = None, **kwargs):
        "ymin and ymax are not supported for Qt graphs and uses infinite lines instead"
        for c in enumerate(coordinates):
            self._dynamic_ax.addItem(pg.InfiniteLine(pos=c, angle=90))

    def add_hLine(self, coordinates: List[float], ymin: List[float] = None, ymax: List[float] = None, **kwargs):

        linestyles = self._map_line_api(args=kwargs, key="linestyle", lookup_container=self.line_syles,
                                        default_value="solid",
                                        iterable=coordinates)
        colors = self._map_line_api(args=kwargs, key="color", lookup_container=None, default_value="r",
                                    iterable=coordinates)
        for i, c in enumerate(coordinates):
            self._dynamic_ax.addItem(pg.InfiniteLine(pos=c, angle=0, pen=pg.mkPen(colors[i], width=2,
                                                                                  style=linestyles[i])))

    def set_onclicked_callback(self, callback: Callable, **kwargs):
        """ callback = function(event)"""
        self._dynamic_ax.scene().sigMouseClicked.connect(lambda event: callback(event, **kwargs))

    def clearPlot(self):
        self.dynamic_canvas.clear()

    def _map_line_api(self, args: dict, key: str, default_value: Any, lookup_container: dict, iterable: List[Any]):
        """translate matplotlib api to pyqtgraph api for lines"""

        "ymin and ymax are not supported for Qt graphs and uses infinite lines instead"
        subject = args.get(key)
        # print(subject)
        # print(lookup_container)
        # print(default_value)
        if subject is not None:
            # print("value is not None")
            if type(subject) is list:
                # print("value is Iterable")
                if lookup_container:
                    # print("values from lookup container")

                    arr = [lookup_container.get(s) for s in subject]
                else:
                    # print("value from args")
                    arr = subject
            else:
                # print("value is not Iterable")
                if lookup_container:
                    # print("values from lookup container")
                    arr = [lookup_container.get(subject) for l in iterable]
                else:
                    # print("value from args")
                    arr = [subject for l in iterable]
        else:
            # print("value is None")
            if lookup_container:
                arr = [lookup_container.get(default_value) for _ in iterable]
            else:
                arr = [default_value for _ in iterable]
        return arr


class QTLineGraph(QTBasedGraph):
    lines: Dict[str, pg.PlotItem] = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None):
        super().__init__(structure, spawning_position)
        self.create_canvas()
        init_buff = RingBuffer(size_max=10, default_value=0.)
        self.lines = dict(
            (id_, self._dynamic_ax.plot(init_buff.data, init_buff.data, pen=pg.mkPen(e.color, width=2), name=e.label))
            for id_, e in self.structure.elements.items())
        if self.structure.grid:
            self.dynamic_canvas.showGrid(x=True, y=True)
        self.autoscale_signal.connect(self.autoscale_trigger)

    def onUpdatePlot(self, dataStruct: LineGraphData):
        try:

            values = list(dataStruct.Data.values())
            min_x, max_x = np.inf, np.NINF
            min_y, max_y = np.inf, np.NINF

            for id_, e in self.structure.elements.items():
                if self.lines[id_].isVisible():
                    sid = e.sensorID
                    y_data = dataStruct.Data.get(sid)[1].data
                    x_data = dataStruct.Data.get(sid)[0].data
                    if y_data is not None:
                        min_x = np.minimum(min_x, np.nanmin(x_data))
                        max_x = np.maximum(max_x, np.nanmax(x_data))
                        min_y = np.minimum(min_y, np.nanmin(y_data))
                        max_y = np.maximum(max_y, np.nanmax(y_data))
                        self.lines[id_].setData(x_data, y_data)
            if min_x != np.inf and max_x != np.NINF:
                if self.autoscale_flag:
                    dy = (max_y - min_y) * 0.1
                    self.set_y_lim(min_y - dy, max_y + dy)
                    dx = (max_x - min_x) * 0.1
                    self.set_x_lim(min_x - dx, max_x + dx)

        except Exception as e:
            print(e)
            if type(e) == AttributeError:
                pass
            else:
                import traceback
                print(traceback.format_exc())

    def clearPlot(self):
        if self.lines is not None:
            for id_, _ in self.structure.elements.items():
                self.lines[id_].setData([np.nan], [np.nan])

    def autoscale_trigger(self, state: bool):
        self.autoscale_flag = state

    def what_r_u(self, event=None, **kwargs):
        print("I am a Line Graph object based on pyqtgraph with ID: %s" % self.ID)

    @staticmethod
    def get_data_container():
        return LineGraphData


class QTLevelGraph(QTBasedGraph):
    ScatterGroups: Dict[str, pg.PlotDataItem] = None
    lines: Dict[str, pg.PlotItem] = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None, line_color=(0, 0, 0)):
        super().__init__(structure, spawning_position)
        self.create_canvas()
        if self.structure.with_lines:
            self.lines = dict(
                (id_, self._dynamic_ax.plot(e.X_init, e.Y_init, pen=pg.mkPen(line_color, width=2)))
                for id_, e in self.structure.elements.items())

        self.ScatterGroups = dict((id_, self._dynamic_ax.scatterPlot(e.X_init, e.Y_init, pen=pg.mkPen(e.color, width=2),
                                                                     name=e.label, brush=pg.mkBrush(e.color)))
                                  for id_, e in self.structure.elements.items())

        if self.structure.grid:
            self.dynamic_canvas.showGrid(x=True, y=True)

    def onUpdatePlot(self, dataStruct: LevelGraphData):
        try:

            xs, ys = dataStruct.x_Data, dataStruct.y_Data
            min_x, max_x = np.inf, np.NINF
            min_y, max_y = np.inf, np.NINF
            for id_, x in xs.items():

                min_x = np.minimum(min_x, np.nanmin(x))
                max_x = np.maximum(max_x, np.nanmax(x))
                min_y = np.minimum(min_y, np.nanmin(ys[id_]))
                max_y = np.maximum(max_y, np.nanmax(ys[id_]))
                self.ScatterGroups[id_].setData(x, ys[id_])
                if self.lines is not None:
                    self.lines[id_].setVisible(self.ScatterGroups[id_].isVisible())
                    self.lines[id_].setData(x, ys[id_])

            if min_x != np.inf and max_x != np.NINF:
                if self.autoscale_flag:
                    dy = (max_y - min_y) * 0.1
                    self.set_y_lim(min_y - dy, max_y + dy)
                    dx = (max_x - min_x) * 0.1
                    self.set_x_lim(min_x - dx, max_x + dx)

        except Exception as e:
            if type(e) == AttributeError:
                pass
            else:
                import traceback
                print(traceback.format_exc())

    def clearPlot(self):
        if self.ScatterGroups is not None:
            for id_, _ in self.structure.elements.items():
                if self.lines is not None:
                    self.lines[id_].setData([np.nan], [np.nan])
                self.ScatterGroups[id_].setData([np.nan], [np.nan])

    def what_r_u(self, event=None, **kwargs):
        print("I am a Level Graph object based on pyqtgraph with ID: %s" % self.ID)

    @staticmethod
    def get_data_container():
        return LevelGraphData


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    import sys


    # X, Y = np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30)
    # X, Y = np.meshgrid(X, Y)
    def filter_(data: LevelGraphData):
        for id_, d in data.x_Data.items():
            data.x_Data[id_] = d + np.random.random(1)[0]


    def test_update_scatter(graphs: List[QTLevelGraph]):
        # print("clicked")
        # x = np.array([0, 1, 2, 3])
        # y = np.random.random(4)
        for graph_ in graphs:
            graph_.update_signal.emit(
                LevelGraphData(x_Data=dict(g1=np.array([0, 1, 2, 3]), g2=np.random.uniform(0, 4, 4)),
                               y_Data=dict(g1=np.random.random(4), g2=np.array([0, 1, 2, 3]))))
            # graph_.update_signal.emit(ScatterGraphData(GroupID="g2", x_Data=np.random.uniform(0,4,4),
            #                                            y_Data=np.array([0, 1, 2, 3])))


    # struct = GraphStructure(ID="test Graph", blit=True, grid=True,
    #                         elements=dict(g1=ElementStructure(sensorID="channel_0", color="b", label="channel_0")))
    struct_scatter = GraphStructure(ID="test_scatter", grid=False,
                                    elements=dict(
                                        g1=ElementStructure(Y=np.array([0, 1, 2, 3]), X=np.array([0, 0, 0, 0]),
                                                            color="r"),
                                        g2=ElementStructure(X=np.array([0, 1, 2, 3]), Y=np.array([1, 1, 1, 1]),
                                                            color="b"))
                                    )
    qapp = QApplication(sys.argv)
    bgc = [QTLevelGraph(struct_scatter, spawning_position=i) for i in [2, 4]]

    timer = QTimer()
    timer.timeout.connect(lambda graphs=bgc: test_update_scatter(graphs))

    for b in bgc:
        b.set_onclicked_callback(lambda event: timer.start(100))
        b.add_postProcess(filter_)
        b.show()

    qapp.exec_()
