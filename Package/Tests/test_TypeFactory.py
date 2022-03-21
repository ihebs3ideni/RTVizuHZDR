import unittest, json
import time
from Package.DataStructures.TypeFactory import LinePlotDataFormatFactory, GraphStructureFactory, \
    TypeFactories, TypeNotSupportedException, TCPRequestObjectFactory
from Package.DataStructures.GraphArgsStructure import GraphStructure, LineElementStructure
from Package.DataStructures.plotDataFormat import LineGraphData
from Package.DataStructures.RingBuffer import RingBuffer
import logging
logging.basicConfig(format='%(asctime)s %(message)s')


class TestTypeFactory(unittest.TestCase):
    def test_Graph_Structure_Type(self):
        logging.warning("Testing GraphStructure Types")
        GSF = GraphStructureFactory()
        self.assertEqual(GraphStructure, GSF.get_main_object())
        self.assertEqual(LineElementStructure, GSF.get_sub_objects().get("ElementStructure"))

    def test_LinePlot_arg_Format(self):
        logging.warning("Testing LinePlotArgFormat Types")
        LPFF = LinePlotDataFormatFactory()
        self.assertEqual(LineGraphData, LPFF.get_main_object())
        self.assertEqual(RingBuffer, LPFF.get_sub_objects().get("RingBuffer"))

    def test_TypeFactories(self):
        logging.warning("Testing Type Factories Types")
        TF = TypeFactories()
        logging.warning("Right Cases")
        self.assertEqual(GraphStructureFactory, TF.graphStructureFactory)
        self.assertEqual(LinePlotDataFormatFactory, TF.linePlotArgFormatFactory)
        self.assertEqual(TCPRequestObjectFactory, TF.tcpRequestFormatFactory)
        self.assertEqual(GraphStructureFactory, TF.getByName("graphStructureFactory"))
        self.assertEqual(LinePlotDataFormatFactory, TF.getByName("linePlotArgFormatFactory"))
        self.assertEqual(TCPRequestObjectFactory, TF.getByName("tcpRequestFormatFactory"))
        logging.warning("OK")
        logging.warning("Wrong Cases")
        self.assertRaises(TypeNotSupportedException, lambda: TF.getByName("GraphStructureFactory"))
        self.assertRaises(TypeNotSupportedException, lambda: TF.getByName("LinePlotDataFormatFactory"))
        self.assertRaises(TypeNotSupportedException, lambda: TF.getByName("TCPRequestObjectFactory"))
        logging.warning("OK")






if __name__ == "__main__":
    unittest.main()
