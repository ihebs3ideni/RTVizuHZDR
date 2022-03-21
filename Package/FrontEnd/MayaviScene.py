from traits.api import HasTraits, Instance, observe, Int, Array, Bool
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
    SceneEditor
from mayavi.modules.vectors import Vectors
from mayavi.modules.glyph import Glyph
from mayavi.core.module import Module
from mayavi.core.source import Source
from mayavi.sources.array_source import ArraySource
from mayavi.core.engine import Engine
from mayavi.core.filter import Filter
from mayavi.core.scene import Scene

# from mayavi.api import Engine
import numpy as np
from mayavi import mlab

from mayavi.core.scene import Scene
from abc import ABC, abstractmethod
from typing import Dict, Callable, Tuple, Any, Type, List
from dataclasses import dataclass
from Package.DataStructures.plotDataFormat import VectorGraphData
import uuid

"""colormaps : The 'colormap' trait of a VectorCutPlaneFactory instance must be 'Accent' or 'Blues' or 'BrBG' or 
'BuGn' or 'BuPu' or 'CMRmap' or 'Dark2' or 'GnBu' or 'Greens' or 'Greys' or 'OrRd' or 'Oranges' or 'PRGn' or 'Paired' 
or 'Pastel1' or 'Pastel2' or 'PiYG' or 'PuBu' or 'PuBuGn' or 'PuOr' or 'PuRd' or 'Purples' or 'RdBu' or 'RdGy' or 
'RdPu' or 'RdYlBu' or 'RdYlGn' or 'Reds' or 'Set1' or 'Set2' or 'Set3' or 'Spectral' or 'Vega10' or 'Vega20' or 
'Vega20b' or 'Vega20c' or 'Wistia' or 'YlGn' or 'YlGnBu' or 'YlOrBr' or 'YlOrRd' or 'afmhot' or 'autumn' or 'binary' 
or 'black-white' or 'blue-red' or 'bone' or 'brg' or 'bwr' or 'cool' or 'coolwarm' or 'copper' or 'cubehelix' or 
'file' or 'flag' or 'gist_earth' or 'gist_gray' or 'gist_heat' or 'gist_ncar' or 'gist_rainbow' or 'gist_stern' or 
'gist_yarg' or 'gnuplot' or 'gnuplot2' or 'gray' or 'hot' or 'hsv' or 'inferno' or 'jet' or 'magma' or 
'nipy_spectral' or 'ocean' or 'pink' or 'plasma' or 'prism' or 'rainbow' or 'seismic' or 'spectral' or 'spring' or 
'summer' or 'terrain' or 'viridis' or 'winter', but a value of 'Hot' <class 'str'> was specified """

"""
def loadVelocity(filename):
    M = loadtxt(filename, skiprows=1)
    
    # Get Points and vectors
    points  = M[:,1:4]
    vectors = M[:,4:7]
    
    # The Data
    mesh = tvtk.PolyData(points=points)
    mesh.point_data.vectors = vectors
    
    # Generate VTK data Source
    src = VTKDataSource(data = mesh)
    
    return src

def setGlyph(m):
    g = Glyph()
    m.add_module(g)    
    
    g.glyph.scale_mode = 'scale_by_vector'
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['arrow_source']
    
    # Scale factor:
    g.glyph.glyph.scale_factor = 0.05
    g.glyph.glyph.color_mode = 'color_by_vector'
    
    return g

    


@mayavi2.standalone
def te():
    reko = loadVelocity('veloReko2.dat')
    simul = None
    if (os.path.isfile("velo.reko.dat")):
        simul = loadVelocity("velo.reko.dat")
    
    # Now Do it: 
    mayavi.new_scene()
    mayavi.add_source(reko)
    setGlyph(mayavi)
    
    if (simul != None):
        mayavi.add_source(simul)
        setGlyph(mayavi)
        
  

te()

"""


class BaseMayaviSceneException(Exception):
    """Base High level exception to notify user to errors related to the MayaviScene"""

    def __init__(self, ID: str, obj: Any, message: str):
        self.ID = ID
        self.obj = obj
        self.message = message
        super().__init__(message)

    def __str__(self):
        return "Error Message: %s ; @ Error source ID: %s" % (self.message, self.ID)


