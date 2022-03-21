from typing import Callable, Tuple, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QCheckBox, QGridLayout, QLabel, QMessageBox

IconPath = r"D:\HZDR\HZDR_VISU_TOOL\Package\Icons\hzdr_logo.png"

class IconObject(QWidget):
    def __init__(self, text, image_path, size: Tuple = (64, 64)):
        super().__init__()
        self.size = size
        self.title = QLabel(text=text)
        self.label = QLabel()
        pixmap = QPixmap(image_path).scaled(*size, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)

        mainlayout = QHBoxLayout(self)
        mainlayout.addWidget(self.title)
        mainlayout.addWidget(self.label)

    def setCallback(self, callback: Callable):
        """Callback needs to catch the mouse click event as the first parameter:
            func(event, *args, **kwargs) """
        self.label.mousePressEvent = callback

    def update_Icon(self, new_path):
        pixmap = QPixmap(new_path).scaled(*self.size, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)


class BaseControlPanel(QMainWindow):
    def __init__(self, title="Base Control Panel", size=(600,300)):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(*size)
        self.setWindowIcon(QIcon(IconPath))
        self.mainWidget = QWidget()
        self.mainLayout = QGridLayout()  # main layout is a Horizental, it means new items go from left to right
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.setLayout(self.mainLayout)

        self.close_callbacks: List[Callable] = None #callback to be executed when closing the panel
        self.push_buttons: Dict[str, QPushButton] = dict()
        self.checkboxes: Dict[str, QCheckBox] = dict()
        self.icons: Dict[str, IconObject] = dict()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.close_callbacks is not None:
                for f in self.close_callbacks:
                    f()
            event.accept()

        else:
            event.ignore()

    def on_close(self, callback: Callable):
        if self.close_callbacks is None:
            self.close_callbacks = []
        self.close_callbacks.append(callback)

    def add_push_button(self, text: str, coordinates: Tuple, callback: Callable = None, UID=None, **kwargs) -> QPushButton:
        """!!! UID needs to be non None if the 'self.push_buttons' dictionary is used to track the buttons!!!"""
        b = QPushButton(self, text=text)
        if callback:
            b.clicked.connect(callback)
        self.mainLayout.addWidget(b, *coordinates, **kwargs)
        if UID:
            self.push_buttons[UID] = b
        return b

    def add_checkbox(self, text, coordinates: Tuple, callback: Callable = None, UID=None, **kwargs) -> QCheckBox:
        """!!! UID needs to be non None if the 'self.checkboxes' dictionary is used to track the checkboxes!!!"""
        cb = QCheckBox(text)
        if callback:
            cb.toggled.connect(callback)
        self.mainLayout.addWidget(cb, *coordinates, **kwargs)
        if UID:
            self.checkboxes[UID] = cb
        return cb

    def add_Icon(self, text, image_path, coordinates: Tuple, callback: Callable = None, UID = None, **kwargs) -> IconObject:
        """!!! UID needs to be non None if the 'self.icons' dictionary is used to track the icons!!!"""
        icon = IconObject(text=text, image_path=image_path)
        if callback:
            icon.setCallback(callback)
        self.mainLayout.addWidget(icon, *coordinates, **kwargs)
        if UID:
            self.icons[UID] = icon
        return icon


def main():

    cp = BaseControlPanel("this is a test")
    # io = IconObject("this is a test", )
    # io.show()
    for i in range(2):
        for j in range(2):
            pb = cp.add_push_button(f"dummy button {i, j}", (i, j))
            pb.clicked.connect(lambda event, x=i, y=j: print(f"Coordinates are: {x, y}"))
    for i in range(2, 4):
        for j in range(2):
            cb = cp.add_checkbox(f"dummy checkbox {i, j}", (i, j))
            cb.toggled.connect(lambda state, x=i, y=j: print(f"Coordinates are: {x, y}, state: {state}"))
    for i in range(2):
        for j in range(2, 3):
            ic = cp.add_Icon(f"dummy Icon {i, j}", IconPath, (i, j),
                             lambda event: print(f"this is a callback test: {event.globalPos(), event.pos()}"))

    return cp



if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    qapp = QApplication(sys.argv)
    cp = main()
    cp.show()
    qapp.exec_()
