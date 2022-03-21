from Package.FrontEnd.CustomizableControlPanel import BaseControlPanel
from Package.FrontEnd.factories import MPLFactory
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.DataStructures.requestBody import Request
from Package.BackEnd.TCP_Client import AsyncTCP_Client, BaseTcpClient, QT_TCPClient
from Package.HelperTools.ExcThread import EventLoopThread
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
import json
from typing import List


# define Backend callback Functions



# def request_data_routine(connection: BaseTcpClient, sampling_frequency: str = 1):
#     """a routine running in a seperate thread that requests data from connection each time interval"""
#     import time
#     refresh_rate = 2000
#     while (True):
#         if connection.isConnected():
#             # print("sample_size= ",sample_size)
#             query = ":DATA? demodulated " + str(1)+"\n"
#             connection.write(query)
#         else:
#             print("No connection established")
#         time.sleep(refresh_rate)


def network_error_callback(error):
    """callback for the error handling in the connection"""
    print("an network error has occured: %s" % repr(error))

def create_graphs()->list:
    # n_graphs = NUMBER_OF_CHANNELS // NUMBER_OF_CHANNELS_PER_GRAPH
    # if n_graphs * NUMBER_OF_CHANNELS_PER_GRAPH < NUMBER_OF_CHANNELS:
    #     n_graphs += 1
    graphs = []
    factory = MPLFactory()
    # for i in range(n_graphs):
    structure = GraphStructure(ID=f"Pegel Viewer {0}", grid=True, blit=True,
                               elements=dict(g1=ElementStructure(X=np.array(range(4)),Y=np.array([0] * 4),
                                                                    color="b", label=f"real ch0-ch3"),
                                             g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                                 color="r", label=f"Imaginary ch0-ch3")
                                             ),)
    graphs.append(factory.get_LevelGraph(structure, spawning_position=1))
    structure = GraphStructure(ID=f"Pegel Viewer {1}", grid=True, blit=True,
                               elements=dict(g1=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                                 color="b", label=f"real ch4-ch7"),
                                             g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                                 color="r", label=f"Imaginary ch4-ch7")))
    graphs.append(factory.get_LevelGraph(structure, spawning_position=2))

    structure = GraphStructure(ID=f"Pegel Viewer {3}", grid=True, blit=True,
                               elements=dict(g1=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                                 color="b", label=f"real ch8-ch11"),
                                             g2=ElementStructure(X=np.array(range(4)), Y=np.array([0] * 4),
                                                                 color="r", label=f"Imaginary ch8-ch11")))
    graphs.append(factory.get_LevelGraph(structure, spawning_position=3))

    structure = GraphStructure(ID=f"Pegel Viewer {4}", grid=True, blit=True,
                               elements=dict(g1=ElementStructure(X=np.array(range(3)), Y=np.array([0] * 3),
                                                                 color="b", label=f"real ch12-ch14"),
                                             g2=ElementStructure(X=np.array(range(3)), Y=np.array([0] * 3),
                                                                 color="r", label=f"Imaginary ch12-ch14")))
    graphs.append(factory.get_LevelGraph(structure, spawning_position=4))
    return graphs

def close_graphs(graph_list):
    for g in graph_list:
        g.close()

def take_screenshot(graph_list, path=r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\screenshots"):
    for g in graph_list:
        g.take_screenshot(path=path)



def main():
    #create connection
    # client = QT_TCPClient

    # create View
    # global request_routine, event_loop

    with QT_TCPClient("localhost", 5400) as client:
        lvl_graphs = create_graphs()
        groups = [range(4), range(4, 8), range(8, 12), range(12, 15)]
        def received_callback(raw_data: bytes):
            """Callback triggered on data received by the connection class"""
            try:
                data = str(raw_data, encoding='ascii')
                # print(data)
                request = Request.parse_obj(json.loads(data)[0])
                for graph, grp in zip(lvl_graphs, groups):
                    r = np.array([request.Body.data.channels[f"channel_{i}"].real for i in grp])
                    im = np.array([request.Body.data.channels[f"channel_{i}"].imag for i in grp])
                    DS = graph.get_data_container()
                    graph.updateFigure(DS(x_Data=dict(g1=np.array(range(len(r))), g2= np.array(range(len(r)))),
                                      y_Data=dict(g1=r, g2=im)))
                    graph.show()

            except Exception as e:
                import traceback
                # print(e.obj)
                print(traceback.format_exc())

        def requesting(timer: QTimer, button):
            if timer.isActive():
                button.setText("Request")
                timer.stop()
                return
            button.setText("Stop")
            timer.start(1000)




        qapp = QApplication(sys.argv)
        # create Control Panel
        cp = BaseControlPanel("Pegel Viewer")
        cp.on_close(lambda: close_graphs(lvl_graphs))
        timer = QTimer()
        timer.timeout.connect(lambda *arg: client.write(":DATA? demodulated 1"))
        connect_b = cp.add_push_button("Connect", (0, 0), callback=client.create_connection)
        init_b = cp.add_push_button("Init", (1, 0), callback=lambda event: client.write("*IDN? demodulated"))
        request_b = cp.add_push_button("Request", (2, 0))
        request_b.clicked.connect(lambda event: requesting(timer, request_b))

        disconnect_b = cp.add_push_button("Disconnect", (3, 0), callback=client.close_connection)
        disconnect_b.clicked.connect(lambda event: request_b.click())

        Connection_status = cp.add_Icon("Connection", r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\no_connection.png",
                                        (1, 1, 2, 1))
        Screenshot_b = cp.add_push_button("Screenshot", (3, 1), lambda event, gs=lvl_graphs: take_screenshot(gs))
        client.on_receive(received_callback)
        client.on_connect(lambda *args: Connection_status.update_Icon(r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\connected.png"))
        client.on_disconnect(lambda *args: Connection_status.update_Icon(r"D:\HZDR\HZDR_VISU_TOOL\Examples\PegelApp\no_connection.png"))
        client.on_error(lambda **kwargs: print(**kwargs))

        cp.show()

    #     graphs = create_graphs()
    #     client.create_connection()
    #     if EVENT_LOOP is None:
    #         EVENT_LOOP = client.start_event_loop(True)
    #     if not EVENT_LOOP.is_alive():
    #         EVENT_LOOP.start()
    #     client.on_connect(lambda data: client.write("*IDN? demodulated\n"))
        # client.on_disconnect(lambda data: client.close_connection())
        # client.on_receive(lambda raw_data: received_callback(raw_data, graphs))
        # client.on_error(network_error_callback)

        qapp.exec_()

if __name__ == "__main__":
    main()