class SourceNotInPipelineException(BaseMayaviSceneException):
    """Base High level exception to notify user when a referenced source doesn't exist in the pipeline"""
    pass


class ModuleNotInPipelineException(BaseMayaviSceneException):
    """Base High level exception to notify user when a referenced Module doesn't exist in the pipeline"""
    pass


class FeatureNotSupportedException(BaseMayaviSceneException):
    """Base High level exception to notify user when a feature is Not Supported"""
    pass


@dataclass
class Pipeline_Item:
    """Data structure for providing data to the MayaviFigure API"""
    X: np.ndarray = None
    Y: np.ndarray = None
    Z: np.ndarray = None
    U: np.ndarray = None
    V: np.ndarray = None
    W: np.ndarray = None


class MayaviFigure(HasTraits):
    """mayavi mlab pipeline documentation: https://docs.enthought.com/mayavi/mayavi/auto/mlab_pipeline_other_functions.html"""
    engine = Instance(Engine, args=())
    scene = Instance(MlabSceneModel)

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     show_label=False),  # height=250, width=300, show_label=False),
                resizable=True  # We need this to resize with the parent widget
                )
    pipeline_funcs: Dict[str, Callable] = None
    counter: int = 0  # only used for testing purposes
    Sources: Dict[str, Dict[str, Any]] = None
    Elements: Dict[str, Dict[str, Any]] = None
    preprocessing: Dict[str, List[Callable]] = dict()
    render: Bool = Bool(False)

    updated_frames: Int = Int(0)

    figure: Scene = None

    def __init__(self, **traits):
        super().__init__(**traits)
        self.Sources = dict()
        self.Elements = dict()

    def _scene_default(self):
        """scene default initializer used as a general __init__ in this"""
        self.engine.start()
        scene = MlabSceneModel(engine=self.engine)
        return scene

    def outline(self, srcs: List[Any] = None):
        if srcs is None:
            srcs = self.Sources.keys()
        for src in srcs:
            if type(src) is str:
                self.scene.mlab.outline(self.Sources.get(src).get("mayavi_src"))
            else:
                self.scene.mlab.outline(src)

    def normalize(self, src):
        """returns a normalized version of the reference src """
        if type(src) is str:
            src = self.Sources.get(src)
            if src is None:
                raise SourceNotInPipelineException(ID=repr(src), obj=src,
                                                   message="the referenced source doesn't exist in the pipeline")
        return self.scene.mlab.pipeline.extract_vector_norm(src)

    def AddVFSource(self, pItem: VectorGraphData, ID=None) -> Tuple[ArraySource, str]:
        """a wrapper around mayavi to add a vector field data source in one call and retrieve a reference to the mayavi source
        and it's ID: return mayavi_src, srcID"""
        if ID is None:
            ID = "Vector_field"
        # """run preprocesses on the glyph source"""
        if self.preprocessing.get(ID):
            for p in self.preprocessing[ID]:
                p(pItem)
        self.Sources[ID] = dict(data=pItem,
                                mayavi_src=self.scene.mlab.pipeline.vector_field(pItem.x_Data, pItem.y_Data,
                                                                                 pItem.z_Data,
                                                                                 pItem.u_Data, pItem.v_Data,
                                                                                 pItem.w_Data,
                                                                                 figure=self.engine.current_scene))
        # src:ArraySource = self.Sources[ID].get("mayavi_src")
        # src.transpose_input_array = False

        return self.Sources[ID].get("mayavi_src"), ID

    def AddGlyphSource(self, pItem: VectorGraphData, ID=None) -> Tuple[ArraySource, str]:
        """a wrapper around mayavi to add a grid data source in one call and retrieve a reference to the mayavi Glyph source
         and it's ID: return mayavi_src, srcID"""
        if ID is None:
            ID = "Grid"

        # """run preprocesses on the glyph source"""
        if self.preprocessing.get(ID):
            for p in self.preprocessing[ID]:
                p(pItem)
        self.Sources[ID] = dict(data=pItem,
                                mayavi_src=self.scene.mlab.pipeline.vector_field(pItem.x_Data, pItem.y_Data,
                                                                                 pItem.z_Data,
                                                                                 np.zeros_like(pItem.x_Data),
                                                                                 np.zeros_like(pItem.y_Data),
                                                                                 np.zeros_like(pItem.z_Data),
                                                                                 figure=self.engine.current_scene))
        # src:ArraySource = self.Sources[ID].get("mayavi_src")
        # src.transpose_input_array = False
        return self.Sources[ID].get("mayavi_src"), ID

    def add_glyph(self, ID: str, srcID=None, normalized=False, **kwargs):
        """the source_ID default to Grid for a glyph"""
        if type(srcID) is str:
            srcID = self.Sources.get(srcID)
            if srcID is None:
                raise SourceNotInPipelineException(ID="", obj=self.Grid,
                                                   message="the referenced field doesn't exist in the pipeline")
            srcID = srcID.get("mayavi_src")
        elif srcID is None:
            srcID = "Grid"

        self.Elements[ID] = dict(type="glyph", normalized=normalized, src=None, src_ID=srcID,
                                 args=kwargs, )
        return self.Elements[ID]

    def add_vector_arrows(self, ID: str, srcID=None, normalized=False, **kwargs) -> dict:
        """srcID: can be either a str: the internal ID for a source
                            or  ArraySource: the explicit object returned by addVFSource or addGlyphSource
            it defaults to Vector_field for an arrow field"""
        if type(srcID) is str:
            srcID = self.Sources.get(srcID)
            if srcID is None:
                raise SourceNotInPipelineException(ID=repr(srcID), obj=srcID,
                                                   message="the referenced field doesn't exist in the pipeline")
            srcID = srcID.get("mayavi_src")
        elif srcID is None:
            srcID = "Vector_field"

        self.Elements[ID] = dict(type="arrows", normalized=normalized, src=None, src_ID=srcID,
                                 args=kwargs, )
        return self.Elements[ID]

    def add_cut_plane(self, ID: str, srcID=None, normalized=False, **kwargs) -> dict:
        """srcID: can be either a str: the internal ID for a source
                                   or  ArraySource: the explicit object returned by addVFSource or addGlyphSource
                   it defaults to Vector_field for a cut_plane"""
        if type(srcID) is str:
            srcID = self.Sources.get(srcID)
            if srcID is None:
                raise SourceNotInPipelineException(ID=repr(srcID), obj=srcID,
                                                   message="the referenced field doesn't exist in the pipeline")
            srcID = srcID.get("mayavi_src")
        elif srcID is None:
            srcID = "Vector_field"

        self.Elements[ID] = dict(type="cut_vector_plane", normalized=normalized, src=None, src_ID=srcID,
                                 args=kwargs)
        return self.Elements[ID]

    def add_stream_line(self, ID, srcID=None, normalized=False, **kwargs) -> dict:
        """srcID: can be either a str: the internal ID for a source
                                         or  ArraySource: the explicit object returned by addVFSource or addGlyphSource
                         it defaults to Vector_field for a stream_line"""
        if type(srcID) is str:
            srcID = self.Sources.get(srcID)
            if srcID is None:
                raise SourceNotInPipelineException(ID=repr(srcID), obj=srcID,
                                                   message="the referenced field doesn't exist in the pipeline")
            srcID = srcID.get("mayavi_src")
        elif srcID is None:
            srcID = "Vector_field"

        self.Elements[ID] = dict(type="streamlines", normalized=normalized, mayavi_src=None, src_ID=srcID,
                                 args=kwargs)
        return self.Elements[ID]

    def toggleHideElement(self, IDS: List[Any]):
        """toggles the hide/show property of each referenced module in the list"""
        elem: Module = None
        for ID in IDS:
            if type(ID) is str:
                if self.Elements.get(ID) is None:
                    raise ModuleNotInPipelineException(ID=ID, obj=self.Elements.keys(),
                                                       message="The referenced Module doesn't exist")

                elem = self.Elements.get(ID).get("mayavi_src")

            else:
                elem = ID
            elem._hideshow()

    def update_vector_field(self, pItem, ID: str = None):
        """pItem: VectorGraphData representation of the updated data
            ID: Source ID only necessary if a custom ID is provided at the creation of the vector field Source
                when calling self.AddVFSource"""
        try:
            if ID is None:
                ID = "Vector_field"
            if self.Sources.get(ID) is None:
                raise SourceNotInPipelineException(ID=ID, obj=self.Sources, message="Source is not in pipeline")
            else:
                self.Sources.get(ID)["data"] = pItem
                field = self.Sources.get(ID).get("mayavi_src")
                field.mlab_source.trait_set(x=pItem.x_Data, y=pItem.y_Data, z=pItem.z_Data,
                                            u=pItem.u_Data, v=pItem.v_Data, w=pItem.w_Data)

                self.counter += 1
                self.updated_frames += 1
        except Exception as e:
            import traceback
            print(traceback.format_exc())

    def update_glyph(self, pItem, ID: str = None):
        """pItem: VectorGraphData representation of the updated data
                  ID: Source ID only necessary if a custom ID is provided at the creation of the vector field Source
                      when calling self.AddVFSource"""
        if ID is None:
            ID = "Grid"
        if self.Sources.get(ID) is None:
            raise SourceNotInPipelineException(ID=ID, obj=self.Sources, message="Source is not in pipeline")
        else:
            if self.preprocessing.get(ID):
                for p in self.preprocessing[ID]:
                    p(pItem)
            self.Sources.get(ID)["data"] = pItem
            grid = self.Sources.get(ID).get("mayavi_src")
            grid.mlab_source.trait_set(x=pItem.x_Data, y=pItem.y_Data, z=pItem.z_Data)
            self.updated_frames += 1

    @observe("updated_frames")
    def frame_updated_callback(self, event):
        self.on_frame_updated(event)

    @observe("render")
    def render_cmd(self, event):
        self.pipeline_funcs: Dict[str, Callable] = dict(streamlines=self.scene.mlab.pipeline.streamline,
                                                        arrows=self.scene.mlab.pipeline.vectors,
                                                        cut_vector_plane=self.scene.mlab.pipeline.vector_cut_plane,
                                                        glyph=self.scene.mlab.pipeline.glyph)
        self.create_scene()

    def toggle_render(self):
        self.render = not self.render

    # @observe('scene.activated')
    # def init_plot(self, event):
    #     # print(event)
    #     # self.__active = True
    #     self.pipeline_funcs: Dict[str, Callable] = dict(streamlines=self.scene.mlab.pipeline.streamline,
    #                                                     arrows=self.scene.mlab.pipeline.vectors,
    #                                                     cut_vector_plane=self.scene.mlab.pipeline.vector_cut_plane,
    #                                                     glyph=self.scene.mlab.pipeline.glyph)
    #     print(self.figure)
    #     self.create_scene()

    @abstractmethod
    def on_frame_updated(self, event):
        pass

    @abstractmethod
    def create_scene(self):
        for id, conf in self.Elements.items():
            func = self.pipeline_funcs.get(conf["type"])
            if func is None:
                raise FeatureNotSupportedException(ID=id, obj=conf["type"],
                                                   message="the requested feature is not supported")
            data_source = conf.get("src_ID")
            if data_source is None:
                raise SourceNotInPipelineException(ID=id, obj=conf,
                                                   message="the referenced data source isn't in the pipeline")
            elif type(data_source) is str:
                data_source = self.Sources.get(data_source).get("mayavi_src")
            # src_id = conf.get("src_ID")
            if conf.get("normalized"):
                data_source = self.normalize(data_source)
            args = conf.get("args")
            if conf.get("mayavi_src") is None:
                pass
                conf["mayavi_src"] = func(data_source, **args)

    def set_onClicked_callback(self, callback: Callable):
        """API call to set an on scene clicked callback"""
        self.engine.current_scene.on_mouse_pick(callback)

    def add_preprocess(self, source_id, func: Callable):
        """appends a preoprcess function to the list, these preprocesses will be ran on the data before plotting it"""
        if self.preprocessing.get(source_id) is None:
            self.preprocessing[source_id] = []
        self.preprocessing[source_id].append(func)
        # self.preprocessing.append(func)

    def suported_pipeline_items(self):
        """returns the supported figures and shapes of the wrapper API"""
        return list(self.pipeline_funcs.keys())

    def get_UI(self, parent):
        """returns the UI Element to be embedded in a custom UI"""
        return self.edit_traits(parent=parent, kind='subpanel').control

    """mayavi api to add modules, sources abd filters directly to the scene engine"""

    def add_module(self, mod: Module):
        """Uses the internal mechanisms of mayavi and should be used as the mayavi api to directly add modules to the scene engine"""
        self.engine.add_module(mod=mod)

    def add_source(self, src: Source):
        """Uses the internal mechanisms of mayavi and should be used as the mayavi api to directly add sources to the scene engine"""
        self.engine.add_source(src=src)

    def add_filter(self, fil: Filter):
        """Uses the internal mechanisms of mayavi and should be used as the mayavi api to directly add filters to the scene engine"""
        self.engine.add_filter(fil=fil)

    @staticmethod
    def get_pipelineitem_struct() -> Type[VectorGraphData]:
        """returns the data type used to group data for the Wrapper API"""
        return VectorGraphData


