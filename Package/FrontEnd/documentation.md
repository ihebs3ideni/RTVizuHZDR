##Base Interface
This class represents the interface that the subclasses either uses or must implement.  
#####Public API
|Method|args|return|Comment|
|---------|----|--------|-------|
|updateFigure|data: class from plotDataFormat.py|None|this is a wrapper around the update signal/slot mechanism|
|add_postProcess|func: Callable[[object], None]|None|adds a postprocess to the pipeline to be executed before the data is plotted|
|take_screenshot|Folder_path: str|None| exports a screen shot of the object widget to the folder specified with formated file name that depends on the date time|
|write_data|data: BaseModel, path:str, newLine:Optional[bool]=True|None| Basic api to write data to a txt or json file, !!!NOT CSV!!!|
#####Interface To be Implemented by child classes
|Method|args|return|Comment|
|---------|----|--------|-------|
|create_canvas|None|None|used as a Figure initializer for different library implementation|
|onUpdatePlot|data: class from plotDataFormat.py|None|This is responsible for actually updating the plot and will be called after updateFigure|
|set_onclicked_callback|callback: Callable|None|sets a callback on mouse clicked|
|get_data_container|None|class from plotDataFormat.py|This is a static method used to retrieve the data type this class expects the data to be in, helpful when importing is confusing|


###MPL Interface
This class overwrites the Base interface in order to implement matplotlib based graphs
####Line Graphs
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
####Level Graphs
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
####Vector Graphs
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|


##QT Interfacce
This class overwrites the Base interface in order to implement pyqtgraphs based graphs
####Line Graphs
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
####Level Graphs
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
####Vector Graphs
Pyqtgraphs doesn't offer support for vector graph plots.

##Mayavi Interface
This class overwrites the Base interface in order to implement mayavi based graphs
####Dynamic Graph
|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|


##UML
![img](file:///D:\HZDR\HZDR_VISU_TOOL\UML_FrontEnd.png)

