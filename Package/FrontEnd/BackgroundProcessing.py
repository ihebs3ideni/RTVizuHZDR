from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject, QRunnable, QThreadPool
from typing import Callable, Dict
import traceback
from dataclasses import dataclass


@dataclass
class WorkerArgs:
    """Data structure intended to hold the callbacks and arguments for a worker signal/slot mechanism"""
    callback: Callable = None
    kwargs: dict = None


WorkerStatus: dict = {0: "Successfully", -1: "Unsuccesfully"}


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal(str)
    error = pyqtSignal(object)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, track_progress=True, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        if track_progress:
            # Add the callback to our kwargs
            self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        status = -1  # assuming error
        try:
            result = self.fn(**self.kwargs)
        except Exception as e:
            # print(e)
            # exctype, value = sys.exc_info()[:2]
            # traceback.format_exc()
            self.signals.error.emit(e)
        else:
            status = 0
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit(WorkerStatus.get(status, "Undefined"))  # Done


# import multiprocessing as mp
#
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QPushButton, QApplication, QWidget
import sys, time
import uuid
import numpy as np
from threading import get_ident

class WorkerTestClass(QMainWindow):
    # workers: Dict[str, WorkerThread] = None

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool.globalInstance()
        self.button = QPushButton("RUN TASK")
        self.button.clicked.connect(self.buton_clbk)
        hbox = QHBoxLayout(self)
        hbox.addStretch()
        hbox.addWidget(self.button)
        hbox.addStretch()
        main_widget = QWidget(self)
        main_widget.setLayout(hbox)
        self.setCentralWidget(main_widget)
        # self.workers = dict()

    def get_worker(self, func, **kwargs):
        id_ = kwargs.get("ID")
        worker = Worker(func, **kwargs)
        worker.signals.finished.connect(lambda status: self.handle_finished(status, id_))
        worker.signals.result.connect(self.capture_data)
        worker.signals.error.connect(lambda error: self.handle_background_task_error(error, id_))
        return worker

    def handle_background_task_error(self, error, ID=None):
        print(f"ERROR in {ID}: {error}")

    @staticmethod
    def dummy_task(ID, **kwargs):
        print(get_ident())
        progress = kwargs.get("progress_callback", None)
        # id_ = kwargs.get("ID")
        for i in range(10):
            # print(id_, i)
            progress.emit(i * 10)
            time.sleep(0.5)
        return np.random.random((30, 30))

    @staticmethod
    def handle_finished(status, ID):
        print(f"Task with ID: {ID} Is Done {status}")

    @staticmethod
    def capture_data(data):
        print(data[0][0])

    @staticmethod
    def progress_fn(n):
        print("%d%% done" % n)

    @pyqtSlot()
    def buton_clbk(self):
        try:
            id_ = str(uuid.uuid4())
            worker = self.get_worker(self.dummy_task, ID=id_)
            self.threadpool.start(worker)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = WorkerTestClass()
    window.show()

    app.exec_()
