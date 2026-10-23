#!/usr/bin/env python3
"""Standalone VTK viewer for Grasshopper WRL files.

Called by grasshopper_gui.py when the embedded Tk/VTK widget is unavailable.
Usage:  python grasshopper_vtk_viewer.py <file.wrl>

Press 'x' in the viewer window to export the current view to a vector PDF.
"""

import sys
from pathlib import Path

VECTOR_FORMATS = {".pdf": "PDF", ".svg": "SVG", ".eps": "EPS", ".ps": "PS"}
RASTER_FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".tif": "TIFF"}


def has_vector_export() -> bool:
    import vtk
    return hasattr(vtk, "vtkGL2PSExporter")


def export_scene(window, path: str, sort: str = "bsp", scale: int = 4) -> Path:
    """Write the render window to `path`. Vector via GL2PS, raster via PNG/JPEG/TIFF."""
    import vtk

    p = Path(path)
    ext = p.suffix.lower()
    window.Render()

    if ext in VECTOR_FORMATS:
        if not has_vector_export():
            raise RuntimeError(
                "This VTK build has no vtkGL2PSExporter, so vector output is "
                "unavailable. Export to .png instead.")
        exp = vtk.vtkGL2PSExporter()
        exp.SetRenderWindow(window)
        exp.SetFilePrefix(str(p.with_suffix("")))
        getattr(exp, "SetFileFormatTo" + VECTOR_FORMATS[ext])()
        exp.CompressOff()
        if sort == "bsp":
            exp.SetSortToBSP()
        else:
            exp.SetSortToSimple()
        exp.Write()
        return p

    if ext not in RASTER_FORMATS:
        raise RuntimeError(f"Unsupported export format: {ext or '(none)'}")

    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(window)
    w2i.SetScale(max(1, int(scale)))
    w2i.ReadFrontBufferOff()
    if RASTER_FORMATS[ext] == "PNG":
        w2i.SetInputBufferTypeToRGBA()
    w2i.Update()

    writer = {
        "PNG":  vtk.vtkPNGWriter,
        "JPEG": vtk.vtkJPEGWriter,
        "TIFF": vtk.vtkTIFFWriter,
    }[RASTER_FORMATS[ext]]()
    writer.SetFileName(str(p))
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()
    return p


def view_wrl(path: str) -> None:
    import vtk

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.15, 0.15, 0.15)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(900, 700)
    window.SetWindowName(f"Grasshopper WRL Viewer — {path}   ['x' = export]")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    importer = vtk.vtkVRMLImporter()
    importer.SetFileName(path)
    importer.SetRenderWindow(window)
    importer.Update()

    def on_key(obj, _evt):
        if obj.GetKeySym() not in ("x", "X"):
            return
        ext = ".pdf" if has_vector_export() else ".png"
        src = Path(path)
        out, n = src.with_suffix(ext), 1
        while out.exists():
            out = src.with_name(f"{src.stem}_{n}{ext}")
            n += 1
        try:
            export_scene(window, str(out))
            print(f"Exported view to {out}", flush=True)
        except Exception as e:
            print(f"Export failed: {e}", file=sys.stderr, flush=True)

    interactor.AddObserver("KeyPressEvent", on_key)

    renderer.ResetCamera()
    window.Render()
    print("Press 'x' in the viewer window to export the current view.", flush=True)
    interactor.Initialize()
    interactor.Start()


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in ("--version", "-V"):
        from ._paths import package_version
        print(f"grasshopper-vtk-viewer {package_version()}")
        return 0
    if len(args) < 1 or args[0] in ("-h", "--help"):
        print("Usage: grasshopper-vtk-viewer <file.wrl>\n"
              "Opens a VRML file written by grasshopper (g4_NN.wrl) in an interactive VTK window.\n"
              "Press 'x' in the window to export the current view.", file=sys.stderr)
        return 0 if args else 1
    view_wrl(args[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
