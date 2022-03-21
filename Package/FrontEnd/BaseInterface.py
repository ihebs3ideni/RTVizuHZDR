import datetime
import pathlib
import uuid
from abc import abstractmethod, ABC
from threading import get_ident
from typing import Any, List, Callable

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRect, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QMenu

from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure, BaseModel
from Package.FrontEnd.BackgroundProcessing import WorkerArgs, Worker

hzdr_icon_path = r"D:\HZDR\HZDR_VISU_TOOL\Package\Icons\hzdr_logo.png"


class BaseGraphException(Exception):
    """Base High level exception to notify user to errors related to the UI"""

    def __init__(self, ID: str, obj: Any, message: str):
        self.ID = ID
        self.obj = obj
        self.message = message
        super().__init__(message)

    def __str__(self):
        return "Error Message: %s ; @ Error source ID: %s\n " \
               "The problematic variable can be accessed by catching the Exception and referencing \"exception.obj\"" % (
                   self.message, self.ID)


class SpawningPositionException(BaseGraphException):
    """High level exception raised when the position where the window will spawn isn't correctly specified"""


class PathNotValidException(BaseGraphException):
    """High level exception raised when the path provided to is not valid"""

class ProcessingException(BaseGraphException):
    """High level exception raised a exception occurs while executing a user provided Process"""

