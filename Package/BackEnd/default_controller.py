from Package.Engine.AppEngine import HZDR_ENGINE
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot
import PyQt5
from abc import abstractmethod, ABC


class BaseController(ABC):
    pass


class AppController(PyQt5.QtCore.QObject):
    connect_sig = pyqtSignal([int])
    disconnect_sig = pyqtSignal([int])
    FS_sig = pyqtSignal([int])
    data_sig = pyqtSignal([int])

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.timer = QTimer()
        self.connect_sig.connect(self.handle_connect)
        self.disconnect_sig.connect(self.handle_disconnect)
        self.FS_sig.connect(self.handle_sampling_frequency)
        self.data_sig.connect(self.handle_received_data)

    def run(self):  # make it work with an instance of the class as an argument in init
        import sys
        from PyQt5.QtWidgets import QApplication
        self.qapp = QApplication(sys.argv)
        self.view = self.view()
        self.view.show()
        self.qapp.exec_()

        # self.view.show()

    @pyqtSlot(int)
    def handle_sampling_frequency(self, arg):
        print(arg, "sampling frequency signal handled")

    @pyqtSlot(int)
    def handle_received_data(self, arg):
        print(arg, "received_data signal handled")

    @pyqtSlot(int)
    def handle_disconnect(self, arg):
        print(arg, "disconnect signal handled")

    @pyqtSlot(int)
    def handle_connect(self, arg):
        print(arg, "connect signal handled")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    import numpy as np


    class test_connection(object):
        def __init__(self, controller: AppController):
            self.timer = QTimer()
            self.controller = controller
            self.timer.timeout.connect(self.timer_triggered)

        def timer_triggered(self):
            res = np.random.randint(0, 4)
            dum = res % 4
            if (dum == 0):
                self.controller.connect_sig.emit(res)
            if (dum == 1):
                self.controller.disconnect_sig.emit(res)
            if (dum == 2):
                self.controller.FS_sig.emit(res)
            if (dum == 3):
                self.controller.data_sig.emit(res)

        def start_simulation(self, event, interval):
            if not self.timer.isActive():
                self.timer.start(interval)
            else:
                self.timer.stop()


    qapp = QApplication(sys.argv)

    qwidget = HZDR_ENGINE((1, 1))

    controller = AppController(qwidget)
    connection = test_connection(controller)
    qwidget.add_graph("1", None)
    connection.start_simulation(None, 100)

    qwidget.show()
    qapp.exec_()
