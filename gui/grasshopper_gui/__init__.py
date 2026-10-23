"""grasshopper-gui: a Tkinter front end for the grasshopper Geant4 simulation.

Entry points (installed as console scripts):
  grasshopper-gui          full GUI with embedded VTK visualization (if vtk is installed)
  grasshopper-gui-novis    same GUI without the visualization tab
  grasshopper-vtk-viewer   standalone viewer for the g4_NN.wrl files grasshopper writes
"""

from ._paths import package_version

__version__ = package_version()

__all__ = ["__version__"]
