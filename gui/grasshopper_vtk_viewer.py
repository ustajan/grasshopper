#!/usr/bin/env python3
"""Standalone VTK viewer for Grasshopper WRL files.

Called by grasshopper_gui.py when the embedded Tk/VTK widget is unavailable.
Usage:  python grasshopper_vtk_viewer.py <file.wrl>
"""

import sys


def view_wrl(path: str) -> None:
    import vtk

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.15, 0.15, 0.15)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(900, 700)
    window.SetWindowName(f"Grasshopper WRL Viewer — {path}")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    importer = vtk.vtkVRMLImporter()
    importer.SetFileName(path)
    importer.SetRenderWindow(window)
    importer.Update()

    renderer.ResetCamera()
    window.Render()
    interactor.Initialize()
    interactor.Start()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: grasshopper_vtk_viewer.py <file.wrl>", file=sys.stderr)
        sys.exit(1)
    view_wrl(sys.argv[1])
