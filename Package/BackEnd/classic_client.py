# import asyncore, socket
# from builtins import OSError
# from time import sleep
# from threading import Thread
# from queue import Queue
# import traceback
# import logging
# from Package.BackEnd.Pause_Play_Protocol import PPP
#
# class ClassisClient(asyncore.dispatcher, PPP):
#     def __init__(self, host, port, interval = 1):
#         asyncore.dispatcher.__init__(self)
#         PPP.__init__(self,True)
#         self.host = host
#         self.port = port
#
#
#
#     def makeConnection(self):
#         try:
#             self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
#             print("socket_created")
#             self.socket.settimeout(1000)
#             self.connect((self.host, self.port))
#             self.set_reuse_addr()
#             return self.connected #connection status
#         except OSError:
#             print("connection Failed")
#             return False #connection not made successfully
#
#
#     def disconnect(self):
#         if self.connected:
#             self.close()
#
#
#     def infinteLoop(self):
#         try:
#             asyncore.loop()
#         except OSError:
#             pass
#
#
#     def requestStatut(self):
#         if self.connected:
#             s = "connected"
#         else:
#             s = "disconnected"
#         r = "Connection to %s on port %d: %s" %  (self.host, self.port, s)
#         return str(r)
#
#     def handle_connect(self):
#         print('connection made')
#         sent = self.send(self.__hi)
#
#
#     def handle_close(self):
#         print("closed")
#
#
#     def handle_error(self):
#         print("handle error")
#         logging.error(traceback.format_exc())
#
#     def handle_read(self):
#         try:
#             rcv = self.recv(10*1024**2)
#             print(rcv.decode())
#             self.send(rcv)
#
#         except Exception  as e:
#             print("ERROR: ",e)
#
#
#
#     def writable(self):
#         pass
#         # return (len(self.buffer) > 0)
#
#     def handle_write(self):
#         pass
