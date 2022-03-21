import asyncore
from threading import Thread
from typing import Callable
from Package.DataStructures.requestBody import *
import numpy as np

class EchoHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, callbacks):
        self.callbacks = callbacks
        super().__init__(sock)
        self.time_series = list(range(10))
        struct = {"Status": {"code": 100, "message": "No Errors"},
                  "Body": {"metaData": {"comment": "This data is generated just for plot testing purposes",
                                        "dataNature": "Mannually generated Data"},
                           "data": {
                               "dataSize": 10,
                               "timesteps": list(np.arange(0,1,0.1)),
                               "channels": {
                                   "channel_1": {"real": list(np.random.random(10)),
                                                  "imag": list(np.random.random(10))},
                                   "channel_2": {"real": list(np.random.random(10)),
                                                  "imag": list(np.random.random(10))},
                                   "channel_3": {"real": list(np.random.random(10)),
                                                  "imag": list(np.random.random(10))},
                                   "channel_4": {"real": list(np.random.random(10)),
                                                  "imag": list(np.random.random(10))},
                                   "channel_5": {"real": list(np.random.random(10)),
                                                  "imag": list(np.random.random(10))},
                                   "channel_6": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_7": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_8": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_9": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_10": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_11": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_12": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_13": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_14": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_15": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                                   "channel_16": {"real": list(np.random.random(10)),
                                                 "imag": list(np.random.random(10))},
                               }
                           }
                           }
                  }

        self.request = Request.parse_obj(struct)
        self.offset:Dict[str, int] = {id_: np.random.randint(0,50) for id_ in self.request.Body.data.channels.keys()}
        self.callbacks["get"] = self.get_callback


    def get_callback(self, sock, data: str):
        try:
            ts = self.request.Body.data.timesteps
            last_t = ts[-1]
            for i, j in zip(range(10),np.arange(last_t+0.1, last_t+1.1, 0.1)):
                ts[i] = j
            print(ts)
            # ts = list(range(int(t_elem), int(ts[0]+2)))
            chs = self.request.Body.data.channels
            for id_, ch in chs.items():
                chs[id_].real = [np.sin(t+self.offset[id_]) for t in ts]
                chs[id_].imag = [np.sin(t+1++self.offset[id_]) for t in ts]
            sock.send(self.request.json().encode())
            # print(chs)
        except Exception as e:
            print(e)


    def handle_read(self):
        try:

            data = self.recv(8192)
            if data:
                data = data.decode()
                cmd, data = data.split(" ")[0], data.split(" ")[1:]
                cb = self.callbacks.get(cmd, None)
                print("cmd =", cmd)
                if cb is None:
                    self.write("The provided cmd is not recognized")
                else: cb(sock=self.socket, data=" ".join(data))
        except OSError as e:
            print(e)


    def handle_write(self):
        print("writable")
        self.send(b"welcome to my server \n")

    def handle_close(self):
        print("connection closed")
        self.close()

    def write(self, data: str):
        self.send(data.encode("ascii"))


class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.callbacks: dict = dict(echo = lambda sock, data: sock.send(data.encode()))
        self.handlers : Dict[str, EchoHandler] = dict()

    def add_callback(self,cmd:str, callback: Callable):
        self.callbacks[cmd] = callback

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        # sock.send(b"welcome to the test server")
        self.handlers[repr(addr)] = EchoHandler(sock, self.callbacks)

    def callback_test(self,sock, data: str):
       sock.send(data.encode())



    def write(self, data: str):
        self.send(data.encode("ascii"))


if __name__ == "__main__":
    server = EchoServer("localhost", 8000) #"192.168.193.177", 8000
    server.add_callback("Hi", lambda **kwargs: kwargs.get("sock").send(b"hey there partner"))
    asyncore.loop()