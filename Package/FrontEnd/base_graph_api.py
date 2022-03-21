# from PyQt5.QtWidgets import QWidget, QGroupBox, QGridLayout, QVBoxLayout, QCheckBox, QHBoxLayout, QLineEdit, QLabel
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import pyqtSlot, pyqtSignal
#
# from abc import abstractmethod, ABC
#
#
# from Package.DataStructures.GraphArgsStructure import GraphStructure
#
# from typing import Dict, List, Optional, Any, Tuple, NamedTuple
# from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot
# from abc import abstractmethod, ABC
# from collections import namedtuple
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
#
#
# class base_graph(QWidget):
#     update_signal = pyqtSignal([dict])
#
#     @abstractmethod
#     def set_onclicked_callback(self, event, callback, **kwargs):
#         pass
#
#     @abstractmethod
#     def set_timer_Callback(self, event, callback, **kwargs):
#         pass
#
#     @abstractmethod
#     def start_Timer(self, interval):
#         pass
#
#     @abstractmethod
#     def set_xRange(self, n):
#         pass
#
#     @abstractmethod
#     @pyqtSlot(dict)
#     def updatePlot(self, data: dict):
#         pass
#
#     def set_title(self, title):
#         self.setWindowTitle(title)
#
#
#
#
#
# class BaseCANVAS(QWidget):
#     """Base class meant to be a base for all widgets"""
#
#     def set_title(self, title: str):
#         """sets the title on the canvas window"""
#         self.setWindowTitle(title)
#
#     def set_icon(self, path: str):
#         """sets the icon on the canvas window"""
#         self.setWindowIcon(QIcon(path))
#
#     @abstractmethod
#     def init_layout(self, **kwargs):
#         """interface method that sets the initial structure and look of the widget"""
#         raise NotImplementedError
#
#     @abstractmethod
#     def init_behavior(self, **kwargs):
#         """interface method that sets the different callbacks and behaviors of the widget"""
#         raise NotImplementedError
#
#     @abstractmethod
#     def create_view(self, **kwargs):
#         """interface method that sets the finalized structure of the view"""
#         raise NotImplementedError
#
#     def save_as_png(self, filepath):
#         self.grab().save(filepath)
#
# class GraphFactory(ABC):
#     """Factory that creates a customised graph object. the factory is not the owner of the objects
#     and they need to be maintined by the user"""
#     # def __init__(self, structure: GraphStructure):
#     #     self.struct = structure
#     @abstractmethod
#     def get_graph_object(self, structure: GraphStructure)->BaseCANVAS:
#         pass
#
# import numpy as np
#
#
# class GraphCANVAS(BaseCANVAS):
#     """Base class meant to be a base for all graph objects"""
#     update_signal = pyqtSignal([dict])
#     autoscale_signal = pyqtSignal([bool])
#     autoscale_box: QCheckBox
#     autoscale_label: QLabel
#     autoscale_x_range_input: QLineEdit
#     Figures: Dict[str, Dict[Any, NamedTuple]]
#     Figures_Layout: QGridLayout
#     Factory: GraphFactory
#
#     # def __init__(self, id_: str, sensorIds: List[Any], labels: Optional[List[str]] = None,
#     #              colors: Optional[List[Any]] = None, update_interval: Optional[int] = None,
#     #              xlim: Tuple[float, float] = (0., 100.), ylim: Tuple[float, float] = (-1, 1)):
#     def __init__(self, id_:str, structure: GraphStructure, factory: GraphFactory):
#         super().__init__()
#         # self.update_signal.connect(self.updatePlot)
#         # self.autoscale_signal.connect(self.autoscale)
#         self.ID: str = id_
#         self.Factory = factory
#         self.structure = structure
#         self.__autoscale = False
#         self.Figures = dict()
#
#     def init_layout(self, **kwargs):
#         # if kwargs.get("Control_Pannel", False) is not None:
#         control_pannel = kwargs.get("Control_Pannel", False)
#         # else:
#         #     self.bottom_layout = QHBoxLayout()
#
#
#         self.Figures_Layout = QGridLayout()
#         self.horizontalGroupBox = QGroupBox(self.ID)
#         self.horizontalGroupBox.setLayout(self.Figures_Layout)
#
#         self.central_layout = QVBoxLayout()
#
#         # self.central_layout.addWidget(QPushButton("TEST"))
#         self.central_layout.addWidget(self.horizontalGroupBox)
#         if control_pannel:
#             self.autoscale_box = QCheckBox("Autoscale")
#             self.autoscale_box.setChecked(self.__autoscale)
#             self.autoscale_box.toggled.connect(lambda: self.autoscale(self.check_back.checkState()))
#             self.autoscale_label = QLabel("X Range: ")
#             default_xrange = kwargs.get("default_xRange", 100)
#             self.autoscale_x_range_input = QLineEdit(str(default_xrange))
#             self.autoscale_x_range_input.returnPressed.connect(lambda: self.set_xRange(int(self.x_range_input.text())))
#             control_box = QHBoxLayout()
#             control_box.addWidget(self.autoscale_box)
#             control_box.addWidget(self.autoscale_label)
#             control_box.addWidget(self.autoscale_x_range_input)
#             self.central_layout.addLayout(control_box)
#         self.setLayout(self.central_layout)
#
#     # def get_control_template(self, default_xrange: int) -> QHBoxLayout:
#     #     self.autoscale_box = QCheckBox("Autoscale")
#     #     self.autoscale_box.setChecked(self.__autoscale)
#     #     self.autoscale_box.toggled.connect(lambda: self.autoscale(self.check_back.checkState()))
#     #     self.autoscale_label = QLabel("X Range: ")
#     #     self.autoscale_x_range_input = QLineEdit(str(default_xrange))
#     #     self.autoscale_x_range_input.returnPressed.connect(lambda: self.set_xRange(int(self.x_range_input.text())))
#     #     hbox = QHBoxLayout()
#     #     hbox.addWidget(self.autoscale_box)
#     #     hbox.addWidget(self.autoscale_label)
#     #     hbox.addWidget(self.autoscale_x_range_input)
#     #     hbox.addChildLayout()
#     #     return hbox
#
#     def add_figure(self, id: str, x: int, y: int, fig: Any = None, ) -> Dict[Any, NamedTuple]:
#         # TODO @iheb Implement a grid layout in the base class an find a way to make it generic
#         if self.Figures.get(id, None) is not None:
#             raise IDConflictException(ID=id, obj=self.Figures.get(id),
#                                       message="An object already exists with the same id")
#         if fig is None:
#             fig = self.create_figure()
#         Coordinates = namedtuple('Coordinates', ['x', 'y'])
#         self.Figures[id] = dict(figure=fig, position=Coordinates(x, y))
#         print(type(self.Figures[id]["figure"]))
#         self.Figures_Layout.addWidget(self.Figures[id]["figure"], x, y)
#         return self.Figures[id]
#
#     def get_autoscale_limites(self, x_data: List[float], y_data: List[float]) -> (float, float, float, float):
#         """
#         :param x_data, y_data:
#         :type x_data, y_data: List[float]
#         """
#         min_y = np.nanmin(y_data)
#         max_y = np.nanmax(y_data)
#         min_x = np.nanmin(x_data)
#         max_x = np.nanmax(x_data)
#         return max_y, min_y, max_x, min_x
#
#     @pyqtSlot(dict)
#     @abstractmethod
#     def updatePlot(self, data: Dict[str, Any]):
#         """Callback slot to be executed when the plot update event is triggered"""
#         pass
#
#     @pyqtSlot(bool)
#     def autoscale(self, state):
#         self.__autoscale = state
#
#     @abstractmethod
#     def clicked(self, event, callback, **kwargs):
#         """Callback to be executed when the canvas clicked event is triggered"""
#         pass
#
#     @abstractmethod
#     def timerCallback(self, event, callback, **kwargs):
#         """Callback to be executed when the timer times out, Only works if the timer has
#         started"""
#         pass
#
#     @abstractmethod
#     def start_Timer(self, interval: int):
#         """starts the timer object"""
#         pass
#
#     @abstractmethod
#     def set_xRange(self, n: int):
#         """setter of the graph window length"""
#         pass
#
#     @abstractmethod
#     def set_yLim(self, y_min: float, y_max: float):
#         """setter of the graph y limites"""
#         pass
#
#     @abstractmethod
#     def create_figure(self)->Any:
#         """returns the default figure overwritten in the child class"""
#         pass
#
#
#
#
#
# if __name__ == "__main__":
#     from PyQt5.QtWidgets import QApplication, QPushButton
#     import sys
#
#     qapp = QApplication(sys.argv)
#     graph = GraphCANVAS(id_="test_graph", sensorIds=[1, 2, 3], labels=["1", "2", "3"])
#     graph.init_layout(Control_Pannel=True, default_xRange=10)
#
#     graph.add_figure("f1", 0,0, QPushButton("Test"))
#     graph.add_figure("f2", 0,1, QPushButton("Test2"))
#     graph.add_figure("f3", 1,0, QPushButton("Test3"))
#     graph.add_figure("f4", 1,1, QPushButton("Test4"))
#     graph.add_figure("f5", 2,0, QPushButton("Test5"))
#     graph.add_figure("f6", 2,1, QPushButton("Test6"))
#     graph.set_title("Test_app")
#     graph.show()
#     qapp.exec_()
