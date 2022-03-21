from queue import Queue
from typing import Protocol, Callable, Any, Dict

from Package.BackEnd.TCP_Client import BaseTcpClient
from Package.FrontEnd.BaseInterface import BaseGraphCanvas


class ControllerInterface(Protocol):
    def add_resource(self, resource: object):
        """Adds a data resource following resource protocol"""
        ...

    def add_view(self, view: object):
        """Adds view to controller"""
        ...

    def _on_new_data(self):
        """set a callback for w"""
        ...

    def on_click_callback(self, elementId, callback: Callable):
        """sets a callback onn click on view element with elementID"""
        ...
class ResourceProtocol(Protocol):
    def push(self, data):
        """push element resource"""
        ...

    def pop(self):
        """pops last element"""

    def isEmpty(self):
        """checks if queue is empty"""

class Resource:
    def __init__(self):
        self.queue = Queue()

    def push(self, data):
        self.queue.put(data)

    def pop(self):
        return self.queue.get() if not self.isEmpty() else None

    def isEmpty(self):
        return self.queue.empty()

class Controller:
    def __init__(self):
        self.rawData: Any = None
        self.data_holder: Any = None

    def add_resource(self, resource):
        self.resource: ResourceProtocol = resource

    def add_view(self, view: Dict[str, BaseGraphCanvas]):
        self.view: Dict[str, BaseGraphCanvas] = view

    def add_parsere(self, parser: Any):
        self.parser = parser

    def on_click_callback(self, elementId, callback: Callable):
        self.view[elementId].set_onclick_callback(callback)

    def _on_new_data(self):
        if self.data_holder is None:
            return
        for id_, element in self.view.items():
            element.updateFigure(self.data_holder.get(id_))
        self.data_holder = None

    def _refresh(self):
        if self.resource is None:
            return
        self.data_holder = self.parser(self.resource.pop())
        self._on_new_data()



