from Package.FrontEnd.BaseInterface import BaseGraphCanvas, BaseGraphException

from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.plotDataFormat import LineGraphData, VectorGraphData, LevelGraphData
from Package.DataStructures.RingBuffer import RingBuffer

from Package.HelperTools.ZoomPan_mpl import ZoomPan
from Package.HelperTools.BlitManager import BlitManager

import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.quiver import Quiver, QuiverKey
from matplotlib.colorbar import Colorbar
from matplotlib.cm import get_cmap, ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Patch

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from typing import List, Any, Dict, Callable

import numpy as np


class MPLGraphUpdatingException(BaseGraphException):
    """High level exception raised when an error related to the graph-updating occurs"""


class MPLSingleQuiverFigureException(BaseGraphException):
    """High level exception raised when user provides multiple quiver configs to the same figure object"""


class MPLBasedGraph(BaseGraphCanvas):
    event_archive: list = []  # list of Event Ids used to keep track of which events are implemented
    _dynamic_ax: Any = None
    zoom_handler: ZoomPan = None
    blit: bool = None

    def create_canvas(self):
        self.dynamic_canvas: FigureCanvas = FigureCanvas(Figure())
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        # print(type(self._dynamic_ax))

        if self.structure.xLim:
            xlim = self.structure.xLim
            self.set_x_lim(xlim[0], xlim[1])
        if self.structure.yLim:
            ylim = self.structure.yLim
            self.set_y_lim(ylim[0], ylim[1])

        self.blit = self.structure.blit

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.dynamic_canvas)
        self.setLayout(vbox)

    def make_zoomable(self):
        self.zoom_handler = ZoomPan()
        scale = 1.1
        self.zoom_handler.zoom_factory(self._dynamic_ax, base_scale=scale)
        self.zoom_handler.pan_factory(self._dynamic_ax)

    def set_x_lim(self, downtLim, upLim):
        try:
            self._dynamic_ax.set_xlim(downtLim, upLim)
        except Exception as e:
            print(e)

    def set_y_lim(self, downtLim, upLim):
        try:
            self._dynamic_ax.set_ylim(downtLim, upLim)
        except Exception as e:
            print(e)

    def add_vLine(self, coordinates: List[float], ymin: List[float], ymax: List[float], **kwargs):
        """kwargs:  -colors : array_like of colors, optional, default: 'k'
                    -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional"""
        colors = kwargs.get("colors")
        if colors is None:
            colors = ["k" for _ in coordinates]
        else:
            if type(colors) is list:
                pass
            else:
                colors = [colors for _ in coordinates]
        styles = kwargs.get("linestyle")
        if styles is None:
            styles = ["solid" for _ in coordinates]
        else:
            if type(styles) is list:
                pass
            else:
                styles = [styles for _ in coordinates]
        if type(ymax) is list:
            pass
        else:
            ymax = [ymax for _ in coordinates]

        if type(ymin) is list:
            pass
        else:
            ymin = [ymin for _ in coordinates]

        for i, c in enumerate(coordinates):
            self._dynamic_ax.vlines(x=c, ymin=ymin[i], ymax=ymax[i], colors=colors[i],
                                    linestyles=styles[i])

    def add_hLine(self, coordinates: List[float], xmin: List[float], xmax: List[float], **kwargs):
        """kwargs:  -colors : array_like of colors, optional, default: 'k'
                           -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional
                   return LineCollection"""
        """kwargs:  -colors : array_like of colors, optional, default: 'k'
                    -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional"""
        colors = kwargs.get("colors")
        if colors is None:
            colors = ["k" for _ in coordinates]
        else:
            if type(colors) is list:
                pass
            else:
                colors = [colors for _ in coordinates]
        styles = kwargs.get("linestyle")
        if styles is None:
            styles = ["solid" for _ in coordinates]
        else:
            if type(styles) is list:
                pass
            else:
                styles = [styles for _ in coordinates]
        if type(xmax) is list:
            pass
        else:
            xmax = [xmax for _ in coordinates]

        if type(xmin) is list:
            pass
        else:
            xmin = [xmin for _ in coordinates]

        for i, c in enumerate(coordinates):
            self._dynamic_ax.hlines(y=c, xmin=xmin[i], xmax=xmax[i], colors=colors[i],
                                    linestyles=styles[i])

    def set_onclicked_callback(self, callback: Callable):
        """ callback = function(event)"""
        c_id = self.dynamic_canvas.mpl_connect('button_press_event', callback)
        self.event_archive.append(c_id)

    def add_patch(self, patch: Patch):
        self._dynamic_ax.add_patch(patch)

    def legend_magic(self, legend):
        if legend:
            legend.set_draggable(state=True, use_blit=self.blit)
            self.lined = dict()
            for legline, origline in zip(legend.get_lines(), self.lines.keys()):
                legline.set_picker(True)  # Enable picking on the legend line.
                self.lined[legline] = self.lines[origline]

    def on_pick(self, event):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legline = event.artist
        if type(legline) is Line2D:
            origline = self.lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled.
            legline.set_alpha(1.0 if visible else 0.2)
            self._dynamic_ax.figure.canvas.draw()

    def autoscale_trigger(self, state: bool):
        self.autoscale_flag = state