class BaseGraphCanvas(QWidget):
    """Base class for all graph objects/widgets"""
    ID: str = None
    xRange: int = 100
    update_signal = pyqtSignal([object])
    autoscale_signal = pyqtSignal([bool])
    autoscale_flag: bool = None
    dynamic_canvas: Any = None
    postProcesses: List[Callable] = None  # functions need to accept the same datatype as updatePlot and overwrite it
    thread_pool: QThreadPool = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None, icon_path=hzdr_icon_path):
        super().__init__()
        self.structure = structure
        if self.structure.ID:
            self.ID = self.structure.ID
        else:
            self.ID = str(uuid.uuid4())
        # init object attributes
        self.postProcesses = []
        self.autoscale_flag = True

        # set window's icon and title
        self.setWindowTitle(self.ID)
        self.setWindowIcon(QIcon(icon_path))
        # resize the window to roughly a quarter of the screen's area
        screen: QRect = QDesktopWidget().availableGeometry()
        self.resize(screen.width() // 2, screen.height() // 2)
        if spawning_position:
            self._setLocationOnScreen(spawning_position)

        if self.structure.asynchronous:
            # only reference threadpool instance if execution mode is asynchronous
            self.thread_pool = QThreadPool.globalInstance()
        self.update_signal.connect(self._updateRoutine)

    ######################################################################
    # Public super class interface
    ######################################################################

    def updateFigure(self, data):
        """a wrapper around the update signal"""
        self.update_signal.emit(data)

    def add_postProcess(self, func: Callable[[object], None]):
        self.postProcesses.append(func)

    def take_screenshot(self, path="D:\HZDR\HZDR_VISU_TOOL\Package\Export_Test", ID=""):
        now = datetime.datetime.now()
        name = f"/shot_{ID}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        # path = str(os.getcwd()) + "/screenShots"  # create a new directory path
        pathlib.Path(path).mkdir(exist_ok=True)  # create the directory if it doesn't exist
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(path + name, 'jpg')

    def write_data(self, data: BaseModel, path, newLine=True):
        """ Basic api to write data to a txt or json file. !!!!NOT CSV!!!!
            Data must be one of the formats in Package/DataStructures/plotDataFormat.py.
            path is  path + filename """
        try:
            with open(path, "a") as f:
                f.write(data.json())
                if newLine:
                    f.write("\n")
        except FileNotFoundError:
            raise PathNotValidException(ID=self.ID, obj=path, message="The provided path is not Valid")

    @pyqtSlot(bool)
    def autoscale_trigger(cls, state: bool):
        cls.autoscale_flag = state

    ######################################################################
    # Public child class interface (To be implemented)
    ######################################################################

    @abstractmethod
    def create_canvas(self):
        """an interface for initializing the canvas based on different libraries"""
        ...

    @abstractmethod
    def onUpdatePlot(self, data: Any):
        """A place holder for implementing each library's api in child classes"""
        ...

    @abstractmethod
    def set_onclicked_callback(self, callback: Callable):
        ...

    @abstractmethod
    def add_vLine(self, coordinates: List[float], ymin: List[float], ymax: List[float], **kwargs):
        """ a simple interface for drawing vertical lines on the graph canvas.
                -this api should allow the addition of either one or multiple lines at a time.
                -kwargs should depend on the implementation"""
        ...

    @abstractmethod
    def add_hLine(self, coordinates: List[float], xmin: List[float], xmax: List[float], **kwargs):
        """ a simple interface for drawing horizontal lines on the graph canvas.
                -this api should allow the addition of either one or multiple lines at a time.
                -kwargs should depend on the implementation"""
        ...

    @abstractmethod
    def set_y_lim(self, downtLim, upLim):
        """An interface for setting the plot's y limits in child classes"""
        ...

    @abstractmethod
    def set_x_lim(self, downtLim, upLim):
        """An interface for setting the plot's x limits in child classes"""
        ...

    @abstractmethod
    def clearPlot(self):
        """An interface for clearing the plot in child classes"""
        ...


    @abstractmethod
    def handle_background_task_finished(self, ID, status):
        print(f"Task with ID: {ID} Is Done {status}")

    @abstractmethod
    def handle_background_task_error(self,error:BaseGraphException, ID= None):
        print(f"ERROR in {ID}: {error}")

    @abstractmethod
    def what_r_u(self, event=None, **kwargs):
        """to be reimplemented by each child Class to redefine themselves.
            args: event necessary if used as on click callback"""
        print("I am a Base Graph object with ID: %s" % self.ID)


    @staticmethod
    def get_data_container():
        """an Interface for returning the type of data structure updateFigure expects """
        ...

    def contextMenuEvent(self, event):
        print(event)
        contextMenu = QMenu(self)
        placeHolder = contextMenu.addAction("THIS IS A PLACE HOLDER, Implement for additional features")
        # openAct = contextMenu.addAction("Open")
        quitAct = contextMenu.addAction("Quit")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            self.close()

    ######################################################################
    # Non-public interface
    ######################################################################

    @staticmethod
    def get_thread_id():
        """returns the ID of the thread where the function is called..
        useful for debugging when asynchronous mode is ON """
        return get_ident()

    def _apply_processes(self, data):
        for p in self.postProcesses:
            try:
                p(data)
            except Exception as e:
                import traceback
                raise ProcessingException(ID=self.ID, obj=p, message=f"The following error occured while "
                                                                     f"executing a user process {traceback.format_exc()}")

        return data

    def _updateRoutine(self, data):
        """Applies the postprocessing layers specified by the user before updating the plot.
        Execution mode depends on structure.asynchronous:
            False: normal top down sequential execution.
            True: Delegate postprocessing to threadpool and update plot on results ready.
        !!!ASYNCHRONOUS DOESN'T MEAN FASTER!!! Due to overhead non asynchronous mode is faster
         however if the postprocessing is heavy, it blocks the eventloop from updating the GUI"""

        if not self.structure.asynchronous or not self.postProcesses:
            try:
                self._apply_processes(data)
            except ProcessingException as e:
                print(e)
            else:
                self.onUpdatePlot(data)
        else:
            id_ = self.ID + f" {('%032x' % uuid.uuid4().int)[:8]}"
            worker = self.spawn_worker(task=self._apply_processes,
                                       data=data.copy(deep=True),
                                       finished=WorkerArgs(callback=self.handle_background_task_finished,
                                                           kwargs=dict(ID=id_)),
                                       results=WorkerArgs(callback=self.onUpdatePlot, kwargs=dict()),
                                       error=WorkerArgs(callback=self.handle_background_task_error,
                                                        kwargs=dict(ID=id_)),
                                       progress=WorkerArgs(callback=lambda n: print("%d%% done" % n), kwargs=dict())
                                       )
            self.thread_pool.start(worker)

    def set_xRange(self, xrange: int):
        self.xRange = xrange

    def set_xy_lim(self):
        """uses the set_x_lim and set_y_lim interface that needs to be implemented by the child class"""
        if self.structure.xLim:
            xlim = self.structure.xLim
            self.set_x_lim(xlim[0], xlim[1])
        if self.structure.yLim:
            ylim = self.structure.yLim
            self.set_y_lim(ylim[0], ylim[1])

    def toggle_autoscale(self, event=None, **kwargs):
        """this function uses the signal slot mechanism that needs to be specified by child classes.
            args: event necessary if used as on click callback"""
        self.autoscale_signal.emit(not self.autoscale_flag)

    def _setLocationOnScreen(self, index=None):
        """Sets the location in which the window will appear depending on the index
                ---------
                | 1 | 2 |
                | 3 | 4 |
                --------
        """
        if index in range(1, 5):
            ag = QDesktopWidget().availableGeometry()
            origin = ag.topLeft()
            # print(origin.x(), origin.y())
            newX, newY = origin.x(), origin.y()
            if index % 2 == 0:
                newX = ag.width() // 2
            if index > 2:
                newY = ag.height() // 2
            self.move(newX, newY)
        else:
            raise SpawningPositionException(ID=self.ID, obj=self,
                                            message="the provided index: %d is not in [1..4]" % index)

    @staticmethod
    def spawn_worker(task, results: WorkerArgs = None, finished: WorkerArgs = None, error: WorkerArgs = None,
                     progress: WorkerArgs = None, **kwargs):
        """Creates a Worker instance with specified signal callbacks.
        !!!! It doesn't keep track of the instances, it's the responsability of the user to do so!!!!"""
        worker = Worker(task, False, **kwargs)
        if finished:
            worker.signals.finished.connect(lambda status: finished.callback(status=status,**finished.kwargs))
        if error:
            worker.signals.error.connect(lambda e: error.callback(error= e, **error.kwargs))
        if progress:
            worker.signals.progress.connect(lambda n: progress.callback(n, **progress.kwargs))
        if results:
            worker.signals.result.connect(lambda res: results.callback(res, **results.kwargs))
        return worker


class BaseFactory(ABC):
    """Factory that creates a customised graph object. the factory is not the owner of the objects
       and they need to be maintained by the user"""

    @abstractmethod
    def get_LineGraph(self, setup: GraphStructure, spawning_position: int = 1):
        """returns a line graph object"""
        ...

    @abstractmethod
    def get_LineGraph_DataStructure(self):
        """returns the data structure used by the line Graph object"""
        ...

    @abstractmethod
    def get_LevelGraph(self, setup: GraphStructure, spawning_position: int = 1):
        """returns a level graph object"""
        ...

    @abstractmethod
    def get_LevelGraph_DataStructure(self):
        """returns the data structure used by the level graph object"""
        ...

    @abstractmethod
    def get_VectorGraph(self, setup: GraphStructure, spawning_position: int = 1):
        """returns a vector graph object"""
        ...

    @abstractmethod
    def get_VectorGraph_DataStructure(self):
        """returns the data structure used by the vector Graph object"""
        ...


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    print(BaseGraphCanvas.get_data_container())
    structure = GraphStructure(ID="test Graph", blit=True, grid=True, yLim=(1, -1),
                               elements=dict(
                                   g1=ElementStructure(sensorID="channel_0", color="blue", label="channel_0")))
    qapp = QApplication(sys.argv)
    bgc = [BaseGraphCanvas(structure, spawning_position=i) for i in range(1, 5)]
    # bgc.setLocationOnScreen()
    for b in bgc:
        b.show()
    qapp.exec_()
