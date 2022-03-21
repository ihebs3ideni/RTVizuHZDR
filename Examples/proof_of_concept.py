from Package.DataStructures.TypeFactory import TypeFactories
from Package.DataStructures.plotDataFormat import LineGraphData
from Package.BackEnd.TCP_Client import AsyncTCP_Client, BaseTcpClient
from Package.FrontEnd.graph_factory import LineGraphFactory, BaseGraphCanvas, QTBasedGraph, MPLBasedGraph
import json
from Package.HelperTools.ExcThread import EventLoopThread
from typing import List

from Examples.controlPanel import ControlPanel

# create data factories
TF = TypeFactories()
graph_Structure_Factory = TF.graphStructureFactory()
request_Structure_Factory = TF.tcpRequestFormatFactory()
Plot_Arg_Factory = TF.linePlotArgFormatFactory()
graph_factory = LineGraphFactory()


# define some callback functions

def received_callback(raw_data: bytes, graphs: List[BaseGraphCanvas], graph_arg: List[LineGraphData]):
    """Callback triggered on data received by the connection class"""
    try:
        # print(str(raw_data, encoding='ascii'))
        global request_routine

        # start a requesting routine to retrieve data from the server

        if request_routine is None:
            data = str(raw_data, encoding='ascii')
            print(data)
            request_routine = EventLoopThread(name="Request Routine Worker", target=request_data_routine,
                                              args=(client, data.split()[0]),
                                              daemon=True)
        if not request_routine.is_alive():
            request_routine.start()
            return
        request = json.loads(raw_data)
        request = request_Structure_Factory.get_main_object().parse_obj(request[0])
        # print(request)
        for i in range(2):
            ga = graph_arg[i]
            graph = graphs[i]
            ga.x_Data.append(request.Body.data.timesteps[::10])
            # for graph in graphs:
            for id, d in ga.y_Data.items():
                s_id = graph.structure.elements.get(id).sensorID
                if request.Body.data.channels.get(s_id) is None:
                    print(s_id)
                else:
                    d.append(request.Body.data.channels.get(s_id).real[::10])
            graph.update_signal.emit(ga)
    except Exception:
        import traceback
        print(traceback.format_exc())


def request_data_routine(connection: BaseTcpClient, sampling_frequency: str):
    """a routine running in a seperate thread that requests data from connection each time interval"""
    import time
    refresh_rate = 4
    # time_base_s = 1/float(sampling_frequency)
    # sample_size = (refresh_rate / (float(sampling_frequency) / 10 ** 9))
    sample_size = refresh_rate * float(sampling_frequency)
    while (True):
        if connection.isConnected():
            # print("sample_size= ",sample_size)
            query = ":DATA? demodulated " + str(sample_size)+"\n"
            connection.send(query.encode())
        else:
            print("No connection established")
        time.sleep(refresh_rate)


def network_error_callback(error):
    """callback for the error handling in the connection"""
    print("an network error has occured: %s" % repr(error))


# create_graph_struct
# SUPPORTED_COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
gs = [
    {"elements": {"l1": {"sensorID": "channel_1", "color": "r", "label": "ch1"},
                  "l2": {"sensorID": "channel_2", "color": "b", "label": "ch2"},
                  "l3": {"sensorID": "channel_3", "color": "g", "label": "ch3"},
                  "l4": {"sensorID": "channel_4", "color": "k", "label": "ch4"},
                  "l5": {"sensorID": "channel_5", "color": "c", "label": "ch5"},
                  "l6": {"sensorID": "channel_6", "color": "m", "label": "ch6"},
                  "l7": {"sensorID": "channel_7", "color": "y", "label": "ch7"},
                  "l8": {"sensorID": "channel_8", "color": "#ff8c00", "label": "ch8"},
                  }, "grid": True, "ID": "g1"},
    {"elements": {"l9": {"sensorID": "channel_9", "color": "r", "label": "ch9"},
                  "l10": {"sensorID": "channel_10", "color": "b", "label": "ch10"},
                  "l11": {"sensorID": "channel_11", "color": "g", "label": "ch11"},
                  "l12": {"sensorID": "channel_12", "color": "k", "label": "ch12"},
                  "l13": {"sensorID": "channel_13", "color": "c", "label": "ch13"},
                  "l14": {"sensorID": "channel_14", "color": "m", "label": "ch14"},
                  # "l15": {"sensorID": "ref_15", "color": "y", "label": "ref15"},
                  }, "ID": "g2", "grid": True, "blit": True}
]