class MPLLineGraph(MPLBasedGraph):
    lines: Dict[str, Line2D] = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None):
        super().__init__(structure, spawning_position)
        self.create_canvas()
        init_buff = RingBuffer(size_max=10, default_value=0.)
        self.lines = dict((id_, self._dynamic_ax.plot(init_buff.data, animated=self.blit)[0],) for id_, e in
                          self.structure.elements.items())
        if self.blit:
            arg = list(self.lines.values())
            self.BM = BlitManager(self.dynamic_canvas, arg)

        for id_, e in self.structure.elements.items():
            if e.color:
                self.lines[id_].set_color(e.color)
            if e.label:
                self.lines[id_].set_label(e.label)
        leg = self._dynamic_ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                      ncol=int(len(self.structure.elements) / 2))
        self.legend_magic(leg)
        if self.structure.grid:
            self._dynamic_ax.grid()
        self.make_zoomable()

        self.dynamic_canvas.mpl_connect('pick_event', self.on_pick)
        self.autoscale_signal.connect(self.autoscale_trigger)
        self.dynamic_canvas.figure.autofmt_xdate()

    def onUpdatePlot(self, data: LineGraphData):
        try:
            xs, ys = data.x_Data, data.y_Data
            values = list(ys.values())
            min_y, max_y = np.nanmin(values[0].data), np.nanmax(values[0].data)
            min_x, max_x = np.nanmin(xs.data), np.nanmax(xs.data)
            for id_, e in self.structure.elements.items():
                if self.lines[id_].get_visible():
                    sid = e.sensorID
                    y_data = ys.get(sid).data
                    if y_data is not None:
                        min_y = np.minimum(min_y, np.nanmin(y_data))
                        max_y = np.maximum(max_y, np.nanmax(y_data))
                        self.lines[id_].set_xdata(xs.data)
                        self.lines[id_].set_ydata(y_data)

            if self.autoscale_flag:
                dy = (max_y - min_y) * 0.1
                self.set_y_lim(min_y - dy, max_y + dy)
            dx = (max_x - min_x) * 0.1
            self.set_x_lim(min_x - dx, max_x + dx)

            if self.blit:
                self.BM.update()
            else:
                self._dynamic_ax.figure.canvas.draw()


        except Exception as e:
            if type(e) == AttributeError:
                pass
            else:
                import traceback
                raise MPLGraphUpdatingException(ID=self.ID, obj=self, message=traceback.format_exc())
                # print(traceback.format_exc())

    def clearPlot(self):
        if self.lines is not None:
            for id_, _ in self.structure.elements.items():
                self.lines[id_].set_xdata(np.nan)
                self.lines[id_].set_ydata(np.nan)
            if self.blit:
                self.BM.update()
            else:
                self._dynamic_ax.figure.canvas.draw()

    def what_r_u(self, event=None, **kwargs):
        print("I am a Line Graph object based on matplotlib with ID: %s" % self.ID)

    @staticmethod
    def get_data_container():
        return LineGraphData


