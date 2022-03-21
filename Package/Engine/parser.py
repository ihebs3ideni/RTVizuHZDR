from typing import Protocol, Callable, Dict, Any


class ParserProtocol(Protocol):
    def map_view_to_callbacks(self, viewId: str, parsing_callback: Callable):
        """adds an element to the parser map"""
        ...

    def __call__(self, raw_Data, *args, **kwargs) -> Dict[str, Any]:
        """parses the raw data to appropriate formatted data for each view element"""
        ...


class SimpleParser:
    def __init__(self):
        self.map: Dict[str, Callable] = dict()

    def map_view_to_callbacks(self, viewId: str, parsing_callback: Callable):
        self.map[viewId] = parsing_callback

    def __call__(self, raw_Data, *args, **kwargs) -> Dict[str, Any]:
        return dict((id_, func(raw_Data)) for id_, func in self.map.items())
