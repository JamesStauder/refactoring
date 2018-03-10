from dolfin import project
from ..constants import *
from ModelLegend import *


class ModelPlotter(object):
    def __init__(self, strs, mesh, plot1, plot2, plot3, t0, dt):
        self.run = True
        self.strs = strs
        self.mesh = mesh
        self.x = mesh.coordinates().flatten()
        S = project(strs.H0+strs.B)
        TD = project(self.strs.tau_d_plot)
        TB = project(self.strs.tau_b_plot)
        TX = project(self.strs.tau_xx_plot)
        TY = project(self.strs.tau_xy_plot)
        TZ = project(self.strs.tau_xz_plot)

        self.plot1 = plot1
        self.plot1.showGrid(x=True, y=True)

        self.ph0 = self.plot1.plot(self.x, self.strs.B.compute_vertex_values(), pen=bluePlotPen)
        self.ph100 = self.plot1.plot(self.x, S.compute_vertex_values(), pen=redPlotPen)
        self.ph1 = self.plot1.plot(self.x, S.compute_vertex_values(), pen=whitePlotPen)

        self.legend1 = ModelLegend(offset=(-50, 50))
        self.legend1.setParentLayoutItem(self.plot1.graphicsItem())
        self.legend1.addItem(self.ph0, '<i>B</i>')
        self.legend1.addItem(self.ph100, '<i>S</i><sub>o</sub>')
        self.legend1.addItem(self.ph1, '<i>S</i>')

        self.plot2 = plot2
        self.plot2.showGrid(x=True, y=True)

        self.ph2 = self.plot2.plot(self.x, TD.compute_vertex_values(), pen=bluePlotPen)
        self.ph3 = self.plot2.plot(self.x, TB.compute_vertex_values(), pen=greenPlotPen)
        self.ph4 = self.plot2.plot(self.x, TX.compute_vertex_values(), pen=redPlotPen)
        self.ph5 = self.plot2.plot(self.x, TY.compute_vertex_values(), pen=tealPlotPen)
        self.ph6 = self.plot2.plot(self.x, TZ.compute_vertex_values(), pen=pinkPlotPen)

        self.legend2 = ModelLegend(offset=(-50, 50))
        self.legend2.setParentItem(self.plot2.graphicsItem())
        self.legend2.addItem(self.ph2, '&tau;<sub>d</sub>')
        self.legend2.addItem(self.ph3, '&tau;<sub>b</sub>')
        self.legend2.addItem(self.ph4, '&tau;<sub>xx</sub>')
        self.legend2.addItem(self.ph5, '&tau;<sub>xy</sub>')
        self.legend2.addItem(self.ph6, '&tau;<sub>xz</sub>')

        self.plot3 = plot3
        self.plot3.showGrid(x=True, y=True)
        self.legend3 = ModelLegend(offset=(-50, 50))
        self.legend3.setParentItem(self.plt3.graphicsItem())

        us = project(self.strs.u(0))
        ub = project(self.strs.u(1))

        self.ph7 = self.plt3.plot(self.x, us.compute_vertex_values(), pen=bluePlotPen)
        self.ph8 = self.plt3.plot(self.x, ub.compute_vertex_values(), pen=greenPlotPen)
        self.legend3.addItem(self.ph7, '&mu;<sub>s</sub>')
        self.legend3.addItem(self.ph8, '&mu;<sub>b</sub>')
