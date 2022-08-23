from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Callable, Optional

from PyQt5.QtNetwork import QHostAddress, QTcpSocket
import asyncore, socket, traceback

from Package.HelperTools.ExcThread import EventLoopThread, ThreadBaseException


class ClientBaseException(Exception):
    """Base High level expection to notify user to errors in client related duties"""

    def __init__(self, error, message: str):
        self.error = error
        self.message: str = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error.__repr__())


class MakingConnectionException(ClientBaseException):
    """High level expection raised when the connection can't be established"""
    pass


class EventloopException(ClientBaseException):
    """High level expection raised when the event loop can't be started"""
    pass


class ConnectionLostException(ClientBaseException):
    """High level expection raised when the event loop can't be started"""
    pass


@dataclass
class BaseTcpClient(ABC):
    """a base class to define the interface of the tcp clients"""
    host: str
    port: int
    connection_callback: Callable = lambda **kwargs: print("Connection callback triggered")
    disconnection_callback: Callable = lambda **kwargs: print("Disconnection callback triggered")
    receive_callback: Callable = lambda **kwargs: print("Received callback triggered")
    error_callback: Callable = lambda **kwargs: exec(
        'raise ClientBaseException(error=None,message=traceback.format_exc())')
    readBufferSize: int = 10 * 1024 ** 2
    is_free: bool = True

    def __enter__(self):
        # ttysetattr etc goes here before opening and returning the file object
        return self

    def __exit__(self, type, value, traceback):
        # Exception handling here
        self.close_connection()

    def on_connect(self, callback: Callable):
        """responsible for setting a callback on connection established"""
        self.connection_callback = callback

    def on_disconnect(self, callback: Callable):
        """responsible for setting a callback on connection closed"""
        self.disconnection_callback = callback

    def on_receive(self, callback: Callable):
        """responsible for setting a callback on data received"""
        self.receive_callback = callback

    def on_error(self, callback: Callable):
        self.error_callback = callback

    def set_readBufferSize(self, size: int) -> None:
        """responsible for setting the size the the receiving buffer"""
        self.readBufferSize = size

    @abstractmethod
    def get_raw_socket(self) -> socket.socket:
        """getter for the raw socket in case needed"""
        pass

    @abstractmethod
    def write(self, data: str):
        """responsible for sending data over the connection"""
        pass

    @abstractmethod
    def create_connection(self, host=None, port=None):
        """responsible for creating the connection"""
        pass

    @abstractmethod
    def close_connection(self):
        """responsible for closing the connection"""
        pass

    @abstractmethod
    def isConnected(self) -> bool:
        """retrurn connection status"""
        pass


import asyncore, socket, traceback
from builtins import OSError
from threading import Thread


class AsyncTCP_Client(BaseTcpClient, asyncore.dispatcher):
    """Client class based on the asyncore event based client and adhering the the interface set in BaseTcpClient.
    This class needs to be instantiated within an asyncore event loop"""

    def __init__(self, host: str, port: int):
        asyncore.dispatcher.__init__(self)
        self.host, self.port = host, port


    def create_connection(self, host=None, port=None):
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        try:
            if not self.connected:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(1000)
                self.connect((self.host, self.port))
                self.set_reuse_addr()
        except OSError:
            raise MakingConnectionException(self.socket, "Connection to the server couldn't be established")

    def close_connection(self):
        if self.connected:
            self.close()

    def handle_error(self):
        # print("from error handler: ",self.connected)
        # self.error_callback(self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))
        raise ClientBaseException(error=self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR),
                            message=traceback.format_exc())

    def write(self, data: str):
        self.send(bytes(data, "ascii"))

    def handle_connect(self):
        self.connection_callback()

    def handle_close(self):
        print("from close handler: ",self.connected)
        self.disconnection_callback()

    def handle_read(self):
        raw_data = self.recv(self.readBufferSize)
        self.receive_callback(raw_data)

    def handle_write(self):
        pass

    # def handle_expt(self):
    #     raise ClientBaseException(error=self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR),
    #                               message="An unidentified Error has occured. Check Socket Exceptions for more details.")

    def isConnected(self) -> bool:
        return self.connected

    def get_raw_socket(self):
        return self.socket

    def start_event_loop(self, threaded: bool = False) -> Optional[Thread]:
        try:
            if threaded:
                t = EventLoopThread(name="ASYNCORE Event loop", target=asyncore.loop, daemon=True)
                t.start()
                return t
            else:
                asyncore.loop()
        except OSError as e:
            raise EventloopException(error=e, message="Asyncore Event Loop could't be started")