if __name__ == '__main__':
    # The QWidget containing the visualization, this is pure PyQt4 code.
    from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QGridLayout, QApplication, \
        QPushButton
    from PyQt5.QtCore import QTimer


    class MayaviQWidget(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.visualization = MayaviFigure()
            # self.visualization.set_onClicked_callback(lambda : print("clicked"))
            pItem = self.visualization.get_pipelineitem_struct()

            x, y, z = np.mgrid[-10:10, -10:10, -4:4]
            field_data = pItem(x_Data=x, y_Data=y, z_Data=z, u_Data=np.cos(x), v_Data=np.sin(y),
                               w_Data=np.ones_like(z) * 0.5)
            grid_data = pItem(x_Data=x, y_Data=y, z_Data=z, u_Data=np.zeros_like(x), v_Data=np.zeros_like(y),
                              w_Data=np.zeros_like(z))
            # self.visualization.add_preprocess("Vector_field", print)
            vf, vf_id = self.visualization.AddVFSource(field_data)

            sf, sf_id = self.visualization.AddGlyphSource(grid_data)
            # self.visualization.outline([vf])
            self.visualization.outline(["Grid"])
            self.visualization.add_glyph("grid", scale_factor=0.05, color=(0, 0, 0))
            self.visualization.add_vector_arrows("field", srcID=vf_id, normalized=True,
                                                 line_width=2,
                                                 # color=(0, 0, 0),
                                                 scale_factor=0.5,
                                                 scale_mode="vector",
                                                 colormap="coolwarm")
            self.visualization.add_cut_plane("fieled_plane", srcID=vf, normalized=False,
                                             scale_factor=1,
                                             colormap='jet',
                                             # seed_visible=False,
                                             plane_orientation='y_axes')
            self.visualization.add_stream_line("field_lines", srcID=vf_id, normalized=True,
                                               # seed_visible=False,
                                               seed_scale=0.5,
                                               seed_resolution=10,
                                               linetype='line',
                                               colormap="Accent")

            # If you want to debug, beware that you need to remove the Qt
            # input hook.
            # QtCore.pyqtRemoveInputHook()
            # import pdb ; pdb.set_trace()
            # QtCore.pyqtRestoreInputHook()

            # The edit_traits call will generate the widget to embed.
            self.ui = self.visualization.get_UI(parent=self)
            layout.addWidget(self.ui)
            # self.ui.setParent(self)


    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication.instance()
    container = QWidget()
    container.setWindowTitle("Embedding Mayavi in a PyQt4 Application")
    # define a "complex" layout to test the behaviour
    layout = QGridLayout(container)


    def update_G(graph: MayaviFigure):
        if (graph):
            try:
                field_data = graph.Sources.get("Vector_field")
                # print(type(field_data.get("data")))
                field_data = field_data.get("data")
                # u = np.cos(field_data.X + graph.counter * 0.1)*np.random.random()*np.random.randint(1,size=1, high=10)
                # self.graph.mlab_source.u = np.cos(self.x + self.counter * 0.1)
                # v = -1 * np.sin(field_data.Y + graph.counter * 0.1)*np.random.random()*np.random.randint(1, size=1, high=10)
                # w = np.cos(graph.z + graph.counter * 0.1)
                # u = np.random.random(graph.x.shape)
                # v = np.random.random(graph.y.shape)
                # w = np.cos(field_data.Z + graph.counter * 0.1)*np.random.random()*np.random.randint(1,size=1, high=10)
                ds = graph.get_pipelineitem_struct()

                glyph_data = graph.Sources.get("Vector_field")

                glyph_data = glyph_data.get("data")
                x = glyph_data.x_Data
                y = glyph_data.y_Data
                z = glyph_data.z_Data
                u = np.cos(x + graph.counter * 0.1) * np.random.uniform(0.1, 2)
                # self.graph.mlab_source.u = np.cos(self.x + self.counter * 0.1)
                v = -1 * np.sin(y + graph.counter * 0.1) * np.random.uniform(0.1, 2)
                # w = np.cos(graph.z + graph.counter * 0.1)
                # u = np.random.random(graph.x.shape)
                # v = np.random.random(graph.y.shape)
                w = field_data.w_Data

                graph.update_vector_field(ds(x_Data=x, y_Data=y, z_Data=z, u_Data=u, v_Data=v, w_Data=w))
                # graph.update_glyph(ds(X=x, Y=y, Z=z))
                # graph.outline()
                # w = np.random.random(graph.z.shape)
                # graph.update_callback(u, v, w)
            # graph.counter += 1
            except Exception as e:
                import traceback
                print(traceback.format_exc())



    def rem_add_cb(button: QPushButton, graph: MayaviFigure):
        # graph.set_onClicked_callback(print)
        if button.text() == "Hide":
            button.setText("Show")
        #     graph.removeElement("field")
        elif button.text() == "Show":
            button.setText("Hide")
        #     graph.add_vector_arrows("field", normalized=True, mask_points=40,
        #                       line_width=1,
        #                       color=(0, 0, 0),
        #                       scale_factor=1., )
        # else:
        #     print("text not recognized")
        graph.toggleHideElement(["field", "fieled_plane"])


    mayavi_widget = MayaviQWidget(container)
    b = QPushButton("Update")
    b2 = QPushButton("Hide")
    t = QTimer()
    t.timeout.connect(lambda *args: update_G(mayavi_widget.visualization))
    b.pressed.connect(lambda *args: t.start(1000))
    b2.pressed.connect(lambda: rem_add_cb(button=b2, graph=mayavi_widget.visualization))
    layout.addWidget(mayavi_widget, 2, 1)
    layout.addWidget(b, 0, 1)
    layout.addWidget(b2, 1, 1)
    container.show()
    window = QMainWindow()
    window.setCentralWidget(container)
    window.show()

    # Start the main event loop.
    app.exec_()

#
# if __name__ == '__main__':
#     import numpy as np
#     from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QGridLayout, QApplication, \
#         QPushButton
#
#     a = np.random.random((4, 4))
#     from mayavi.api import Engine
#
#     app = QApplication.instance()
#     e = Engine()
#     e.start()
#     s = e.new_scene()
#     from mayavi.sources.api import ArraySource
#
#     src = ArraySource(scalar_data=a)
#     e.add_source(src)
#     from mayavi.filters.api import WarpScalar, PolyDataNormals
#
#     warp = WarpScalar()
#     e.add_filter(warp, obj=src)
#     normals = PolyDataNormals()
#     e.add_filter(normals, obj=warp)
#     from mayavi.modules.api import Surface, Vectors
#
#     surf = Surface()
#     vect = Vectors()
#     e.add_module(surf, obj=normals)
#     e.add_module(vect, obj=src)
#     e.add_module(vect, obj=normals)
#     app.exec_()