class MPLLevelGraph(MPLBasedGraph):
    """a Level Graph (scatter plot with points connected by lines) based on Matplotlib"""
    lines: Dict[str, Line2D] = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None):
        super().__init__(structure, spawning_position)
        self.create_canvas()
        self.lines = dict((id_, self._dynamic_ax.plot(e.X, e.Y, "-o", animated=self.blit)[0],) for id_, e in
                          self.structure.elements.items())
        if self.blit:
            arg = list(self.lines.values())
            self.BM = BlitManager(self.dynamic_canvas, arg)
        for id_, e in self.structure.elements.items():
            if e.color:
                self.lines[id_].set_color(e.color)
            if e.label:
                self.lines[id_].set_label(e.label)
        leg = self._dynamic_ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                      ncol=int(len(self.structure.elements) / 2))
        self.legend_magic(leg)
        self.dynamic_canvas.mpl_connect('pick_event', self.on_pick)
        self._dynamic_ax.autoscale(enable=True, axis="y", tight=False)

        if self.structure.grid:
            self._dynamic_ax.grid()
        self.make_zoomable()
        # self.update_signal.connect(self.updatePlot)
        self.autoscale_signal.connect(self.autoscale_trigger)
        self.dynamic_canvas.figure.autofmt_xdate()

    def onUpdatePlot(self, data: LevelGraphData):
        try:
            xs, ys = data.x_Data, data.y_Data
            min_x, max_x = np.inf, np.NINF
            min_y, max_y = np.inf, np.NINF
            for id_, x in xs.items():
                if self.lines[id_].get_visible():
                    y = ys[id_]
                    min_x = np.minimum(min_x, np.nanmin(x))
                    max_x = np.maximum(max_x, np.nanmax(x))
                    min_y = np.minimum(min_y, np.nanmin(y))
                    max_y = np.maximum(max_y, np.nanmax(y))
                    self.lines[id_].set_xdata(x)
                    self.lines[id_].set_ydata(y)

            if min_x != np.inf:
                if self.autoscale_flag:
                    dy = (max_y - min_y) * 0.1
                    self.set_y_lim(min_y - dy, max_y + dy)
                dx = (max_x - min_x) * 0.1
                self.set_x_lim(min_x - dx, max_x + dx)

            if self.blit:
                self.BM.update()
            else:
                self._dynamic_ax.figure.canvas.draw()

        except Exception as e:
            print(e)
            if type(e) == AttributeError:
                pass
            else:
                import traceback
                raise MPLGraphUpdatingException(ID=self.ID, obj=self, message=traceback.format_exc())

    def clearPlot(self):
        if self.lines is not None:
            for id_, _ in self.structure.elements.items():
                self.lines[id_].set_xdata(np.nan)
                self.lines[id_].set_ydata(np.nan)
            if self.blit:
                self.BM.update()
            else:
                self._dynamic_ax.figure.canvas.draw()

    def what_r_u(self, event=None, **kwargs):
        print("I am a Level Graph object based on matplotlib with ID: %s" % self.ID)

    @staticmethod
    def get_data_container():
        return LevelGraphData