# map the dictionary structure to objects
main_type = graph_Structure_Factory.get_main_object()
from Package.HelperTools.timing_deco import _time
@_time
def create_obj(gs, g):
    return gs.get_main_object().parse_obj(g)

# print(main_type.schema_json())

for i, g in enumerate(gs):
    gs[i] = create_obj(graph_Structure_Factory, g)
    # gs[i] = graph_Structure_Factory.get_main_object().parse_obj(g)
    print(type(gs[i]))
    # gs[i].blit = False

# create_data_structure from graph structure
rb = Plot_Arg_Factory.get_sub_objects()["RingBuffer"]
plot_history = 1000
global graph_Data
graph_Data = []
for g in gs:
    ds = dict()
    for id_, e in g.elements.items():
        ds[id_] = rb(plot_history)
    graph_Data.append(Plot_Arg_Factory.get_main_object()(x_Data=rb(plot_history), y_Data=ds.copy()))

global request_routine, event_loop
request_routine = None
event_loop = None
global graphs
graphs = None

# create connection handler
with AsyncTCP_Client("localhost", 5400) as client:
    from PyQt5.QtWidgets import QApplication
    import sys


    def create_graphsCB(graph_factory: LineGraphFactory):
        """callback for the spawn_graphs button on the control panel"""
        global graphs
        if graphs is None:
            # print(gs[0])
            graphs = [graph_factory.get_qt_graph(gs[0]), graph_factory.get_mpl_graph(gs[1])]
        # setup some graph features
        for graph in graphs:
            if isinstance(graph, QTBasedGraph):
                print("qt")
                graph.add_hLine([0.5,0.6,0.7], linestyle=["dashdot", "dotted", "solid"], color=["r", "g", "b"])
            if isinstance(graph, MPLBasedGraph):
                print("mpl")
                graph.add_hLine([0.5, 0.6, 0.8],xmin=[5,6,7],xmax=[100,101,102], colors=["r", "g", "b"], linestyle=["dashdot", "dotted", "solid"])
            graph.set_onclicked_callback(graph.what_r_u)
            graph.show()


    def closeCB():
        """callback on closing on the control panel"""
        global graphs
        if graphs is not None:
            for graph in graphs:
                graph.close()


    def connectCB():
        """callback for the connect button on the control panel"""
        # clear graphs
        global graphs, graph_Data
        if graphs is not None:
            graph_Data = []
            for g in gs:
                ds = dict()
                for id_, e in g.elements.items():
                    ds[id_] = rb(plot_history)
                graph_Data.append(Plot_Arg_Factory.get_main_object()(x_Data=rb(plot_history), y_Data=ds.copy()))
            for g in graphs:
                g.clearPlot()

        # establish connection and start event loop to handle callbacks
        client.create_connection()

        global event_loop
        if event_loop is None:
            event_loop = client.start_event_loop(True)
        if not event_loop.is_alive():
            event_loop.start()


    def disconnectCB():
        """callback for the disconnect button on the control panel"""
        global event_loop, request_routine
        event_loop, request_routine = None, None
        client.close_connection()


    def autoscaleCB(cp: ControlPanel):
        """callback for the autoscale button on the control panel"""
        global graphs
        if graphs is not None:
            for g in graphs:
                g.toggle_autoscale()
                cp.auto_scale_status = g.autoscale_flag


    try:
        qapp = QApplication(sys.argv)

        # setup control panel
        control_panel = ControlPanel(connection=client, init_autoscale=True)
        control_panel.set_connect_callback(connectCB)
        control_panel.set_disconnect_callback(disconnectCB)
        control_panel.set_autoscale_callback(lambda: autoscaleCB(control_panel))
        control_panel.set_spawn_graphs_callback(lambda: create_graphsCB(graph_factory))
        control_panel.set_on_close_callback(closeCB)

        # setup connection callbacks
        client.on_connect(lambda: client.write("*IDN? demodulated\n"))
        client.on_disconnect(lambda: client.close_connection())
        client.on_receive(lambda raw_data: received_callback(raw_data, graphs, graph_Data))
        client.on_error(network_error_callback)

        qapp.exec_()
    except Exception as e:
        import traceback

        print(traceback.format_exc())
