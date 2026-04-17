# Grasshopper GUI

A Python/Tkinter frontend for the [Grasshopper](https://github.com/mit-quest/grasshopper) Geant4 simulation toolkit.  
The GUI lets you define a simulation, generate the GDML input file, run Grasshopper, and inspect the results — all without touching the command line or editing XML by hand.

## Requirements

| Dependency | Purpose | How to install |
|---|---|---|
| Python 3.8+ | runtime | — |
| **tkinter** | GUI framework (stdlib, but needs system lib) | see below |
| matplotlib ≥ 3.5 | Analysis tab histograms | `pip install matplotlib` |
| numpy ≥ 1.21 | Analysis tab histograms | `pip install numpy` |
| vtk ≥ 9.0 *(optional)* | 3D WRL preview | `pip install vtk` |

### Installing tkinter

tkinter ships with Python but requires a native library that some distributions omit:

```bash
# macOS (Homebrew) — match the version to your Python
brew install python-tk@3.13

# Debian / Ubuntu
sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter
```

### Install Python dependencies

```bash
pip install -r gui/requirements.txt
```

## Running

```bash
python3 gui/grasshopper_gui.py
```

The GUI saves all settings to `gui/grasshopper_gui_settings.json` when you close the window and restores them on the next launch.

## Tabs

### 1 · Beam & Physics
Define the primary particle (electron, gamma, neutron, proton, alpha), beam energy, number of events, random seed, beam size and offsets, and physics production cuts.

### 2 · Output Options
Toggle ASCII text output (`.dat`), brief vs. full column format, VRML visualization output, and the three data-filter flags (`SaveSurfaceHitTrack`, `SaveTrackInfo`, `SaveEdepositedTotalEntry`).

### 3 · Geometry
Define the world volume (box dimensions + material) and add an arbitrary number of sub-volumes (Box, Tube, or Sphere) with material, position, rotation, and an optional "is detector" flag.  Volumes flagged as detectors receive a `det_phys` physvol name, which is required for Grasshopper to register them as sensitive volumes.  Double-click a row to edit it.

### 4 · GDML
Click **Generate GDML** to build the GDML file from the current form values and save it automatically to `default.gdml` in the working directory (the Run tab's GDML field is updated automatically).  Use **Save as…** to write to a different path.  The text widget shows the full generated XML for review.

### 5 · Run
Set the path to the `grasshopper` executable, the GDML input file, and the ROOT output file.  Click **▶ Run simulation** to launch the process; stdout/stderr stream into the log window in real time.  **■ Stop** sends SIGTERM.  After a successful run the WRL and `.dat` output files are loaded automatically.

### 6 · Visualization
Inspect the VRML geometry/track file produced by Grasshopper (`VRMLvisualizationOn = 1`).

- **Find latest** scans the working directory for `g4_*.wrl` files and selects the most recently modified one.
- **Open in viewer** passes the file to a configurable external program (`open` on macOS, `xdg-open` on Linux, `start` on Windows, or any custom path such as `paraview`).
- **3D preview** — if `vtk` is installed and was built with Tk rendering support, an interactive viewport is embedded directly in the tab (trackball-camera mouse navigation).  If `libvtkRenderingTk` is unavailable (e.g. the ROOT-bundled VTK build), a **Open 3D view (VTK window)** button launches `grasshopper_vtk_viewer.py` as a subprocess instead, opening a standalone VTK window.

### 7 · Analysis
Load a `.dat` output file (auto-loaded after each run) and plot any column as a histogram.

| Control | Description |
|---|---|
| **Column** | Column to histogram (auto-detected from file; brief and full formats supported) |
| **Bins** | Number of histogram bins |
| **Log Y** | Toggle logarithmic Y axis |
| **Filter 1 / 2** | Row filters: select a column and min/max values; only rows passing both filters are plotted.  Leave column or limits blank to disable. |

The navigation toolbar below the plot (pan, zoom, save) is provided by matplotlib.

## GDML notes

The generator writes `<quantity>` tags (with units) for `BeamEnergy`, `BeamSize`, `BeamOffset*`, and `ProductionLowLimit`, matching the format that Grasshopper's GDML parser expects.  All other simulation constants use `<constant>` tags.

Materials labelled `G4_*` (e.g. `G4_AIR`, `G4_Pb`) are referenced by name without a definition block — Geant4's GDML parser resolves them from the NIST database automatically.  Custom materials (Air, Iron, NaI, etc.) have full element and material definitions generated automatically.

## Files

| File | Purpose |
|---|---|
| `grasshopper_gui.py` | Main application |
| `grasshopper_vtk_viewer.py` | Standalone VTK window, launched as subprocess when embedded Tk/VTK is unavailable |
| `requirements.txt` | Python dependencies |
| `grasshopper_gui_settings.json` | Auto-generated; stores session settings |
| `grasshopper_gui_novisualization.py` | Same, but without the vtk/visualization |
