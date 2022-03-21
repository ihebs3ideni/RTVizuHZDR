# from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
# from PyQt5.QtNetwork import QHostAddress, QTcpSocket
# import socket
#
# class QtClient(object):
#     def __init__(self, Host, port, controller=None):
#         # super().__init__()
#         self.HOST, self.PORT = Host, port
#         self.controller = controller
#         if Host is None:
#             raise Exception("Host is not defined")
#         if port is None:
#             raise Exception("PORT is not defined")
#         self.tcpSocket = QTcpSocket()
#         if self.controller:
#             self.tcpSocket.connected.connect(self.controller.handle_connect)
#             self.tcpSocket.disconnected.connect(self.controller.handle_disconnect)
#             self.tcpSocket.readyRead.connect(self.controller.handle_receive)
#             self.tcpSocket.error.connect(self.controller.handle_error)
#         else:
#             self.tcpSocket.connected.connect(self.handle_connect)
#             self.tcpSocket.disconnected.connect(self.handle_disconnect)
#             self.tcpSocket.readyRead.connect(self.handle_receive)
#             self.tcpSocket.error.connect(self.handle_error)
#         self.blockSize = 0
#
#     def write(self, data):
#         self.tcpSocket.write(data)
#
#     def connection_state(self):
#         return self.tcpSocket.state()
#
#     def close(self):
#         self.tcpSocket.close()
#
#     def disconnect(self):
#         print("Disconnecting")
#         try:
#             print(self.tcpSocket.bytesAvailable())
#             if self.connection_state() == self.tcpSocket.ConnectedState:
#                 self.tcpSocket.close()
#             else:
#                 print("No connection to close")
#         except Exception as e:
#             print("ERROR: ",e)
#
#     def make_connection(self):
#         if self.tcpSocket.state() != self.tcpSocket.ConnectedState:
#             self.tcpSocket.connectToHost(self.HOST, self.PORT, QIODevice.ReadWrite)
#             if(self.tcpSocket.waitForConnected(1000)):
#                 # self.tcpSocket.setsockopt(
#                 #     socket.SOL_SOCKET, socket.SO_REUSEADDR,
#                 #     self.tcpSocket.getsockopt(socket.SOL_SOCKET,
#                 #                            socket.SO_REUSEADDR) | 1
#                 # )
#                 self.tcpSocket.write(b"hello server sir")
#                 print(self.tcpSocket.state())
#             else:
#                 print("Connection failed")
#         else:
#             print("Already connected")
#
#     def handle_connect(self):
#         print("Testing connection callback")
#
#     def handle_disconnect(self):
#         print("disconnected")
#         # self.tcpSocket.write(b"Testing disconnection callback")
#         self.disconnect()
#
#     def handle_receive(self):
#         try:
#             data = self.tcpSocket.readAll()
#             # instr = QDataStream(self.tcpSocket)
#             # instr.setVersion(QDataStream.Qt_5_0)
#             # if self.blockSize == 0:
#             #     if self.tcpSocket.bytesAvailable() < 2:
#             #         return
#             #     self.blockSize = instr.readUInt16()
#             # if self.tcpSocket.bytesAvailable() < self.blockSize:
#             #     return
#             # # Print response to terminal, we could use it anywhere else we wanted.
#             print(str(data, encoding='ascii'))
#             # self.tcpSocket.write(data)
#         except Exception as e:
#             print("ERROR: ",e)
#
#     def handle_error(self, socketError):
#         pass
#
#
#
# if __name__=="__main__":
#     import sys
#     from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QHBoxLayout
#
#     class Test_app(QDialog):
#         def __init__(self):
#             super().__init__()
#             self.c = QtClient("192.168.215.17", 8000)
#             self.button1 = QPushButton("Connect")
#             self.button2 = QPushButton("Disconnect")
#             self.button3 = QPushButton("Send")
#             hbox = QHBoxLayout()
#             hbox.addWidget(self.button1)
#             hbox.addWidget(self.button2)
#             hbox.addWidget(self.button3)
#             self.setLayout(hbox)
#             self.button1.clicked.connect(self.c.make_connection)
#             self.button2.clicked.connect(self.c.disconnect)
#             self.button3.clicked.connect(lambda: self.c.tcpSocket.write(b"echo Test"))
#
#     app = QApplication(sys.argv)
#     a = Test_app()
#     sys.exit(a.exec_())