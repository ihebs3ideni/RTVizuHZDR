import unittest, json
import time
from Package.BackEnd.TCP_Client import *
from threading import Thread
import logging
logging.basicConfig(format='%(asctime)s %(message)s')

global dummy_test
dummy_test = "empty"

class TestTCPCLIENT(unittest.TestCase):
    """class for testing the TCP connection"""
    host, port = "localhost", 8000



    def test_Async_Connection(self):
        def connect_callback():
            logging.warning("connection callback triggered")
            # raise MakingConnectionException(None, "this is a test, connection callback triggered")

        def receive_callback(raw_data):
            pass
            # raise MakingConnectionException(raw_data.decode(), "this is a test, connection callback triggered")

        def close_callback():
            pass
            # raise ConnectionLostException(client, "connection closed callback is triggered")

        logging.warning("Testing wrong Connection")
        with AsyncTCP_Client(self.host, 1000) as client:
            client.on_connect(connect_callback)
            client.on_receive(receive_callback)
            client.on_disconnect(close_callback)
            self.assertRaises(MakingConnectionException, client.create_connection)

        logging.warning("Testing right Connection")
        with AsyncTCP_Client(self.host, self.port) as client:
            client.on_connect(connect_callback)
            client.on_receive(receive_callback)
            client.on_disconnect(close_callback)
            client.create_connection()
            self.assertEqual(client.isConnected(), True)
            client.write("echo Test")


        logging.warning("Testing connection Done")


    def test_Async_receive_test(self):
        global dummy_test
        def connect_callback():
            logging.warning("Connection callback")

        def receive_callback(raw_data:bytes):
            logging.warning("receive callback")
            print(str(raw_data, encoding='ascii'))
            global dummy_test
            dummy_test = str(raw_data, encoding='ascii')

        def close_callback():
            pass

        logging.warning("Testing sending/receiving")


        with AsyncTCP_Client(self.host, self.port) as client:

            client.on_connect(connect_callback)
            client.on_receive(receive_callback)
            client.on_disconnect(close_callback)
            client.create_connection()
            print("connection status = ", client.isConnected())
            client.start_event_loop(threaded=True)
            client.write("echo hey boo")
            time.sleep(0.1)
            print(dummy_test)
            self.assertEqual("hey boo", dummy_test)
            client.write("echo this is not fun")
            time.sleep(0.1)
            self.assertEqual("this is not fun", dummy_test)

        logging.warning("Testing sending/receiving DONE")

    def test_diconnection(self):
        def connect_callback():
            pass
            # raise MakingConnectionException(None, "this is a test, connection callback triggered")

        def receive_callback(raw_data):
            pass
            # raise MakingConnectionException(raw_data.decode(), "this is a test, connection callback triggered")

        def close_callback():
            raise ConnectionLostException(client, "connection closed callback is triggered")

        logging.warning("Testing disconnection")
        with AsyncTCP_Client(self.host, self.port) as client:
            client.on_connect(connect_callback)
            client.on_receive(receive_callback)
            client.on_disconnect(close_callback)
            client.create_connection()
            client.start_event_loop(threaded=True)
            time.sleep(0.1)
            self.assertEqual(client.isConnected(), True)
            self.assertRaises(ConnectionLostException, client.disconnection_callback)
        logging.warning("Testing disconnection Done")
    def test_error(self):
        def connect_callback():
            pass
            # raise MakingConnectionException(None, "this is a test, connection callback triggered")

        def receive_callback(raw_data):
            pass
            # raise MakingConnectionException(raw_data.decode(), "this is a test, connection callback triggered")

        def close_callback():
            raise ConnectionLostException(client, "connection closed callback is triggered")

        def error_callback():
            raise ClientBaseException(error=client.get_raw_socket().getsockopt(socket.SOL_SOCKET, socket.SO_ERROR),
                                      message=traceback.format_exc())

        logging.warning("Testing exception handling")
        with AsyncTCP_Client(self.host, self.port) as client:
            client.on_connect(connect_callback)
            client.on_receive(receive_callback)
            client.on_disconnect(close_callback)
            client.on_error(error_callback)
            client.create_connection()
            client.start_event_loop(threaded=True)
            self.assertEqual(client.isConnected(), True)
            self.assertRaises(ClientBaseException, client.error_callback)

        logging.warning("Testing exception handling Done")
if __name__ == "__main__":
    unittest.main()




