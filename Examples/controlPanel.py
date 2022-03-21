# create Control Panel Class
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QRadioButton, \
    QButtonGroup, QMessageBox
from PyQt5.QtCore import QTimer
from typing import Callable
from Package.BackEnd.TCP_Client import BaseTcpClient


class ControlPanel(QMainWindow):
    """A simpple Control Pannel for basic use.
    !!!!!!ATTENTION!!!!!!: on_close must take no arguments"""
    def __init__(self, connection: BaseTcpClient, init_autoscale: bool = False, on_close: Callable = None):
        super().__init__()
        self.connection: BaseTcpClient = connection
        self.close_callback: Callable = on_close #must take not arguments
        self.setWindowTitle("Visu Control Pannel")
        self.spawn_graphs = QPushButton("Spawn Graphs")
        self.connecting = QPushButton("Connect")
        self.disconnecting = QPushButton("Disconnect")
        self.connection_status = QRadioButton("Connection")
        self.auto_scale = QPushButton("Autoscale")
        self.auto_scale_status: bool = init_autoscale
        self.auto_scale_indicator = QRadioButton("Autoscale")
        self.auto_scale_indicator.setChecked(self.auto_scale_status)

        self.status_refresh_timer = QTimer()
        self.status_refresh_timer.timeout.connect(
            lambda: self.connection_status.setChecked(self.connection.isConnected()))
        self.status_refresh_timer.timeout.connect(lambda: self.auto_scale_indicator.setChecked(self.auto_scale_status))
        self.connecting.clicked.connect(lambda: self.status_refresh_timer.start(100))

        g1 = QButtonGroup(self)
        g1.setExclusive(False)
        g2 = QButtonGroup(self)
        g2.setExclusive(False)
        g1.addButton(self.connection_status)
        g1.addButton(self.connecting)
        g1.addButton(self.disconnecting)
        g2.addButton(self.auto_scale_indicator)
        central_widget = QWidget(self)
        # central_widget.setStyleSheet("""
        #                QWidget {
        #                    border: 20px solid black;
        #                    border-radius: 10px;
        #                    background-color: rgb(1, 1, 1);
        #                    }
        #                """)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.spawn_graphs)
        hbox.addWidget(self.connecting)
        hbox.addWidget(self.disconnecting)
        hbox.addWidget(self.auto_scale)
        hbox1 = QHBoxLayout(self)
        hbox1.addWidget(self.connection_status)
        hbox1.addWidget(self.auto_scale_indicator)
        layout.addLayout(hbox)
        layout.addLayout(hbox1)
        central_widget.setLayout(layout)
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.close_callback:
                self.close_callback()
            event.accept()

        else:
            event.ignore()

    def set_connect_callback(self, callback: Callable):
        self.connecting.clicked.connect(callback)

    def set_disconnect_callback(self, callback: Callable):
        self.disconnecting.clicked.connect(callback)

    def set_autoscale_callback(self, callback: Callable):
        self.auto_scale.clicked.connect(callback)

    def set_spawn_graphs_callback(self, callback: Callable):
        self.spawn_graphs.clicked.connect(callback)

    def set_on_close_callback(self, callback: Callable):
        self.close_callback = callback