# RTVizuHZDR
real time visualization Library for experiment monitoring for HZDR Contactless Inductive Flow Tomography team

## Custom Data Structure Overview
### GraphArgsStrcuture
a Number of objects used as config structures.
####GraphStructure:
Object used as config to setup one Figure. It Contains a dictionary of **ElementStructure** that setup each element individually
and a list of optional parameters for further control.

**!!!! IF YOU SET _asynchronous = True_ FOR ONE FIGURE, SET IT FOR ALL FIGURES BECAUSE THEY SHARE THE SAME EVENTLOOP IF THEY 
 RUN WITHIN THE SAME PROCESS!!!!**

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|elements|Dict[str,ElementStructure]|No|a dictionary of elements to be drawn in the canvas. Each element will be referenced by the key provided here.|
|xLim|Tuple[float, float]|Yes|the x axis limits if autoscale is not active|
|yLim|Tuple[float, float]|Yes|the x axis limits if autoscale is not active|
|grid|Bool|Yes|controls whether or not to render gridlines|
|blit|Bool|Yes|only relevant for MPL Graphs that support [blitting](https://matplotlib.org/stable/tutorials/advanced/blitting.html) |
|ID|str|Yes|an optional ID to keep track of graphs from within, otherwise a uuid will be generated instead|
|colormap|str|Yes|Name of the colormap to be used, only relevant for quivers|
|asynchronous|Bool|Yes|Controls where the postprocessing runs.  False->mainthread  True->Threadpool.  Useful for heavy processing that blocks the Eventloop|


####ElementStructure:
Object used as config to setup one element within the Figure.
Whether each attribute is necessary or optional depends on the Figure Type.
##### For Line Graphs:
if the attribute is not in the table, it is not relevant to this figure type.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|sensorID|str|No|the ID/Key of the specific data to be plotted in this element|
|color|str or RGB|Yes|the color of the line element|
|label|str|Yes|the label of this element in the legend|

##### For Level Graphs:
if the attribute is not in the table, it is not relevant to this figure type.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|X|numpy.ndArray|No|Initial X_Position of each Point|
|Y|numpy.ndArray|No|Initial Y_Position of each Point|
|Z|numpy.ndArray|Yes|Initial Z_Position of each Point|
|color|str or RGB|Yes|the color of the line element|
|label|str|Yes|the label of this element in the legend|

##### For Vector Graphs/Quivers:
if the attribute is not in the table, it is not relevant to this figure type.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|X|numpy.ndArray|No|Initial X_Position of each Point|
|Y|numpy.ndArray|No|Initial Y_Position of each Point|
|Z|numpy.ndArray|Yes|Initial Z_Position of each Point|
|color|str or RGB|Yes|the color of the line element|
|label|str|Yes|the label of this element in the legend|
|zorder|int|Yes|the zorder for the artist. Artists with lower zorder values are drawn first|
|scale|int|Yes|Number of data units per arrow length unit, [more..](https://matplotlib.org/stable/api/_as_gen/matplotlib.quiver.Quiver.html)|
|units|str|Yes|The scaling units according to [the MPL Quiver API](https://matplotlib.org/stable/api/_as_gen/matplotlib.quiver.Quiver.html)|
|density|float|Yes|Controls the closeness of streamlines according to [the MPL Streamlines API](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.streamplot.html#matplotlib.axes.Axes.streamplot)|
#####For Mayavi Dynamic Graphs:
if the attribute is not in the table, it is not relevant to this figure type.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|

###plotDataFormat
a number of Objects defining the data structures used by each Figure Type
####LineGraphData:
An object grouping the data needed by Line graphs. This assumes that all lines share the same X axis data.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|x_Data|RingBuffer(custom)|No|Ringbuffer used as the common X axis Data for all Figure Lines|
|y_Data|Dict[str, RingBuffer]|No|dictionary that contains the y axis data for each Figure Line, the key/ID must match that of the element dict in GraphStructure |

####LevelGraphData:
An object grouping the data needed by Level graphs.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|x_Data|Dict[str, ndarray]|No|dictionary that contains the element id and the x_Data for a group of points connected by a line, the element must match that of the element dict in GraphStructure|
|y_Data|Dict[str, ndarray]|No|dictionary that contains the element id and the y_Data for a group of points connected by a line, the element must match that of the element dict in GraphStructure|
|z_Data|Dict[str, ndarray]|Yes|dictionary that contains the element id and the z_Data for a group of points connected by a line, the element must match that of the element dict in GraphStructure|


####VectorGraphData:
An object grouping the data needed by Vector graphs.

|Attribute|Type|Optional|Comment|
|---------|----|--------|-------|
|x_Data|ndarray|No|array that contains the X axis data of the grid |
|y_Data|ndarray|No|array that contains the Y axis data of the grid |
|z_Data|ndarray|Yes|array that contains the Z axis data of the grid|
|u_Data|ndarray|No|array that contains the X axis data of the velocity component. ergo U |
|v_Data|ndarray|No|array that contains the Y axis data of the velocity component. ergo V|
|w_Data|ndarray|Yes|array that contains the Z axis data of the velocity component. ergo W|


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



