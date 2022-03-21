from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QLineEdit, \
    QApplication, \
    QCheckBox, QGridLayout

from Package.FrontEnd.base_graph_api import base_graph
from Package.FrontEnd.matplotlib_based.Embedded_line_graph import MPLGraphWidget
from Package.FrontEnd.qtgraph_based.Embedded_line_graph import QtGraphWidget


class graph_parameters(object):
    ID, TYPE, RefreshTime = None, None, None
    SENSOR_IDS, LABELS, COLORS = [], [], []


class Custom_widgets(QWidget):
    def __init__(self,id_):
        super().__init__()
        self.id = id_
        self.__graphs= dict()
        self.setWindowTitle(self.id)

    def save_as_png(self, filepath):
        self.grab().save(filepath)

    def init_widget(self):

        self.init_layout()
        self.check_back = QCheckBox("Autoscale")
        # self.check_back.
        # self.check_back.setChecked(self.__autoscale)
        self.check_back.toggled.connect(self.autoscale_callback)
        self.label = QLabel("X Range: ")
        self.x_range_input = QLineEdit("----")
        self.x_range_input.returnPressed.connect(self.lineedit_callback)
        self.buttom_layout.addWidget(self.check_back)
        self.buttom_layout.addWidget(self.label)
        self.buttom_layout.addWidget(self.x_range_input)

        # self.x_range_input.returnPressed.connect(lambda: self.set_xRange(int(self.x_range_input.text())))
    @pyqtSlot()
    def autoscale_callback(self):
        for id, graph in self.__graphs.items():
            graph.autoscale_sig.emit(self.check_back.checkState())

    @pyqtSlot()
    def lineedit_callback(self):
        for id, graph in self.__graphs.items():
            graph.set_xRange(int(self.x_range_input.text()))

    def init_layout(self):
        self.grid_layout = QGridLayout()
        self.central_layout = QVBoxLayout()
        self.buttom_layout = QHBoxLayout()
        self.horizontalGroupBox = QGroupBox(self.id)
        self.horizontalGroupBox.setLayout(self.grid_layout)
        self.central_layout.addWidget(self.horizontalGroupBox)
        self.central_layout.addLayout(self.buttom_layout)
        self.setLayout(self.central_layout)

    def add_graph(self, graph_id, graph_obj, y, x):
        self.__graphs[graph_id] = graph_obj
        self.grid_layout.addWidget(self.__graphs[graph_id], y, x)
        return graph_obj

    def add_stretch(self, x, y):
        self.grid_layout.setColumnStretch(x, y)

    def get_graph(self, graph_id):
        return self.__graphs.get(graph_id, None)


class HZDR_ENGINE(QMainWindow):
    def __init__(self, grid_dimensions: tuple):
        super().__init__()
        self.__menus = dict()
        # self.__widgets = dict()
        self.__buttons = dict()
        self.__layouts = dict()
        self.__supported_layout= dict(h=QHBoxLayout,v=QVBoxLayout)
        self.__supported_line_graph = dict(qt= QtGraphWidget, mpl=MPLGraphWidget)
        self.__supported_graph_types = dict(line= self.__supported_line_graph["qt"])
        # self.MAIN_WIDGET = QWidget()
        # self.setCentralWidget(self.MAIN_WIDGET)
        self._graphs = dict()
        self.__widgets = dict(main=QWidget())
        self.setCentralWidget(self.__widgets["main"])
        print("supported graphs are: ", self.__supported_graph_types)
        """
        graph_dict ={"type: , "graph_ids": , "sensor_ids": , yLim=update_interval, labels, colors, xLim,
                 backgroundStyle }"""
    def create_new_widget(self, id,  **kwargs):
        self.__widgets[id] = Custom_widgets(id)
        self.__widgets[id].init_widget()

    """ kwargs keys: "update_interval", "labels", "colors", "timer_callback", "onclick_callback"
                    "onclick_callback_args", "timer_callback_args",backgroundStyle """
    def add_graph_to_widget(self, widget_id, graph_id, graph_type,Sensor_ids, y_pos, x_pos, **kwargs):
        refresh_rate = kwargs.get("update_interval", None)
        labels = kwargs.get("labels", None)
        colors = kwargs.get("colors", None)
        onclick_callback = kwargs.get("onclick_callback", None)
        onclick_callback_args = kwargs.get("onclick_callback_args", None)
        timer_callback = kwargs.get("timer_callback", None)
        timer_callback_args = kwargs.get("timer_callback_args", None)
        backgroundStyle = kwargs.get("backgroundStyle", None)
        graph = self.__widgets[widget_id].add_graph(graph_id, self.__supported_graph_types[graph_type](graph_id, Sensor_ids,
                                                                                                       refresh_rate, labels,
                                                                                                       colors), y_pos, x_pos)
        if onclick_callback:
            graph.set_onclicked_callback(lambda event:onclick_callback(event, onclick_callback_args))
        if timer_callback:
            graph.set_timer_Callback(lambda event: timer_callback(event, timer_callback_args))
        return graph

    """kwargs: "nature": timer, clicked.., "graph_obj": reference to the current graph object """
    def set_graph_callbacks(self, widget_id, graph_id, callback, **kwargs):
        callback_nature = kwargs.get("nature", None)
        kwargs["graph_obj"] = self.__widgets[widget_id].get_graph(graph_id)
        if str(callback_nature).lower() == "timer":
            self.__widgets[widget_id].get_graph(graph_id).set_timer_Callback(callback, **kwargs)
        if str(callback_nature).lower() == "clicked":
            self.__widgets[widget_id].get_graph(graph_id).set_onclicked_callback(callback, **kwargs)

    def start_graph_timer(self,widget_id, graph_id, interval=None):
        self.__widgets[widget_id].get_graph(graph_id).start_Timer(interval)



    def add_layout(self, id, type):
        try:
            self.__layouts[id] = self.__supported_layout[type]()
            return self.__layouts[id]
        except Exception as e:
            print("ERROR ADDING LAYOUT: ", e)

    def add_Widget_to_layout(self,layout_id, widget_id =None, button_id=None):
        if widget_id:
            self.__layouts[layout_id].addWidget(self.__widgets[widget_id])
        if button_id:
            self.__layouts[layout_id].addWidget(self.__buttons[button_id])

    def add_stretch(self, layout):
        if type(layout) is str:
            self.__layouts[layout].addStretch()
        else:
            layout.addStretch()

    def set_main_layout(self, layout):
        # if type(layout) is str:
            self.__widgets["main"].setLayout(self.__layouts[layout])
        # else:
        #     self.centralWidget().setLayout(layout)


    def add_button(self, id, name:str, callback):
        try:
            self.__buttons[id] = QPushButton(name)
            self.__buttons[id].clicked.connect(callback)
            return self.__buttons[id]
        except Exception as e:
            print("ERROR ADDING BUTTON: ", e)



    def add_line_graph(self, id, callback=None, type="qt")->base_graph:
        # def clk_callback(event):
        #     print("clicked")
        id_ = "line_graph_"+str(id)
        self._graphs[id_] = self.__supported_line_graph[type](id_, [0, 1, 2], 100, colors=['r', 'g', 'b'])
        # self.__menu_dict[id].set_xRange(100)
        self._graphs[id_].set_onclicked_callback(callback)
        return self._graphs["line_graph_"+str(id)]


    def render_graphs(self):
        for key, value in self.__widgets.items():
            print("key:", key,  "status:", value.show())


    def get_widget(self, id_):
        return self.__widgets[id_]

    def export(self):
        for k, wid in self.__widgets.items():
            print("Tests/"+str(k)+".png")
            if k != "main":
                wid.save_as_png("D:\HZDR\HZDR_VISU_TOOL\Tests\\"+str(k)+".png")



