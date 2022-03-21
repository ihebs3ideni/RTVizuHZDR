import pyqtgraph as pg
import numpy as np
from typing import List

class CenteredArrowItem(pg.ArrowItem):
    def setData(self, x, y, angle):
        self.opts['angle'] = angle
        opt = dict([(k, self.opts[k]) for k in ['headLen', 'tipAngle', 'baseAngle', 'tailLen', 'tailWidth']])
        path = pg.functions.makeArrowPath(**opt)
        b = path.boundingRect()
        tr = pg.QtGui.QTransform()
        tr.rotate(angle)
        tr.translate(-b.x() - b.width() / 2, -b.y() - b.height() / 2)
        self.path = tr.map(path)
        self.setPath(self.path)
        self.setPos(x, y)

class QTQuiver(pg.GraphicsItem):
    arrows : List[pg.ArrowItem] = []
    def __init__(self, ax, X, Y, U, V, color="K"):
        self.ax = ax
        self.rows, self.cols = X.shape
        # print(X.shape)
        # print(Y.shape)
        # print(U.shape)
        # print(V.shape)
        for i in range(self.rows):
            for j in range(self.cols):
                pos = [X[i,j], Y[i,j]]
                angle = np.degrees(np.arctan2(V[i,j], U[i,j]))
                arrow = pg.ArrowItem(pos=pos, angle=angle,headLen=0.01, headWidth=.01, tailLen=.01, tailWidth=.01, pxMode=False)
                self.arrows.append(arrow)
                self.ax.addItem(arrow)


    def set_UVC(self, U, V, C=None):
        print("updating")
        for _,arr in enumerate(self.arrows):
            for i in range(self.rows):
                for j in range(self.cols):
                    angle = np.degrees(np.arctan2(V[i, j], U[i, j]))
                    arr.setStyle(angle=angle)

if __name__ == '__main__':
    import numpy as np
    import PyQt5.QtWidgets as qt
    import pyqtgraph as pg


    class GraphWidget(qt.QWidget):
        """A widget for simplifying graphing tasks

        :param qt.QWidget parent:
        :param Dict[str, dict] layout: A mapping from title to row/col/rowspan/colspan kwargs
        """

        def __init__(self, parent, layout_spec):
            super(GraphWidget, self).__init__(parent=parent)

            self.axes = {}
            glw = pg.GraphicsLayoutWidget(parent=self)
            for name, layout in layout_spec.items():
                self.axes[name] = pg.PlotItem(name=name, title=name)
                glw.addItem(self.axes[name], **layout)
            box_layout = qt.QVBoxLayout()
            box_layout.addWidget(glw, 1)
            self.setLayout(box_layout)

        @property
        def normal_pen(self):
            return pg.mkPen(color='w', width=2)

        @property
        def good_pen(self):
            return pg.mkPen(color='g', width=2)

        @property
        def bad_pen(self):
            return pg.mkPen(color='r', width=2)

        def plot(self, mode, x, y, axis):
            if mode == 'normal':
                pen = self.normal_pen
            elif mode == 'good':
                pen = self.good_pen
            elif mode == 'bad':
                pen = self.bad_pen

            plot_item = pg.PlotCurveItem(x, y, pen=pen, skipFiniteCheck=True)
            self.axes[axis].addItem(plot_item)


    if __name__ == '__main__':
        from PyQt5.QtGui import *
        from PyQt5.QtWidgets import *
        from PyQt5.QtCore import *

        import time
        import traceback, sys


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
            finished = pyqtSignal()
            error = pyqtSignal(tuple)
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

            def __init__(self, fn, *args, **kwargs):
                super(Worker, self).__init__()

                # Store constructor arguments (re-used for processing)
                self.fn = fn
                self.args = args
                self.kwargs = kwargs
                self.signals = WorkerSignals()

                # Add the callback to our kwargs
                self.kwargs['progress_callback'] = self.signals.progress

            @pyqtSlot()
            def run(self):
                '''
                Initialise the runner function with passed args, kwargs.
                '''

                # Retrieve args/kwargs here; and fire processing using them
                try:
                    result = self.fn(*self.args, **self.kwargs)
                except:
                    traceback.print_exc()
                    exctype, value = sys.exc_info()[:2]
                    self.signals.error.emit((exctype, value, traceback.format_exc()))
                else:
                    self.signals.result.emit(result)  # Return the result of the processing
                finally:
                    self.signals.finished.emit()  # Done


        class MainWindow(QMainWindow):

            def __init__(self, *args, **kwargs):
                super(MainWindow, self).__init__(*args, **kwargs)

                self.counter = 0

                layout = QVBoxLayout()

                self.l = QLabel("Start")
                b = QPushButton("DANGER!")
                b.pressed.connect(self.oh_no)

                layout.addWidget(self.l)
                layout.addWidget(b)

                w = QWidget()
                w.setLayout(layout)

                self.setCentralWidget(w)

                self.show()

                self.threadpool = QThreadPool()
                print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

                self.timer = QTimer()
                self.timer.setInterval(1000)
                self.timer.timeout.connect(self.recurring_timer)
                self.timer.start()

            def progress_fn(self, n):
                print("%d%% done" % n)

            def execute_this_fn(self, progress_callback):
                for n in range(0, 5):
                    time.sleep(1)
                    progress_callback.emit(int(n * 100 / 4))

                return "Done."

            def print_output(self, s):
                print(s)

            def thread_complete(self):
                print("THREAD COMPLETE!")

            def oh_no(self):
                # Pass the function to execute
                worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
                worker.signals.result.connect(self.print_output)
                worker.signals.finished.connect(self.thread_complete)
                worker.signals.progress.connect(self.progress_fn)

                # Execute
                self.threadpool.start(worker)

            def recurring_timer(self):
                self.counter += 1
                self.l.setText("Counter: %d" % self.counter)


        app = QApplication([])
        window = MainWindow()
        app.exec_()