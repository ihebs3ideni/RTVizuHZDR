from Package.FrontEnd.BaseInterface import BaseGraphCanvas, BaseGraphException
from Package.DataStructures.GraphArgsStructure import GraphStructure, ElementStructure
from Package.FrontEnd.MayaviScene import MayaviFigure, SourceNotInPipelineException, FeatureNotSupportedException, \
    ModuleNotInPipelineException, BaseMayaviSceneException, Pipeline_Item
from Package.DataStructures.plotDataFormat import VectorGraphData
import vtk

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget, QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from typing import List, Any, Dict, Callable

import numpy as np


class MayaviBaseGraph(BaseGraphCanvas):
    checkBoxLayout: QHBoxLayout = None

    def create_canvas(self):
        self.dynamic_canvas: MayaviFigure = MayaviFigure()
        self.UI = self.dynamic_canvas.get_UI(parent=self)
        layout = QVBoxLayout(self)
        self.checkBoxLayout = QHBoxLayout(self)
        layout.addLayout(self.checkBoxLayout)
        layout.addWidget(self.UI)
        self.setLayout(layout)
        # self.set_xy_lim()

    def set_onclicked_callback(self, callback: Callable):
        self.dynamic_canvas.set_onClicked_callback(callback)


class MayaviDynamicGraph(MayaviBaseGraph):
    visibleFeatures: Dict[str, QCheckBox] = None

    def __init__(self, structure: GraphStructure, spawning_position: int = None):
        super().__init__(structure, spawning_position)
        self.create_canvas()
        self.visibleFeatures = dict()
        vtk_out = vtk.vtkOutputWindow()
        vtk_out.SetInstance(vtk_out)
        # errOut = vtk.vtkFileOutputWindow()
        # errOut.SetFileName("Package/log.txt")
        # vtkStdErrOut = vtk.vtkOutputWindow()
        # vtkStdErrOut.SendToStdErrOn()
        # vtkStdErrOut.SetInstance(errOut)
        for id_, e in self.structure.elements.items():
            # print(id_)
            pItem = self.get_data_container()
            """this assumes that x, y and z are created using np.mgrid"""

            field_data = pItem(x_Data=e.X, y_Data=e.Y, z_Data=e.Z, u_Data=np.cos(e.X), v_Data=np.sin(e.Y),
                               w_Data=np.ones_like(e.Z) * 0.5)
            grid_data = pItem(x_Data=e.X, y_Data=e.Y, z_Data=e.Z, u_Data=np.zeros_like(e.X), v_Data=np.zeros_like(e.X),
                              w_Data=np.zeros_like(e.X))
            vf, vf_id = self.dynamic_canvas.AddVFSource(field_data)
            sf, sf_id = self.dynamic_canvas.AddGlyphSource(grid_data)

            self.checkBoxLayout.addStretch()
            if e.hasVectorField:
                self.dynamic_canvas.add_vector_arrows(id_ + "_field", srcID=vf_id, normalized=True,
                                                      line_width=2,
                                                      # color=(0, 0, 0),
                                                      scale_factor=0.5,
                                                      scale_mode="vector",
                                                      colormap="coolwarm")
                self.visibleFeatures["vectorField"] = QCheckBox("Vector field")
                self.visibleFeatures["vectorField"].setChecked(True)
                self.visibleFeatures["vectorField"].stateChanged.connect(
                    lambda: self.dynamic_canvas.toggleHideElement([id_ + "_field"]))
                self.checkBoxLayout.addWidget(self.visibleFeatures["vectorField"])
            if e.hasGrid:
                self.dynamic_canvas.add_glyph(id_ + "_grid", scale_factor=0.05, color=(0, 0, 0))
                self.visibleFeatures["grid"] = QCheckBox("Grid")
                self.visibleFeatures["grid"].setChecked(True)
                self.visibleFeatures["grid"].stateChanged.connect(
                    lambda: self.dynamic_canvas.toggleHideElement([id_ + "_grid"]))
                self.checkBoxLayout.addWidget(self.visibleFeatures["grid"])
            if e.hasCutPlane:
                self.dynamic_canvas.add_cut_plane(id_ + "field_plane", srcID=vf, normalized=False,
                                                  scale_factor=1,
                                                  colormap='jet',
                                                  # seed_visible=False,
                                                  plane_orientation='y_axes')
                self.visibleFeatures["field_plane"] = QCheckBox("Cut Plane")
                self.visibleFeatures["field_plane"].setChecked(True)
                self.visibleFeatures["field_plane"].stateChanged.connect(
                    lambda: self.dynamic_canvas.toggleHideElement([id_ + "field_plane"]))
                self.checkBoxLayout.addWidget(self.visibleFeatures["field_plane"])
            if e.hasStreamLines:
                self.dynamic_canvas.add_stream_line(id_ + "field_lines", srcID=vf_id, normalized=True,
                                                    # seed_visible=False,
                                                    seed_scale=0.5,
                                                    seed_resolution=10,
                                                    linetype='line',
                                                    colormap="Accent")
                self.visibleFeatures["streamlines"] = QCheckBox("Streamlines")
                self.visibleFeatures["streamlines"].setChecked(True)
                self.visibleFeatures["streamlines"].stateChanged.connect(
                    lambda: self.dynamic_canvas.toggleHideElement([id_ + "field_lines"]))
                self.checkBoxLayout.addWidget(self.visibleFeatures["streamlines"])
            self.checkBoxLayout.addStretch()
            self.dynamic_canvas.outline()
        self.dynamic_canvas.toggle_render()


    def onUpdatePlot(self, data: Pipeline_Item):
        """TODO: @Iheb: fix this to support multiple sources with IDs"""
        self.dynamic_canvas.update_vector_field(data)

    def add_hLine(self, coordinates: List[float], xmin: List[float], xmax: List[float], **kwargs):
        pass

    def add_vLine(self, coordinates: List[float], ymin: List[float], ymax: List[float], **kwargs):
        pass

    def set_y_lim(self, downtLim, upLim):
        pass

    def set_x_lim(self, downtLim, upLim):
        pass

    def clearPlot(self):
        pass

    @staticmethod
    def get_data_container():
        return MayaviFigure.get_pipelineitem_struct()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    def update_(graph: MayaviDynamicGraph):
        try:
            DS = graph.get_data_container()
            X, Y, Z = np.mgrid[-10:10, -10:10, -4:4]
            graph.updateFigure(
                DS(x_Data=X, y_Data=Y, z_Data=Z,
                   u_Data=np.random.random(X.shape),
                   v_Data=np.random.random(Y.shape),
                   w_Data=np.random.random(Z.shape)))
        except Exception as e:
            import traceback
            print(traceback.format_exc())


    x, y, z = np.mgrid[-10:10, -10:10, -4:4]
    structure = [GraphStructure(ID="test Graph %d" % i, blit=True, grid=True, yLim=(1, -1),
                                elements={str(i): ElementStructure(X=x, Y=y, Z=z, hasGrid=True, hasStreamLines=True,
                                                                   hasVectorField=True, hasCutPlane=True,
                                                                   )}) for i in range(4)]
    qapp = QApplication(sys.argv)
    bgc = [MayaviDynamicGraph(structure[i - 1], spawning_position=i) for i in range(1, 5)]
    for b in bgc:
        b.set_onclicked_callback(lambda event, graph=b: update_(graph))
        b.show()
    qapp.exec_()