if __name__ == "__main__":
    import sys
    import numpy as np
    import time
    import threading
    from Package.DataStructures.RingBuffer import RingBuffer

    global lock
    lock = threading.Lock()
    graph_data = []
    for i in range(2):
        graph_data.append(dict(x={0: RingBuffer(100), 1: RingBuffer(100), 2: RingBuffer(100)},
                      y={0: RingBuffer(100), 1: RingBuffer(100), 2: RingBuffer(100)}))
        for j in range(3):
            graph_data[i]["x"][j].append(0)
            graph_data[i]["y"][j].append(1)


    def generator():
        while (1):
            with lock as l:
                for j in range(2):
                    for i in range(3):
                        graph_data[j]["x"][i].append(graph_data[j]["x"][i][0] + 1)
                        graph_data[j]["y"][i].append(np.random.randint(0, 10))
            time.sleep(0.5)

    def test_callback(event, **kwargs):
        index = kwargs.get("index", 0)
        graph_obj = kwargs.get("graph_obj", 0)
        with lock as l:
            data = graph_data[index]
            graph_obj.update_signal.emit(data)

    def connect_callback():
        if not gn_thread.is_alive():
            gn_thread.start()

    gn_thread = threading.Thread(target=generator, daemon=True)
    qapp = QApplication(sys.argv)
    app = HZDR_ENGINE((1,1))
    h_layout = app.add_layout("first", "h")
    app.set_main_layout("first")
    app.add_stretch("first")
    app.add_button("start", "Start", app.render_graphs)
    app.add_button("connect", "Connect", connect_callback)
    app.add_button("save", "SAVE", app.export)
    app.add_Widget_to_layout("first", button_id="start")
    app.add_Widget_to_layout("first", button_id="connect")
    app.add_Widget_to_layout("first", button_id="save")

    app.create_new_widget("1")
    graph = app.add_graph_to_widget("1", "test", "line", [0,1,2], 0,0, labels=["ch0", "ch1", "ch2"], colors=["r", "g", "b"])


    app.add_graph_to_widget("1", "test2", "line", [0,1,2], 1,0)
    app.set_graph_callbacks("1", "test", test_callback, nature= "clicked", index=1)

    app.set_graph_callbacks("1", "test2", test_callback, nature= "timer", index=0)
    app.start_graph_timer("1", "test2", 100)

    app.create_new_widget("2")
    app.add_graph_to_widget("2", "test", "line", [0, 1, 2], 0, 0, labels=["ch0", "ch1", "ch2"],
                                    colors=["r", "g", "b"])
    app.add_graph_to_widget("2", "test2", "line", [0, 1, 2], 1, 0)

    app.set_graph_callbacks("2", "test2", test_callback, nature= "clicked", index=1)

    app.set_graph_callbacks("2", "test", test_callback, nature= "timer", index=0)
    app.start_graph_timer("2", "test", 100)

    app.show()
    qapp.exec_()