class MPLVectorGraph(MPLBasedGraph):
    arrows: Quiver = None
    arrowkeys: QuiverKey = None  # TODO: @iheb Check if arrowkeys are needed
    colorbar: Colorbar = None
    lines: Any
    blit: bool = None
    update_signal = pyqtSignal([VectorGraphData])  # overwite the input type
    counter_q = 0
    plot_lines = False

    # _colormap: str = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None):
        super().__init__(structure, spawning_position)
        try:
            assert len(self.structure.elements) == 1  # api only supports one quiver element pro graph
        except AssertionError as e:
            raise MPLSingleQuiverFigureException(ID=self.structure.ID, obj=structure.elements,
                                                 message="Only one quiver element per Figure is supported and mutiple "
                                                         "were provided")
        self.init_blit, self.blit = self.structure.blit, self.structure.blit

        self.create_canvas()
        self.colorbar = self.add_colorBar(self.structure.colorMap)

        """no need for keys because we made sure elements can only contain one element"""
        e = list(self.structure.elements.values())[0]
        self.arrows = self._dynamic_ax.quiver(e.X, e.Y, np.zeros(e.X.shape), np.zeros(e.X.shape),
                                              cmap=get_cmap(self.structure.colorMap), color=e.color,
                                              zorder=e.zorder, scale=e.scale, units=e.units, animated=self.blit)

        if self.structure.grid:
            self._dynamic_ax.grid()

        if self.blit:
            self.BM = BlitManager(self.dynamic_canvas, [self.arrows])
        self.make_zoomable()

    def toggle_lines(self):
        self.plot_lines = not self.plot_lines
        self._dynamic_ax.collections = [value for value in self._dynamic_ax.collections if
                                        type(value) == Quiver]
        self._dynamic_ax.patches = []
        if self.init_blit:
            self.blit = not self.blit

    def add_colorBar(self, map_name):
        sm = ScalarMappable(cmap=get_cmap(map_name), norm=Normalize())
        return plt.colorbar(sm, ax=self._dynamic_ax, shrink=0.75)

    # @_time
    def onUpdatePlot(self, data: VectorGraphData):
        try:
            # self.mutex.lock()
            # print(self.get_thread_id())
            xs, ys = data.x_Data, data.y_Data
            us, vs = data.u_Data, data.v_Data
            if not data.c_Data:
                data.c_Data = np.hypot(us, vs)
            self.arrows.set_UVC(us, vs, data.c_Data)

            if self.plot_lines:
                self._dynamic_ax.collections = [value for value in self._dynamic_ax.collections if
                                                type(value) == Quiver]
                self._dynamic_ax.patches = []

                e = list(self.structure.elements.values())[0]
                self.lines = self._dynamic_ax.streamplot(xs, ys, us, vs, color=us, cmap="gray", density=e.density,
                                                         zorder=e.zorder + 1)  # zorder +1 means quiver is updated before lines

            if self.blit:
                self.BM.update()
            else:
                self._dynamic_ax.figure.canvas.draw()

        except Exception as e:
            if type(e) == AttributeError:
                print(e)
            else:
                import traceback
                raise MPLGraphUpdatingException(ID=self.ID, obj=self, message=traceback.format_exc())

    def what_r_u(self, event=None, **kwargs):
        print("I am a Vector Graph object based on matplotlib with ID: %s" % self.ID)

    @staticmethod
    def get_data_container():
        return VectorGraphData


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    import sys


    # X, Y = np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30)
    # X, Y = np.meshgrid(X, Y)
    def filter_(data: LevelGraphData):
        for id_, d in data.x_Data.items():
            data.x_Data[id_] = d + np.random.random(1)[0]


    def test_update_scatter(graphs: List[MPLLevelGraph]):
        # print("clicked")
        # x = np.array([0, 1, 2, 3])
        # y = np.random.random(4)
        for graph_ in graphs:
            graph_.update_signal.emit(
                LevelGraphData(x_Data=dict(g1=np.array(range(20)), g2=np.random.uniform(0, 4, 20)),
                               y_Data=dict(g1=np.random.random(20), g2=np.array(range(20)))))


    # struct = GraphStructure(ID="test Graph", blit=True, grid=True,
    #                         elements=dict(g1=ElementStructure(sensorID="channel_0", color="b", label="channel_0")))
    struct_scatter = [GraphStructure(ID="test_scatter_%d" % i, grid=True, blit=True, asynchronous=True,
                                     elements=dict(
                                         g1=ElementStructure(Y=np.array(range(20)), X=np.array([0] * 20),
                                                             color="r", label="g1"),
                                         g2=ElementStructure(X=np.array(range(20)), Y=np.array([1] * 20),
                                                             color="b", label="g2"))
                                     ) for i in range(2)]
    qapp = QApplication(sys.argv)
    bgc = [MPLLevelGraph(struct_scatter[i], spawning_position=p) for i, p in enumerate([1, 3])]

    timer = QTimer()
    timer.timeout.connect(lambda graphs=bgc: test_update_scatter(graphs))

    for b in bgc:
        # b.set_onclicked_callback(lambda event: timer.start(100))
        b.set_onclicked_callback(lambda event, graph=b: timer.start(500))
        b.add_postProcess(filter_)
        b.show()

    qapp.exec_()
    from matplotlib.path import Path


    class Mould(Patch):

        def __init__(self, width, height, **kwargs):
            super().__init__()
            self.mould_width = width
            self.mould_height = height
            self.surfaceLevel = 23.0
            self.wall = 8.0

            vertices = []
            codes = []

            xl = -self.mould_width / 2.0
            xr = self.mould_width / 2.0
            d = self.wall
            yb = 0.0
            yt = self.mould_height

            # generate points of the left side of the moudld wall
            vertices = [(xl - d, yb), (xl, yb), (xl, yt), (xl - d, yt), (xl - d, yb)]
            codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
            # generate points for the right side of the mould wall
            vertices += [(xr, yb), (xr + d, yb), (xr + d, yt), (xr, yt), (xr, yb)]
            codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]

            self.set_edgecolor(kwargs.get("edgecolor", "k"))
            self.set_fill(False)
            self._path = Path(vertices, codes)

        def get_path(self):
            return self._path


    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication

    # bg = MPLBasedGraph(structure=GraphStructure(elements=dict(g1=ElementStructure())))

    global counter
    counter = 0
    import sys
    from matplotlib.backend_bases import MouseButton


    def click_callback(event, graph_, timer):
        # graph_.get_thread_id()
        # print(graph_.ID)
        # print(timer.interval())
        if event.button == MouseButton.LEFT:
            if not timer.isActive():
                timer.start(300)

            # timer.setInterval(500) if timer.interval() == 200 else timer.setInterval(200)

        elif event.button == MouseButton.RIGHT:
            print("right clicked")
            graph_.toggle_lines()


    def preprocess_Test(data: VectorGraphData):
        # for i, d in enumerate(data.u_Data):
        data.v_Data = 10 * data.v_Data
        data.u_Data = 10 * data.u_Data


    def normalize(data: VectorGraphData):
        data.u_Data = data.u_Data / np.sqrt(data.u_Data ** 2 + data.v_Data ** 2)
        data.v_Data = data.v_Data / np.sqrt(data.u_Data ** 2 + data.v_Data ** 2)
        # V = V / np.sqrt(U ** 2 + V ** 2);
        # def _normalize_1d(arr: np.ndarray):
        #     return (arr - np.amin(arr))/ (np.amax(arr) - np.amin(arr))
        # data.u_Data = _normalize_1d(data.u_Data)
        # data.v_Data = _normalize_1d(data.v_Data)
        # print(np.amax(data.u_Data))
        # print(np.amax(data.v_Data))


    def butter_highpass_filter(data, cutoff, fs, order=5):
        from scipy import signal
        def butter_highpass(cutoff, fs, order=5):
            nyq = 0.5 * fs
            normal_cutoff = cutoff / nyq
            b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
            return b, a

        try:
            b, a = butter_highpass(cutoff, fs, order=order)
            y = signal.filtfilt(b, a, data)
            return y
        except Exception as e:
            print(e)
            return data


    def filter_noise(data: VectorGraphData):
        # data.u_Data = butter_highpass_filter(data.u_Data, 10, 100)
        # data.v_Data = butter_highpass_filter(data.v_Data, 10, 100)
        shape = data.u_Data.shape
        data.u_Data *= np.random.random(shape)
        data.v_Data *= np.random.random(shape)
        # for i in range(100):
        #     pass
        # time.sleep(0.5)


    # @_time
    def test(graph_):
        try:
            global counter
            for g in graph_:
                # print(g.get_thread_id())
                GraphData.u_Data = np.cos(GraphData.x_Data + counter * 0.1)
                GraphData.v_Data = np.sin(GraphData.y_Data + counter * 0.1)
                if g.isVisible():
                    g.update_signal.emit(GraphData)

            counter += 1
        except Exception as e:
            print(e)


    X, Y = np.meshgrid(np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30))
    setup_ = [GraphStructure(colorMap="jet", elements=dict(q1=ElementStructure(X=X, Y=Y), ), blit=True,
                             asynchronous=True) for i in range(4)]

    GraphData = VectorGraphData(x_Data=X, y_Data=Y, u_Data=np.zeros(X.shape), v_Data=np.zeros(Y.shape))
    # GraphData[4]
    mould = Mould(0., 0.635, edgecolor='g')

    # factory = VectorGraphFactory()
    # from Package.FrontEnd.BackgroundProcessing import QtProcessWrapper

    qapp = QApplication(sys.argv)
    # graphs = []
    # for i in range(1, 5):
    # if i == 4:
    #     setup_.asynchronous = True
    # graphs.append(MPLVectorGraph(setup_[i-1], spawning_position=i))
    graphs = list(MPLVectorGraph(setup_[i - 1], spawning_position=i) for i in range(1, 5))

    t = QTimer()
    t.timeout.connect(lambda: test(graphs))

    for g in graphs:
        g.set_onclicked_callback(lambda event, graph=g: click_callback(event, graph, t))
        # g.add_patch(Mould(1, 3, edgecolor='g'))
        # print(g.get_thread_id())
        # g.add_postProcess(normalize)
        # g.add_postProcess(filter_noise)
        g.show()

    qapp.exec_()
