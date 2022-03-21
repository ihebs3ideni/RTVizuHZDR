# from Package.DataStructures.GraphArgsStructure import GraphStructure
# from Package.DataStructures.RingBuffer import RingBuffer
# from Package.DataStructures.plotDataFormat import LineGraphData, VectorGraphData
# from Package.DataStructures.TypeFactory import LinePlotDataFormatFactory, GraphStructureFactory, VectorGraphDataFormatFactory
# from abc import ABC, abstractmethod
# from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget
# from PyQt5.QtCore import pyqtSlot, pyqtSignal
# import pyqtgraph as pg
# PS = pg.QtCore.Qt.PenStyle
# import time
#
# from Package.HelperTools.ZoomPan_mpl import ZoomPan
#
# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')
# import matplotlib
# matplotlib.use("Qt5Agg")
#
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# # from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
# from matplotlib.lines import Line2D
# from matplotlib.quiver import Quiver, QuiverKey
#
# from matplotlib.cm import get_cmap
#
#
# import matplotlib.ticker as plticker
#
# import numpy as np
# from typing import Any, Callable, Dict, List
#
# from Package.HelperTools.BlitManager import BlitManager
# from Package.HelperTools.QTQuiverWrapper import CenteredArrowItem, QTQuiver
# from collections.abc import Iterable
#
# #
# # plt.style.use('dark_background')
#
#
# class BaseGraphException(Exception):
#     """Base High level exception to notify user to errors related to the UI"""
#
#     def __init__(self, ID: str, obj: Any, message: str):
#         self.ID = ID
#         self.obj = obj
#         self.message = message
#         super().__init__(message)
#
#     def __str__(self):
#         return "Error Message: %s ; @ Error source ID: %s" % (self.message, self.ID)
#
#
# class WrongDimensionsException(BaseGraphException):
#     """Base High level exception to notify user to errors in config shapes"""
#     pass
#
#
# class IDConflictException(BaseGraphException):
#     """Base High level exception to notify user to objects with the same id"""
#     pass
#
#
# class BadDataFormatException(BaseGraphException):
#     """Base High level exception to be raised when the data provided is not in the correct format"""
#     pass
#
# class LibraryDoesntSupportException(BaseGraphException):
#     """Base High level exception to be raised when requested Graph type isn't supported by the requested Library"""
#     pass
#
#
# class BaseGraphCanvas(QWidget):
#     """Base class for all graph objects/widgets produced by the factory"""
#     ID: str = None
#     xRange: int = 100
#     update_signal = pyqtSignal([object])
#     autoscale_signal = pyqtSignal([bool])
#     autoscale_flag: bool = True
#     dynamic_canvas: Any = None
#     preprocessing = []
#
#     def __init__(self, structure: GraphStructure):
#         super().__init__()
#         self.structure = structure
#         self.ID = self.structure.ID
#         self.update_signal.connect(self.updateRoutine)
#         # self.setStyleSheet("""
#         #         QWidget {
#         #             border: 20px solid black;
#         #             border-radius: 10px;
#         #             background-color: rgb(255, 255, 255);
#         #             }
#         #         """)
#
#     @abstractmethod
#     def add_vLine(self, coordinates: List[float], ymin: List[float], ymax: List[float], **kwargs):
#         """ a simple api to draw vertical lines on the graph canvas.
#                 -this api should allow the addition of either one or multiple lines at a time.
#                 -kwargs should depend on the implementation"""
#         pass
#
#     @abstractmethod
#     def add_hLine(self, coordinates: List[float], xmin: List[float], xmax: List[float], **kwargs):
#         """ a simple api to draw horizontal lines on the graph canvas.
#                 -this api should allow the addition of either one or multiple lines at a time.
#                 -kwargs should depend on the implementation"""
#         pass
#
#     @abstractmethod
#     def set_y_lim(self, downtLim, upLim):
#         pass
#
#     @abstractmethod
#     def set_x_lim(self, downtLim, upLim):
#         pass
#
#     @abstractmethod
#     def clearPlot(self):
#         pass
#
#     @abstractmethod
#     def updatePlot(self, data:Any):
#         pass
#
#     def updateRoutine(self, data):
#         for p in self.preprocessing:
#             p(data)
#         self.updatePlot(data)
#
#
#     @classmethod
#     @pyqtSlot(bool)
#     def autoscale_trigger(self, state: bool):
#         self.autoscale_flag = state
#
#     def set_xRange(self, xrange: int):
#         self.xRange = xrange
#
#     def set_xy_lim(self):
#         """uses the set_x_lim and set_y_lim interface that needs to be implemented by the child class"""
#         if self.structure.xLim:
#             xlim = self.structure.xLim
#             self.set_x_lim(xlim[0], xlim[1])
#         if self.structure.yLim:
#             ylim = self.structure.yLim
#             self.set_y_lim(ylim[0], ylim[1])
#
#     def what_r_u(self, event=None, **kwargs):
#         """to be reimplemented by each child Class to redefine themselves.
#             args: event necessary if used as on click callback"""
#         print("I am a Base Graph object with ID: %s" % self.ID)
#
#     def toggle_autoscale(self, event=None, **kwargs):
#         """this function uses the signal slot mechanism that needs to be specified by child classes.
#             args: event necessary if used as on click callback"""
#         self.autoscale_signal.emit(not self.autoscale_flag)
#
#     def location_on_the_screen(self):
#         ag = QDesktopWidget().availableGeometry()
#         sg = QDesktopWidget().screenGeometry()
#
#         widget = self.geometry()
#         x = ag.width() - widget.width()
#         y = 2 * ag.height() - sg.height() - widget.height()
#         self.move(x, y)
#
#     def add_preprocess(self, func:Callable):
#         self.preprocessing.append(func)
#
#
#
#
#
# class QTBasedGraph(BaseGraphCanvas):
#     line_syles = dict(solid=PS(1),dashed=PS(2), dashdot=PS(4), dotted=PS(3))
#
#     def create_canvas(self):
#         # self.dynamic_canvas = pg.PlotWidget()
#         self.dynamic_canvas = pg.plot()
#         self._dynamic_ax = self.dynamic_canvas.getPlotItem()
#         self._dynamic_ax.addLegend(colCount=int(len(self.structure.elements) / 2))
#         # self.add_hLine([0.5,0.6,0.7], linestyle=["dashdot", "dotted", "solid"], color=["r", "b", "k"], label=["r", "b", "k"] )
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.dynamic_canvas)
#         self.setLayout(layout)
#         self.set_xy_lim()
#
#     def set_x_lim(self, downtLim, upLim):
#         try:
#             self._dynamic_ax.setXRange(downtLim, upLim)
#         except Exception as e:
#             print(e)
#
#     def set_y_lim(self, downtLim, upLim):
#         try:
#             self._dynamic_ax.setYRange(downtLim, upLim)
#         except Exception as e:
#             print(e)
#
#     def add_vLine(self, coordinates: List[float], ymin: List[float] = None, ymax: List[float] = None, **kwargs):
#         "ymin and ymax are not supported for Qt graphs and uses infinite lines instead"
#         for c in enumerate(coordinates):
#             self._dynamic_ax.addItem(pg.InfiniteLine(pos=c, angle=90))
#
#     def add_hLine(self, coordinates: List[float], ymin: List[float] = None, ymax: List[float] = None, **kwargs):
#
#         linestyles = self._translate_api(args=kwargs, key="linestyle", lookup_container=self.line_syles, default_value="solid",
#                                          iterable=coordinates)
#         colors = self._translate_api(args=kwargs, key="color", lookup_container=None, default_value="r",
#                                          iterable=coordinates)
#         for i, c in enumerate(coordinates):
#             self._dynamic_ax.addItem(pg.InfiniteLine(pos=c, angle=0, pen=pg.mkPen(colors[i], width=2,
#                                                                                   style=linestyles[i])))
#
#
#     def set_onclicked_callback(self, callback: Callable, **kwargs):
#         """ callback = function(event)"""
#         self._dynamic_ax.scene().sigMouseClicked.connect(lambda event: callback(event, **kwargs))
#
#     def clearPlot(self):
#         self.dynamic_canvas.clear()
#
#     def _translate_api(self, args:dict, key: str,default_value: Any, lookup_container: dict, iterable: List[Any]):
#         """translate matplotlib api to pyqtgraph api for lines"""
#
#         "ymin and ymax are not supported for Qt graphs and uses infinite lines instead"
#         subject = args.get(key)
#         # print(subject)
#         # print(lookup_container)
#         # print(default_value)
#         if subject is not None:
#             # print("value is not None")
#             if type(subject) is list:
#                 # print("value is Iterable")
#                 if lookup_container:
#                     # print("values from lookup container")
#
#                     arr = [lookup_container.get(s) for s in subject]
#                 else:
#                     # print("value from args")
#                     arr = subject
#             else:
#                 # print("value is not Iterable")
#                 if lookup_container:
#                     # print("values from lookup container")
#                     arr = [lookup_container.get(subject) for l in iterable]
#                 else:
#                     # print("value from args")
#                     arr = [subject for l in iterable]
#         else:
#             # print("value is None")
#             if lookup_container:
#                 arr = [lookup_container.get(default_value) for _ in iterable]
#             else:
#                 arr = [default_value for _ in iterable]
#         return arr
#
# class MPLBasedGraph(BaseGraphCanvas):
#     event_archive: list = []
#     _dynamic_ax: Any = None
#     zoom_handler: ZoomPan = None
#
#     def create_canvas(self):
#         self.dynamic_canvas:FigureCanvas = FigureCanvas(Figure())
#         # self.dynamic_canvas.figure.tight_layout()
#         self._dynamic_ax = self.dynamic_canvas.figure.subplots()
#         # print(self._dynamic_ax)
#         # self.add_hLine([0.5, 0.6, 0.8],xmin=[5,6,7],xmax=[100,101,102], colors=["red", "g", "b"], label=["l1", "l2","l3"],
#         #                linestyle=["solid", "dotted", "dashed"])
#         # self.add_vLine([10,20,30],ymin=-2,ymax=2, colors=["red", "k", "y"], label=["l4", "l5", "l6"])
#         # self.dynamic_canvas.set_tight_layout(True)
#
#         if self.structure.xLim:
#             xlim = self.structure.xLim
#             self.set_x_lim(xlim[0], xlim[1])
#         if self.structure.yLim:
#             ylim = self.structure.yLim
#             self.set_y_lim(ylim[0], ylim[1])
#         # toolbar = NavigationToolbar(self.dynamic_canvas, self)
#
#         vbox = QVBoxLayout(self)
#         # vbox.addWidget(toolbar)
#         vbox.addWidget(self.dynamic_canvas)
#         self.setLayout(vbox)
#
#
#     def make_zoomable(self):
#         self.zoom_handler = ZoomPan()
#         scale = 1.1
#         self.zoom_handler.zoom_factory(self._dynamic_ax, base_scale=scale)
#         self.zoom_handler.pan_factory(self._dynamic_ax)
#
#     def set_x_lim(self, downtLim, upLim):
#         try:
#             self._dynamic_ax.set_xlim(downtLim, upLim)
#         except Exception as e:
#             print(e)
#
#     def set_y_lim(self, downtLim, upLim):
#         try:
#             self._dynamic_ax.set_ylim(downtLim, upLim)
#         except Exception as e:
#             print(e)
#
#     def add_vLine(self, coordinates: List[float], ymin: List[float], ymax: List[float], **kwargs):
#         """kwargs:  -colors : array_like of colors, optional, default: 'k'
#                     -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional"""
#         colors = kwargs.get("colors")
#         if colors is None:
#             colors = ["k" for _ in coordinates]
#         else:
#             if type(colors) is list:
#                 pass
#             else:
#                 colors = [colors for _ in coordinates]
#         styles = kwargs.get("linestyle")
#         if styles is None:
#             styles = ["solid" for _ in coordinates]
#         else:
#             if type(styles) is list:
#                 pass
#             else:
#                 styles = [styles for _ in coordinates]
#         if type(ymax) is list:
#             pass
#         else:
#             ymax = [ymax for _ in coordinates]
#
#         if type(ymin) is list:
#             pass
#         else:
#             ymin = [ymin for _ in coordinates]
#
#         for i, c in enumerate(coordinates):
#             self._dynamic_ax.vlines(x=c, ymin=ymin[i], ymax=ymax[i], colors=colors[i],
#                                     linestyles=styles[i])
#
#     def add_hLine(self, coordinates: List[float], xmin: List[float], xmax: List[float], **kwargs):
#         """kwargs:  -colors : array_like of colors, optional, default: 'k'
#                            -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional
#                    return LineCollection"""
#         """kwargs:  -colors : array_like of colors, optional, default: 'k'
#                     -linestyles : {'solid', 'dashed', 'dashdot', 'dotted'}, optional"""
#         colors = kwargs.get("colors")
#         if colors is None:
#             colors = ["k" for _ in coordinates]
#         else:
#             if type(colors) is list:
#                 pass
#             else:
#                 colors = [colors for _ in coordinates]
#         styles = kwargs.get("linestyle")
#         if styles is None:
#             styles = ["solid" for _ in coordinates]
#         else:
#             if type(styles) is list:
#                 pass
#             else:
#                 styles = [styles for _ in coordinates]
#         if type(xmax) is list:
#             pass
#         else:
#             xmax = [xmax for _ in coordinates]
#
#         if type(xmin) is list:
#             pass
#         else:
#             xmin = [xmin for _ in coordinates]
#
#         for i, c in enumerate(coordinates):
#             self._dynamic_ax.hlines(y=c, xmin=xmin[i], xmax=xmax[i], colors=colors[i],
#                                     linestyles=styles[i])
#
#     def set_onclicked_callback(self, callback: Callable):
#         """ callback = function(event)"""
#         c_id = self.dynamic_canvas.mpl_connect('button_press_event', callback)
#         self.event_archive.append(c_id)
#
# class MAYAVIBasedGraph(BaseGraphCanvas):
#     pass
#
# class QTLineGraph(QTBasedGraph):
#     lines: Dict[str, pg.PlotItem] = None
#
#     def __init__(self, structure: GraphStructure):
#         super().__init__(structure)
#         self.location_on_the_screen()
#         self.create_canvas()
#         init_buff = RingBuffer(size_max=10, default_value=np.nan)
#         for id_, e in self.structure.elements.items():
#             print(type(e))
#         self.lines = dict(
#             (id_, self._dynamic_ax.plot(init_buff.data, init_buff.data, pen=pg.mkPen(e.color, width=2), name=e.label))
#             for id_, e in self.structure.elements.items())
#         if self.structure.grid:
#             self.dynamic_canvas.showGrid(x=True, y=True)
#         self.update_signal.connect(self.updatePlot)
#         self.autoscale_signal.connect(self.autoscale_trigger)
#
#     def updatePlot(self, data: LineGraphData):
#         try:
#             xs, ys = data.x_Data, data.y_Data
#             values = list(ys.values())
#             min_y, max_y = np.nanmin(values[0].data), np.nanmax(values[0].data)
#             min_x, max_x = np.nanmin(xs.data), np.nanmax(xs.data)
#             for id_, e in self.structure.elements.items():
#                 y_data = ys.get(id_).data
#                 if y_data is not None:
#                     min_y = np.minimum(min_y, np.nanmin(y_data))
#                     max_y = np.maximum(max_y, np.nanmax(y_data))
#                 self.lines[id_].setData(xs.data, y_data)
#             # ax =self.dynamic_canvas.getAxis('bottom')
#             # ax.setTicks([[(v, "%.1f" % v) for v in np.nan_to_num(xs.data[::10])]])
#             if self.autoscale_flag:
#                 self.set_y_lim(min_y - 0.1 * min_y, max_y * 1.1)
#             self.set_x_lim(min_x, max_x)
#             # print(min_x, max_x)
#
#         except Exception as e:
#             if type(e) == AttributeError:
#                 pass
#             else:
#                 import traceback
#                 print(traceback.format_exc())
#
#     def clearPlot(self):
#         if self.lines is not None:
#             for id_, _ in self.structure.elements.items():
#                 self.lines[id_].setData([np.nan], [np.nan])
#
#     def autoscale_trigger(self, state: bool):
#         self.autoscale_flag = state
#
#     def what_r_u(self, event=None, **kwargs):
#         print("I am a Line Graph object based on pyqtgraph with ID: %s" % self.ID)
#
#
# class MPLLineGraph(MPLBasedGraph):
#     lines: Dict[str, Line2D] = None
#     blit: bool = None
#
#     def __init__(self, structure: GraphStructure):
#         super().__init__(structure)
#         self.create_canvas()
#         init_buff = RingBuffer(size_max=10, default_value=0.)
#         self.blit = self.structure.blit
#         self.lines = dict((id_, self._dynamic_ax.plot(init_buff.data, animated=self.blit)[0],) for id_, e in
#                           self.structure.elements.items())
#         if self.blit:
#             arg = list(self.lines.values())
#             self.BM = BlitManager(self.dynamic_canvas, arg)
#
#         for id_, e in self.structure.elements.items():
#             if e.color:
#                 self.lines[id_].set_color(e.color)
#             if e.label:
#                 self.lines[id_].set_label(e.label)
#                 leg = self._dynamic_ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
#                                               ncol=int(len(self.structure.elements) / 2))
#                 self.legend_magic(leg)
#         self.dynamic_canvas.mpl_connect('pick_event', self.on_pick)
#
#         if self.structure.grid:
#             self._dynamic_ax.grid()
#         self.make_zoomable()
#         self.update_signal.connect(self.updatePlot)
#         self.autoscale_signal.connect(self.autoscale_trigger)
#         self.dynamic_canvas.figure.autofmt_xdate()
#
#     def legend_magic(self, legend):
#         if legend:
#             legend.set_draggable(state=True, use_blit=self.blit)
#             self.lined = dict()
#             for legline, origline in zip(legend.get_lines(), self.lines.keys()):
#                 legline.set_picker(True)  # Enable picking on the legend line.
#                 self.lined[legline] = self.lines[origline]
#
#     def on_pick(self, event):
#         # On the pick event, find the original line corresponding to the legend
#         # proxy line, and toggle its visibility.
#         legline = event.artist
#         origline = self.lined[legline]
#         print(self.lined)
#         visible = not origline.get_visible()
#         origline.set_visible(visible)
#         # Change the alpha on the line in the legend so we can see what lines
#         # have been toggled.
#         legline.set_alpha(1.0 if visible else 0.2)
#         self._dynamic_ax.figure.canvas.draw()
#
#     def updatePlot(self, data: LineGraphData):
#         try:
#             xs, ys = data.x_Data, data.y_Data
#             values = list(ys.values())
#             min_y, max_y = np.nanmin(values[0].data), np.nanmax(values[0].data)
#             min_x, max_x = np.nanmin(xs.data), np.nanmax(xs.data)
#             for id_, e in self.structure.elements.items():
#                 y_data = ys.get(id_).data
#                 if y_data is not None:
#                     min_y = np.minimum(min_y, np.nanmin(y_data))
#                     max_y = np.maximum(max_y, np.nanmax(y_data))
#                     self.lines[id_].set_xdata(xs.data)
#                     self.lines[id_].set_ydata(y_data)
#             # self._dynamic_ax.set_xticks(ticks=np.nan_to_num(xs.data[::10]))
#             # loc = plticker.MultipleLocator(base=.1)  # this locator puts ticks at regular intervals
#             # self._dynamic_ax.xaxis.set_major_locator(loc)
#
#             # self.fr_number.fr_number.set_text("frame: {j}".format(j=id_))
#
#             if self.blit:
#                 # print("blitting")
#                 self.BM.update()
#             else:
#                 self._dynamic_ax.figure.canvas.draw()
#             if self.autoscale_flag:
#                 self.set_y_lim(min_y - 0.1 * min_y, max_y * 1.1)
#             self.set_x_lim(min_x - min_x * 0.1, max_x * 1.1)
#
#         except Exception as e:
#             if type(e) == AttributeError:
#                 pass
#             else:
#                 import traceback
#                 print(traceback.format_exc())
#
#     def clearPlot(self):
#         if self.lines is not None:
#             for id_, _ in self.structure.elements.items():
#                 self.lines[id_].set_xdata(np.nan)
#                 self.lines[id_].set_ydata(np.nan)
#             if self.blit:
#                 self.BM.update()
#             else:
#                 self._dynamic_ax.figure.canvas.draw()
#
#     def autoscale_trigger(self, state: bool):
#         self.autoscale_flag = state
#
#     def what_r_u(self, event=None, **kwargs):
#         print("I am a Line Graph object based on matplotlib with ID: %s" % self.ID)
# import time
#
# class QTVectorGraph(QTBasedGraph):
#     """ !!!NOTE: Too slow to use. pyqtgraphs doesn't support quivers but offers an arrow item which is too slow to use for a
#     vector graph"""
#     arrows: Dict[str, QTQuiver]
#     update_signal = pyqtSignal([VectorGraphData])
#     def __init__(self, structure: GraphStructure):
#         super().__init__(structure)
#         # self.location_on_the_screen()
#         self.create_canvas()
#         self.arrows = dict((id_, QTQuiver(self._dynamic_ax, e.X, e.Y, np.zeros(e.X.shape), np.zeros(e.X.shape)))
#                            for id_, e in self.structure.elements.items())
#         self.update_signal.connect(self.updatePlot)
#
#     def updatePlot(self, data: VectorGraphData):
#         try:
#             # xs, ys = data.x_Data, data.y_Data
#             us, vs = data.u_Data, data.v_Data
#             for id_, e in self.structure.elements.items():
#                 self.arrows[id_].set_UVC(us, vs)
#         except Exception as e:
#             if type(e) == AttributeError:
#                 pass
#             else:
#                 import traceback
#                 print(traceback.format_exc())
#
# # from scipy.interpolate  import griddata
# class MPLVectorGraph(MPLBasedGraph):
#     arrows: Dict[str, Quiver] = None
#     arrowkeys: Dict[str, QuiverKey] = None
#     lines : Dict[str, Any]
#     blit: bool = None
#     update_signal = pyqtSignal([VectorGraphData]) #overwite the input type
#     counter_q = 0
#     plot_lines = False
#     def __init__(self, structure: GraphStructure):
#         super().__init__(structure)
#         self.create_canvas()
#         init_buff = RingBuffer(size_max=32, default_value=0.)
#         self.blit = self.structure.blit
#         self.init_blit = self.blit
#         norm, cm = self.add_colorBar("copper")
#         # self.arrows = self._dynamic_ax.quiver( self.structure.elements, Y, animated=self.blit))
#         self.arrows = dict((id_, self._dynamic_ax.quiver( e.X, e.Y, np.zeros(e.X.shape),np.zeros(e.X.shape), color= e.color,
#                               cmap=get_cmap("copper"), zorder=e.zorder, scale=e.scale, units= e.units,animated=self.blit)) for id_, e in
#                           self.structure.elements.items())
#
#         self.lines = dict()
#         if self.blit:
#             arg = list(self.arrows.values())
#             self.BM = BlitManager(self.dynamic_canvas, arg)
#         self.make_zoomable()
#         # for id_, e in self.structure.elements.items():
#         #     if e.color:
#         #         self.lines[id_].set_color(e.color)
#         #     if e.label:
#         #         self.lines[id_].set_label(e.label)
#         #         leg = self._dynamic_ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
#         #                                       ncol=int(len(self.structure.elements) / 2))
#         #         self.legend_magic(leg)
#         # self.dynamic_canvas.mpl_connect('pick_event', self.on_pick)
#         # self.update_signal.connect(self.updateRoutine)
#
#     def add_colorBar(self, map_name:str = "jet"):
#         from matplotlib.cm import get_cmap, ScalarMappable
#         from matplotlib.colors import Normalize
#         import matplotlib.pyplot as plt
#         norm = Normalize()
#         cm= get_cmap(map_name)
#         sm= ScalarMappable(cmap=cm, norm=norm)
#         plt.colorbar(sm, ax=self._dynamic_ax)
#         return norm, cm
#         # self.colorbars = dict( (id_, self._dynamic_ax.colorbar(sm)) for id_, e in self.structure.elements.items() )
#
#     def toggle_lines(self):
#         self.plot_lines = not self.plot_lines
#         self._dynamic_ax.collections = [value for value in self._dynamic_ax.collections if
#                                         type(value) == Quiver]
#         self._dynamic_ax.patches = []
#         if self.init_blit:
#             self.blit = not self.blit
#
#     def updatePlot(self, data):
#         try:
#             # print("updating")
#             xs, ys = data.x_Data, data.y_Data
#             us, vs = data.u_Data, data.v_Data
#             # min_y, max_y = np.nanmin(values[0].data), np.nanmax(values[0].data)
#             # min_x, max_x = np.nanmin(xs.data), np.nanmax(xs.data)
#             for id_, e in self.structure.elements.items():
#                 # y_data = ys.get(id_).data
#                 # if y_data is not None:
#                 #     min_y = np.minimum(min_y, np.nanmin(y_data))
#                 #     max_y = np.maximum(max_y, np.nanmax(y_data))
#                 # angle = np.degrees(np.arctan2(vs[i], us[i]))
#                 # print(angle)
#                 # self.arrows[id_].set_offsets(np.array([xs, ys]).T)
#
#                 if self.plot_lines:
#                     self._dynamic_ax.collections = [value for value in self._dynamic_ax.collections if
#                                                     type(value) == Quiver]
#                     self._dynamic_ax.patches = []
#                     # xi = [np.linspace(min(x_), max(x_), 100) for x_ in xs]
#                     # yi = [np.linspace(min(y_), max(y_), 100) for y_ in xs]
#                     # xi, yi = [], []
#                     # for x_, y_ in zip(xs, ys):
#                     #     xi.append(np.linspace(min(x_), max(x_), 100))
#                     #     yi.append(np.linspace(min(y_), max(y_), 100))
#                     # ui = griddata((xs, ys), us, (xs, ys), method='cubic')
#                     # vi = griddata((xs, ys), vs, (xs, ys), method='cubic')
#
#                     # xi, yi = np.meshgrid()
#                     self.lines[id_] = self._dynamic_ax.streamplot(xs, ys, us, vs, color="b",
#                                                                   zorder=e.zorder)
#                 self.arrows[id_].set_UVC(us, vs, np.hypot(us, vs))
#
#
#
#             if self.blit:
#                 self.BM.update()
#             else:
#                 self._dynamic_ax.figure.canvas.draw()
#             print(time.time())
#             # ax =self.dynamic_canvas.getAxis('bottom')
#             # ax.setTicks([[(v, "%.1f" % v) for v in np.nan_to_num(xs.data[::10])]])
#             # if self.autoscale_flag:
#             #     self.set_y_lim(min_y - 0.1 * min_y, max_y * 1.1)
#             # self.set_x_lim(min_x, max_x)
#             # print(min_x, max_x)
#
#         except Exception as e:
#             if type(e) == AttributeError:
#                 pass
#             else:
#                 import traceback
#                 print(traceback.format_exc())
# # class MPLScatterGraph(MPLBasedGraph):
# #     def __init__(self, structure: GraphStructure, identicalBubbles=True):
# #         super().__init__(structure)
# #         self.create_canvas()
# #         init_buff = RingBuffer(10)
# #         if identicalBubbles:
# #             self.scatter = dict(
# #                 (id_, self._dynamic_ax.plot(init_buff.data, init_buff.data, marker='o')[0],) for id_, e in
# #                 self.structure.elements.items())
# #         else:
# #             self.scatter = dict((id_, self._dynamic_ax.scatter(init_buff.data, init_buff.data),) for id_, e in
# #                                 self.structure.elements.items())
# #             # self.scatter = self._dynamic_ax.scatter(init_buff.data, init_buff.data)
# #         # self.lines = dict((id_, self._dynamic_ax.scatter(init_buff.data, init_buff.data)[0],) for id_, e in
# #         #                   self.structure.elements.items())
# #
# #         for id_, e in self.structure.elements.items():
# #             if e.label:
# #                 self.scatter[id_].set_label(e.label)
# #             if e.color:
# #                 self.lines[id_].set_color(e.color)
# #         self.update_signal.connect(self.updatePlot)
#
#
# class BaseFactory(ABC):
#     """Factory that creates a customised graph object. the factory is not the owner of the objects
#     and they need to be maintained by the user"""
#
#     @abstractmethod
#     def get_mpl_graph(self, setup: GraphStructure) -> BaseGraphCanvas:
#         """returns a graph object based on matplotlib"""
#         pass
#
#     @abstractmethod
#     def get_qt_graph(self, setup: GraphStructure) -> BaseGraphCanvas:
#         """returns a graph object based on QtGraphs"""
#         pass
#
#     @abstractmethod
#     def get_mayavi_graph(self, setup: GraphStructure) ->BaseGraphCanvas:
#         """return a graph object 3D based on mayavi and VTK"""
#         pass
#
#
# class LineGraphFactory(BaseFactory):
#     """Factory that creates a customised line graph object. the factory is not the owner of the objects
#        and they need to be maintained by the user"""
#
#     def get_mpl_graph(self, setup: GraphStructure) -> MPLLineGraph:
#         return MPLLineGraph(structure=setup)
#
#     def get_qt_graph(self, setup: GraphStructure) -> QTLineGraph:
#         return QTLineGraph(structure=setup)
#
#     def get_mayavi_graph(self, setup: GraphStructure) ->BaseGraphCanvas:
#         pass
#
#
# # class ScatterGraphFactory(BaseFactory):
# #     """Factory that creates a customised line graph object. the factory is not the owner of the objects
# #        and they need to be maintained by the user"""
# #
# #     def get_mpl_graph(self, setup: GraphStructure, identicalBubbles: bool = True) -> BaseGraphCanvas:
# #         scatterGraph = MPLScatterGraph(structure=setup, identicalBubbles=identicalBubbles)
# #         # scatterGraph.create_canvas()
# #         return scatterGraph
# #
# #     def get_qt_graph(self, setup: GraphStructure) -> BaseGraphCanvas:
# #         pass
#
# class VectorGraphFactory(BaseFactory):
#     """Factory that creates a customised line graph object. the factory is not the owner of the objects
#        and they need to be maintained by the user"""
#
#     def get_mpl_graph(self, setup: GraphStructure) -> MPLLineGraph:
#         return MPLVectorGraph(structure=setup)
#
#     def get_qt_graph(self, setup: GraphStructure) -> None:
#         raise LibraryDoesntSupportException(ID="..", obj=setup, message="PyqtGraphs doesn't support vector graphs")
#
#     def get_mayavi_graph(self, setup: GraphStructure) ->BaseGraphCanvas:
#         pass
#
#
# if __name__ == "__main__":
#     from PyQt5.QtWidgets import QApplication
#     from PyQt5.QtCore import QTimer
#     from PyQt5.QtWidgets import QApplication
#
#     global counter
#     counter = 0
#     import sys
#     def click_callback(event, graph_, timer):
#         if event.dblclick:
#             print("double_click")
#             graph_.toggle_lines()
#         else:
#             timer.start(100)
#
#     def preprocess_Test(data: VectorGraphData):
#         # for i, d in enumerate(data.u_Data):
#             data.v_Data = -1*data.v_Data
#
#     def test(graph_):
#         global counter
#         GraphData.u_Data = np.cos(GraphData.x_Data + counter * 0.1)
#         GraphData.v_Data = np.sin(GraphData.y_Data + counter * 0.1)
#         # GraphData.x_Data.append(np.random.random(32))
#         # GraphData.y_Data.append(np.random.random(32))
#         # GraphData.u_Data.append(np.random.random(32))
#         # GraphData.v_Data.append(np.random.random(32))
#         # print(GraphData.x_Data.data)
#         counter += 1
#         # for id, d in GraphData.y_Data.items():
#         #     d.append(np.random.random(1))
#         #     print(id, d.data)
#         # d = dict(g1=dict(y=list(np.random.randint(0, 10, size=10)), x=list(np.arange(0, 10))),
#         #          g2=dict(y=list(np.random.randint(0, 10, size=10)), x=list(np.arange(0, 10))))
#         # print(GraphData)
#         graph_.update_signal.emit(GraphData)
#
#
#     gsF = GraphStructureFactory()
#     ElementStructure = gsF.get_sub_objects()
#     GraphStructure = gsF.get_main_object()
#
#     # for i in range(100):
#     #     dummy[str(i)] = es(X=)
#     # X, Y = np.mgrid[:2 * np.pi:10j, :2 * np.pi:5j]
#     X = np.linspace(0, 2 * np.pi, 30)
#     Y = np.linspace(0, 2 * np.pi, 30)
#     X, Y = np.meshgrid(X,Y)
#     # print(X.shape)
#     setup_ = GraphStructure(elements=dict(quiv=ElementStructure(X=X, Y=Y, color="r")),blit=True)
#
#     pdF = VectorGraphDataFormatFactory()
#     VectorGraphData = pdF.get_main_object()
#     # rb = pdF.get_sub_objects()["RingBuffer"]
#     GraphData = VectorGraphData(x_Data=X, y_Data=Y, u_Data=np.cos(X), v_Data=np.sin(Y))
#
#     factory = VectorGraphFactory()
#
#     qapp = QApplication(sys.argv)
#     graph = factory.get_mpl_graph(setup_)
#
#
#     # graph.make_zoomable()
#
#     t = QTimer()
#     t.timeout.connect(lambda: test(graph))
#     graph.set_onclicked_callback(lambda event: click_callback(event, graph, t))
#     # graph.add_preprocess(print)
#     graph.add_preprocess(preprocess_Test)
#
#     graph.show()
#
#     qapp.exec_()