from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpSocket, QAbstractSocket


class QT_TCPClient(BaseTcpClient):
    """Client class based on the QT event system and adhering the the interface set in BaseTcpClient.
        This class needs to e instantiated inside a QApplication event loop """
    def __init__(self, host: str, port: int):
        self.host, self.port = host, port
        self.socket = QTcpSocket()
        self.fragments = []
        self.socket.connected.connect(self.handle_connect)
        self.socket.disconnected.connect(self.handle_close)
        self.socket.error.connect(self.handle_error)
        self.socket.readyRead.connect(self.handle_read)
        # self.msg_received.connect(self.receive_callback)

    def handle_connect(self):
        self.connection_callback()

    def handle_close(self):
        self.disconnection_callback()

    #
    def handle_read(self):
        raw_data = self.socket.readAll()
        self.fragments.append(raw_data)
        if raw_data.endsWith(b'\n'):
            self.receive_callback(b''.join(self.fragments))
            self.fragments.clear()



    #
    def on_error(self, callback: Callable):
        self.socket.error.connect(callback)

    def handle_error(self, socketError):
        self.error_callback(socketError)
        # raise ClientBaseException(error=socketError,message="A socket related error has occured")

    def isConnected(self) -> bool:
        """returns True if connected and False otherwise"""
        return self.socket.state() == self.socket.ConnectedState

    def state(self) -> QAbstractSocket.SocketState:
        if self.socket is not None:
            return self.socket.state()

    def create_connection(self, **kwargs):
        try:
            if not self.isConnected():
                self.socket.connectToHost(self.host, self.port, QIODevice.ReadWrite)
                # self.socket.waitForConnected(1000)
                # if self.socket.waitForConnected(1000):
                #     print("connection made")
                # else:
                #     print("Connection request timed out")
                #     raise MakingConnectionException(self.socket, "Connection request timed out")
            else:
                print("Already connected")
        except OSError:
            raise MakingConnectionException(self.socket, "Connection to the server couldn't be established")



    def close_connection(self):
        if self.isConnected():
            self.socket.close()

    def write(self, data: str):
        self.is_free = False
        self.socket.write(bytes(data, "ascii"))
        self.is_free = True

    def get_raw_socket(self):
        return self.socket


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QHBoxLayout


    class Test_app(QDialog):
        def __init__(self):
            super().__init__()
            self.c = QT_TCPClient("localhost", 5400)

            self.c.on_connect(self.handle_connect)
            self.c.on_disconnect(self.handle_disconnect)
            self.c.on_receive(self.handle_receive)
            self.c.on_error(self.c.handle_error)
            self.button1 = QPushButton("Connect")
            self.button2 = QPushButton("Disconnect")
            self.button3 = QPushButton("Send")
            hbox = QHBoxLayout()
            hbox.addWidget(self.button1)
            hbox.addWidget(self.button2)
            hbox.addWidget(self.button3)

            self.setLayout(hbox)
            self.button1.clicked.connect(self.c.create_connection)
            self.button2.clicked.connect(self.c.close_connection)
            self.button3.clicked.connect(lambda: self.c.write("echo Test"))

        def handle_connect(self):
            print("Testing connection callback")

        def handle_disconnect(self):
            print("disconnected")
            # self.tcpSocket.write(b"Testing disconnection callback")
            self.c.close_connection()

        def handle_receive(self, data):
            try:
                # instr = QDataStream(self.tcpSocket)
                # instr.setVersion(QDataStream.Qt_5_0)
                # if self.blockSize == 0:
                #     if self.tcpSocket.bytesAvailable() < 2:
                #         return
                #     self.blockSize = instr.readUInt16()
                # if self.tcpSocket.bytesAvailable() < self.blockSize:
                #     return
                # # Print response to terminal, we could use it anywhere else we wanted.
                print(str(data, encoding='ascii'))
                # self.tcpSocket.write(data)
            except Exception as e:
                print("ERROR: ", e)


    app = QApplication(sys.argv)
    a = Test_app()
    sys.exit(a.exec_())
