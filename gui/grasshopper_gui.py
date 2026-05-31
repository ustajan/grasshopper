#!/usr/bin/env python3
"""Grasshopper GUI — Python/Tkinter frontend for the Grasshopper Geant4 simulation.

Requires: Python 3.8+, tkinter (stdlib)
Optional: matplotlib, numpy  (needed for the Analysis tab)

Usage:
    python grasshopper_gui.py
"""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_SETTINGS_PATH = Path(__file__).parent / "grasshopper_gui_settings.json"

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import vtk
    from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
    HAS_VTK = True
except Exception:
    HAS_VTK = False


# ── Dark theme palette ────────────────────────────────────────────────────────

_DARK = {
    "bg":     "#1e1e1e",   # root / notebook background
    "bg2":    "#2d2d2d",   # panel / button background
    "bg3":    "#3a3a3a",   # hover / active
    "fg":     "#dcdcdc",   # primary text
    "fg_dim": "#7a7a7a",   # hints / secondary text
    "entry":  "#252525",   # text-entry / text-widget background
    "sel":    "#3a6ea8",   # selection blue
    "border": "#444444",   # borders / separators
    "accent": "#5a9e5a",   # green (grasshopper!)
}


def _apply_dark_theme(root: tk.Tk) -> None:
    """Configure ttk styles and root background for night mode."""
    D = _DARK
    root.configure(bg=D["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=D["bg"], foreground=D["fg"],
        fieldbackground=D["entry"],
        bordercolor=D["border"],
        darkcolor=D["bg"], lightcolor=D["bg2"],
        troughcolor=D["bg2"],
        selectbackground=D["sel"], selectforeground=D["fg"],
        insertcolor=D["fg"],
    )
    style.configure("TFrame",          background=D["bg"])
    style.configure("TLabel",          background=D["bg"],  foreground=D["fg"])
    style.configure("TLabelframe",     background=D["bg"],  bordercolor=D["border"])
    style.configure("TLabelframe.Label", background=D["bg"], foreground=D["fg"])
    style.configure("TSeparator",      background=D["border"])
    style.configure("TButton",
        background=D["bg2"], foreground=D["fg"],
        bordercolor=D["border"], focuscolor=D["bg2"], padding=4)
    style.map("TButton",
        background=[("active", D["bg3"]), ("pressed", D["bg3"])],
        relief=[("pressed", "sunken")])
    style.configure("TEntry",
        fieldbackground=D["entry"], foreground=D["fg"],
        bordercolor=D["border"], insertcolor=D["fg"])
    style.configure("TCombobox",
        fieldbackground=D["entry"], foreground=D["fg"],
        background=D["bg2"], bordercolor=D["border"], arrowcolor=D["fg"])
    style.map("TCombobox",
        fieldbackground=[("readonly", D["entry"])],
        selectbackground=[("readonly", D["sel"])])
    style.configure("TCheckbutton",
        background=D["bg"], foreground=D["fg"],
        indicatorbackground=D["entry"], indicatorforeground=D["fg"])
    style.map("TCheckbutton",
        background=[("active", D["bg"])],
        indicatorcolor=[("selected", D["accent"])])
    style.configure("TNotebook",       background=D["bg"],  bordercolor=D["border"])
    style.configure("TNotebook.Tab",
        background=D["bg2"], foreground=D["fg"],
        padding=[10, 4], bordercolor=D["border"])
    style.map("TNotebook.Tab",
        background=[("selected", D["bg"]), ("active", D["bg3"])],
        foreground=[("selected", D["accent"])])
    style.configure("TScrollbar",
        background=D["bg2"], troughcolor=D["bg"],
        bordercolor=D["border"], arrowcolor=D["fg"])
    style.map("TScrollbar", background=[("active", D["bg3"])])
    style.configure("Treeview",
        background=D["entry"], foreground=D["fg"],
        fieldbackground=D["entry"], bordercolor=D["border"])
    style.configure("Treeview.Heading",
        background=D["bg2"], foreground=D["fg"],
        bordercolor=D["border"], relief="flat")
    style.map("Treeview",
        background=[("selected", D["sel"])],
        foreground=[("selected", D["fg"])])
    style.map("Treeview.Heading",
        background=[("active", D["bg3"])])


# ── Material library ──────────────────────────────────────────────────────────
# Each entry: density_g_cm3, [(element_symbol, fraction), ...], state
# Elements: symbol -> (Z, atomic_mass_g_mol)

_ELEMENTS: Dict[str, Tuple[int, float]] = {
    "H":  (1,  1.008),  "C":  (6,  12.011), "N":  (7,  14.007),
    "O":  (8,  15.999), "Na": (11, 22.990), "Al": (13, 26.982),
    "Si": (14, 28.086), "B":  (5,  10.811), "Fe": (26, 55.845),
    "Cu": (29, 63.546), "W":  (74, 183.84), "Pb": (82, 207.20),
    "I":  (53, 126.90),
}

_CUSTOM_MATERIALS: Dict[str, tuple] = {
    "Air":          (1.293e-3, [("N", 0.7),     ("O",  0.3)],                       "gas"),
    "Vacuum":       (1e-25,    [("N", 0.7),     ("O",  0.3)],                       "gas"),
    "Iron":         (7.874,    [("Fe", 1.0)],                                        "solid"),
    "Lead":         (11.35,    [("Pb", 1.0)],                                        "solid"),
    "Aluminum":     (2.699,    [("Al", 1.0)],                                        "solid"),
    "Copper":       (8.960,    [("Cu", 1.0)],                                        "solid"),
    "Tungsten":     (19.30,    [("W",  1.0)],                                        "solid"),
    "Silicon":      (2.329,    [("Si", 1.0)],                                        "solid"),
    "Water":        (1.000,    [("H",  0.1119), ("O",  0.8881)],                    "liquid"),
    "NaI":          (3.670,    [("Na", 0.1534), ("I",  0.8466)],                    "solid"),
    "PlasticScint": (1.032,    [("C",  0.9146), ("H",  0.0854)],                    "solid"),
    "BoratedPoly":  (1.000,    [("H",  0.1314), ("C",  0.6234),
                                ("B",  0.0500), ("O",  0.1952)],                    "solid"),
}

# G4 NIST materials: referenced by name only — no definition block needed in GDML.
# Listed in two groups: simple elements (Z = 1..98, periodic-table order) followed by
# compounds and mixtures (alphabetical by leading letter).
_G4_ELEMENTS = [
    "G4_H",  "G4_He", "G4_Li", "G4_Be", "G4_B",  "G4_C",  "G4_N",  "G4_O",  "G4_F",  "G4_Ne",
    "G4_Na", "G4_Mg", "G4_Al", "G4_Si", "G4_P",  "G4_S",  "G4_Cl", "G4_Ar", "G4_K",  "G4_Ca",
    "G4_Sc", "G4_Ti", "G4_V",  "G4_Cr", "G4_Mn", "G4_Fe", "G4_Co", "G4_Ni", "G4_Cu", "G4_Zn",
    "G4_Ga", "G4_Ge", "G4_As", "G4_Se", "G4_Br", "G4_Kr", "G4_Rb", "G4_Sr", "G4_Y",  "G4_Zr",
    "G4_Nb", "G4_Mo", "G4_Tc", "G4_Ru", "G4_Rh", "G4_Pd", "G4_Ag", "G4_Cd", "G4_In", "G4_Sn",
    "G4_Sb", "G4_Te", "G4_I",  "G4_Xe", "G4_Cs", "G4_Ba", "G4_La", "G4_Ce", "G4_Pr", "G4_Nd",
    "G4_Pm", "G4_Sm", "G4_Eu", "G4_Gd", "G4_Tb", "G4_Dy", "G4_Ho", "G4_Er", "G4_Tm", "G4_Yb",
    "G4_Lu", "G4_Hf", "G4_Ta", "G4_W",  "G4_Re", "G4_Os", "G4_Ir", "G4_Pt", "G4_Au", "G4_Hg",
    "G4_Tl", "G4_Pb", "G4_Bi", "G4_Po", "G4_At", "G4_Rn", "G4_Fr", "G4_Ra", "G4_Ac", "G4_Th",
    "G4_Pa", "G4_U",  "G4_Np", "G4_Pu", "G4_Am", "G4_Cm", "G4_Bk", "G4_Cf",
]

_G4_COMPOUNDS = [
    # Numbered
    "G4_1,2-DICHLOROBENZENE", "G4_1,2-DICHLOROETHANE",
    # A
    "G4_A-150_TISSUE", "G4_ACETONE", "G4_ACETYLENE", "G4_ADENINE",
    "G4_ADIPOSE_TISSUE_ICRP", "G4_AIR", "G4_ALANINE", "G4_ALUMINUM_OXIDE",
    "G4_AMBER", "G4_AMMONIA", "G4_ANILINE", "G4_ANTHRACENE",
    # B
    "G4_B-100_BONE", "G4_BAKELITE", "G4_BARIUM_FLUORIDE", "G4_BARIUM_SULFATE",
    "G4_BENZENE", "G4_BERYLLIUM_OXIDE", "G4_BGO", "G4_BLOOD_ICRP",
    "G4_BONE_COMPACT_ICRU", "G4_BONE_CORTICAL_ICRP", "G4_BORON_CARBIDE",
    "G4_BORON_OXIDE", "G4_BRAIN_ICRP", "G4_BRASS", "G4_BRONZE", "G4_BUTANE",
    # C
    "G4_C-552", "G4_CADMIUM_TELLURIDE", "G4_CADMIUM_TUNGSTATE",
    "G4_CALCIUM_CARBONATE", "G4_CALCIUM_FLUORIDE", "G4_CALCIUM_OXIDE",
    "G4_CALCIUM_SULFATE", "G4_CALCIUM_TUNGSTATE", "G4_CARBON_DIOXIDE",
    "G4_CARBON_TETRACHLORIDE", "G4_CELLULOSE_BUTYRATE",
    "G4_CELLULOSE_CELLOPHANE", "G4_CELLULOSE_NITRATE", "G4_CERIC_SULFATE",
    "G4_CESIUM_FLUORIDE", "G4_CESIUM_IODIDE", "G4_CHLOROBENZENE",
    "G4_CHLOROFORM", "G4_CONCRETE", "G4_CR39", "G4_CYCLOHEXANE", "G4_CYTOSINE",
    # D
    "G4_DACRON", "G4_DICHLORODIETHYL_ETHER", "G4_DIETHYL_ETHER",
    "G4_DIMETHYL_SULFOXIDE", "G4_DNA_A", "G4_DNA_ADENINE", "G4_DNA_ADENOSINE",
    "G4_DNA_C", "G4_DNA_CYTIDINE", "G4_DNA_CYTOSINE", "G4_DNA_G",
    "G4_DNA_GUANINE", "G4_DNA_GUANOSINE", "G4_DNA_METHYLURIDINE",
    "G4_DNA_MONOPHOSPHATE", "G4_DNA_MU", "G4_DNA_THYMINE", "G4_DNA_U",
    "G4_DNA_URACIL", "G4_DNA_URIDINE",
    # E
    "G4_ETHANE", "G4_ETHYL_ALCOHOL", "G4_ETHYL_CELLULOSE", "G4_ETHYLENE",
    "G4_EYE_LENS_ICRP",
    # F
    "G4_FERRIC_OXIDE", "G4_FERROBORIDE", "G4_FERROUS_OXIDE",
    "G4_FERROUS_SULFATE", "G4_FREON-12", "G4_FREON-12B2", "G4_FREON-13",
    "G4_FREON-13B1", "G4_FREON-13I1",
    # G
    "G4_GADOLINIUM_OXYSULFIDE", "G4_Galactic", "G4_GALLIUM_ARSENIDE",
    "G4_GEL_PHOTO_EMULSION", "G4_GLASS_LEAD", "G4_GLASS_PLATE", "G4_GLUTAMINE",
    "G4_GLYCEROL", "G4_GRAPHITE", "G4_GRAPHITE_POROUS", "G4_GUANINE",
    "G4_GYPSUM",
    # K
    "G4_KAPTON", "G4_KEVLAR",
    # L (includes liquid-element forms: G4_lAr, G4_lH2, etc.)
    "G4_lAr", "G4_lBr", "G4_LANTHANUM_OXYBROMIDE", "G4_LANTHANUM_OXYSULFIDE",
    "G4_LEAD_OXIDE", "G4_lH2", "G4_LITHIUM_AMIDE", "G4_LITHIUM_CARBONATE",
    "G4_LITHIUM_FLUORIDE", "G4_LITHIUM_HYDRIDE", "G4_LITHIUM_IODIDE",
    "G4_LITHIUM_OXIDE", "G4_LITHIUM_TETRABORATE", "G4_lKr", "G4_lN2", "G4_lO2",
    "G4_lPROPANE", "G4_LUCITE", "G4_LUNG_ICRP", "G4_lXe",
    # M
    "G4_M3_WAX", "G4_MAGNESIUM_CARBONATE", "G4_MAGNESIUM_FLUORIDE",
    "G4_MAGNESIUM_OXIDE", "G4_MAGNESIUM_TETRABORATE", "G4_MERCURIC_IODIDE",
    "G4_METHANE", "G4_METHANOL", "G4_MIX_D_WAX", "G4_MS20_TISSUE",
    "G4_MUSCLE_SKELETAL_ICRP", "G4_MUSCLE_STRIATED_ICRU",
    "G4_MUSCLE_WITH_SUCROSE", "G4_MUSCLE_WITHOUT_SUCROSE", "G4_MYLAR",
    # N
    "G4_N-BUTYL_ALCOHOL", "G4_N-HEPTANE", "G4_N-HEXANE", "G4_N-PENTANE",
    "G4_N-PROPYL_ALCOHOL", "G4_N,N-DIMETHYL_FORMAMIDE", "G4_NAPHTHALENE",
    "G4_NEOPRENE", "G4_NITROBENZENE", "G4_NITROUS_OXIDE", "G4_NYLON-11_RILSAN",
    "G4_NYLON-6-10", "G4_NYLON-6-6", "G4_NYLON-8062",
    # O
    "G4_OCTADECANOL", "G4_OCTANE",
    # P
    "G4_PARAFFIN", "G4_PbWO4", "G4_PHOTO_EMULSION",
    "G4_PLASTIC_SC_VINYLTOLUENE", "G4_PLEXIGLASS", "G4_PLUTONIUM_DIOXIDE",
    "G4_POLYACRYLONITRILE", "G4_POLYCARBONATE", "G4_POLYCHLOROSTYRENE",
    "G4_POLYETHYLENE", "G4_POLYOXYMETHYLENE", "G4_POLYPROPYLENE",
    "G4_POLYSTYRENE", "G4_POLYTRIFLUOROCHLOROETHYLENE", "G4_POLYVINYL_ACETATE",
    "G4_POLYVINYL_ALCOHOL", "G4_POLYVINYL_BUTYRAL", "G4_POLYVINYL_CHLORIDE",
    "G4_POLYVINYL_PYRROLIDONE", "G4_POLYVINYLIDENE_CHLORIDE",
    "G4_POLYVINYLIDENE_FLUORIDE", "G4_POTASSIUM_IODIDE", "G4_POTASSIUM_OXIDE",
    "G4_PROPANE", "G4_Pyrex_Glass", "G4_PYRIDINE",
    # R
    "G4_RUBBER_BUTYL", "G4_RUBBER_NATURAL", "G4_RUBBER_NEOPRENE",
    # S
    "G4_SILICON_DIOXIDE", "G4_SILVER_BROMIDE", "G4_SILVER_CHLORIDE",
    "G4_SILVER_HALIDES", "G4_SILVER_IODIDE", "G4_SKIN_ICRP",
    "G4_SODIUM_CARBONATE", "G4_SODIUM_IODIDE", "G4_SODIUM_MONOXIDE",
    "G4_SODIUM_NITRATE", "G4_STAINLESS-STEEL", "G4_STILBENE", "G4_SUCROSE",
    # T
    "G4_TEFLON", "G4_TERPHENYL", "G4_TESTIS_ICRP", "G4_TETRACHLOROETHYLENE",
    "G4_THALLIUM_CHLORIDE", "G4_THYMINE", "G4_TISSUE_SOFT_ICRP",
    "G4_TISSUE_SOFT_ICRU-4", "G4_TISSUE-METHANE", "G4_TISSUE-PROPANE",
    "G4_TITANIUM_DIOXIDE", "G4_TOLUENE", "G4_TRICHLOROETHYLENE",
    "G4_TRIETHYL_PHOSPHATE", "G4_TUNGSTEN_HEXAFLUORIDE",
    # U
    "G4_URACIL", "G4_URANIUM_DICARBIDE", "G4_URANIUM_MONOCARBIDE",
    "G4_URANIUM_OXIDE", "G4_UREA",
    # V
    "G4_VALINE", "G4_VITON",
    # W
    "G4_WATER", "G4_WATER_VAPOR",
    # X
    "G4_XYLENE",
]

_G4_MATERIALS = _G4_ELEMENTS + _G4_COMPOUNDS

# Divider rows shown in the material combobox — they are not real materials and
# must be filtered out before GDML emission.  `_is_divider` is used at GDML
# generation time to guard against the user accidentally clicking one.
_DIV_ELEMENTS  = "─── G4 NIST: elements ───"
_DIV_COMPOUNDS = "─── G4 NIST: compounds ───"

def _is_divider(name: str) -> bool:
    return name.startswith("───")

_MAT_CHOICES = (
    sorted(_CUSTOM_MATERIALS.keys())
    + [_DIV_ELEMENTS]  + _G4_ELEMENTS
    + [_DIV_COMPOUNDS] + _G4_COMPOUNDS
)

_PARTICLES = {
    "Electron (e-)": 11,
    "Gamma (γ)":     22,
    "Neutron":       2112,
    "Proton":        2212,
    "Alpha":         1000020040,
}

_BRIEF_COLS = [
    "E_beam(MeV)", "E(MeV)", "EventID", "ParticleName",
    "CreatorProcessName", "Time(ns)", "detector#",
]
_FULL_COLS = [
    "E_beam(MeV)", "E_incident(MeV)", "E_deposited(MeV)",
    "x_incident(mm)", "y_incident(mm)", "z_incident(mm)",
    "theta(rad)", "Time(ns)", "EventID", "TrackID", "ParticleID",
    "ParticleName", "CreatorProcessName",
    "IsEdepositedTotalEntry", "IsSurfaceHitTrack", "detector#",
]


def _build_materials_xml(mat_names: set) -> str:
    """Return the full <materials>…</materials> XML block."""
    custom = {m for m in mat_names if m in _CUSTOM_MATERIALS}
    needed_elems: set = set()
    for mat in custom:
        for sym, _ in _CUSTOM_MATERIALS[mat][1]:
            needed_elems.add(sym)

    lines = ["  <materials>", ""]
    for sym in sorted(needed_elems):
        Z, A = _ELEMENTS[sym]
        lines.append(f'    <element Z="{Z}" name="{sym}_elem">')
        lines.append(f'      <atom unit="g/mole" value="{A}"/>')
        lines.append("    </element>")
    if needed_elems:
        lines.append("")
    for mat in sorted(custom):
        density, fracs, state = _CUSTOM_MATERIALS[mat]
        lines.append(f'    <material name="{mat}" state="{state}">')
        lines.append(f'      <D unit="g/cm3" value="{density}"/>')
        for sym, frac in fracs:
            lines.append(f'      <fraction n="{frac}" ref="{sym}_elem"/>')
        lines.append("    </material>")
    lines += ["", "  </materials>"]
    return "\n".join(lines)


# ── Volume dialog ─────────────────────────────────────────────────────────────

class VolumeDialog(tk.Toplevel):
    """Modal dialog for adding or editing a geometry volume."""

    def __init__(self, parent: tk.Misc, volume: Optional[dict] = None):
        super().__init__(parent)
        self.result: Optional[dict] = None
        self.title("Edit Volume" if volume else "Add Volume")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        self.configure(bg=_DARK["bg"])
        self._v = volume or {}
        self._shape_var = tk.StringVar(value=self._v.get("shape", "Box"))
        self._dim_vars: Dict[str, tk.StringVar] = {}
        self._dim_frame: Optional[ttk.LabelFrame] = None

        self._build_ui()
        self.wait_window()

    def _build_ui(self):
        p = dict(padx=6, pady=3)

        ttk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", **p)
        self._name_var = tk.StringVar(value=self._v.get("name", ""))
        ttk.Entry(self, textvariable=self._name_var, width=22).grid(
            row=0, column=1, columnspan=2, sticky="ew", **p)

        ttk.Label(self, text="Shape:").grid(row=1, column=0, sticky="e", **p)
        shape_cb = ttk.Combobox(
            self, textvariable=self._shape_var,
            values=["Box", "Tube", "Sphere"], width=10, state="readonly")
        shape_cb.grid(row=1, column=1, sticky="w", **p)
        shape_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_dim_frame())

        ttk.Label(self, text="Material:").grid(row=2, column=0, sticky="e", **p)
        self._mat_var = tk.StringVar(value=self._v.get("material", "G4_AIR"))
        mat_cb = ttk.Combobox(self, textvariable=self._mat_var,
                               values=_MAT_CHOICES, width=24)
        mat_cb.grid(row=2, column=1, columnspan=2, sticky="ew", **p)

        self._dim_frame = ttk.LabelFrame(self, text="Dimensions (mm)")
        self._dim_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=6, pady=4)
        self._refresh_dim_frame()

        self._build_xyz_row("Position (mm)", "pos", 4)
        self._build_xyz_row("Rotation (deg)", "rot", 5)

        self._is_det = tk.BooleanVar(value=self._v.get("is_detector", False))
        ttk.Checkbutton(
            self, text='Detector volume  (physvol name will contain "det_phys")',
            variable=self._is_det,
        ).grid(row=6, column=0, columnspan=3, sticky="w", padx=8, pady=2)

        ttk.Label(self, text="Detector index:").grid(row=7, column=0, sticky="e", **p)
        self._det_idx = tk.StringVar(value=str(self._v.get("det_idx", "0")))
        ttk.Entry(self, textvariable=self._det_idx, width=6).grid(
            row=7, column=1, sticky="w", **p)
        ttk.Label(self, text="(appended to det_phys)", foreground="gray").grid(
            row=7, column=2, sticky="w", **p)

        bf = ttk.Frame(self)
        bf.grid(row=8, column=0, columnspan=3, pady=10)
        ttk.Button(bf, text="OK",     command=self._ok).pack(side="left", padx=8)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side="left", padx=8)
        self.columnconfigure(1, weight=1)

    def _build_xyz_row(self, label: str, prefix: str, row: int):
        fr = ttk.LabelFrame(self, text=label)
        fr.grid(row=row, column=0, columnspan=3, sticky="ew", padx=6, pady=3)
        for col_idx, axis in enumerate(("x", "y", "z")):
            key = f"{prefix}_{axis}"
            ttk.Label(fr, text=f"{axis}:").grid(row=0, column=col_idx * 2, padx=4)
            var = tk.StringVar(value=str(self._v.get(key, "0")))
            self._dim_vars[key] = var
            ttk.Entry(fr, textvariable=var, width=8).grid(
                row=0, column=col_idx * 2 + 1, padx=4, pady=4)

    def _refresh_dim_frame(self):
        for w in self._dim_frame.winfo_children():
            w.destroy()
        shape = self._shape_var.get()
        if shape == "Box":
            specs = [("x", "100"), ("y", "100"), ("z", "100")]
        elif shape == "Tube":
            specs = [("rmin", "0"), ("rmax", "50"), ("z", "100")]
        else:  # Sphere
            specs = [("rmin", "0"), ("rmax", "50")]
        for col_idx, (key, default) in enumerate(specs):
            full_key = f"dim_{key}"
            ttk.Label(self._dim_frame, text=f"{key}:").grid(
                row=0, column=col_idx * 2, padx=4)
            var = tk.StringVar(value=str(self._v.get(full_key, default)))
            self._dim_vars[full_key] = var
            ttk.Entry(self._dim_frame, textvariable=var, width=8).grid(
                row=0, column=col_idx * 2 + 1, padx=4, pady=4)

    def _ok(self):
        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Please enter a volume name.", parent=self)
            return
        mat = self._mat_var.get().strip()
        if not mat or mat.startswith("─"):
            messagebox.showwarning("Invalid material", "Please select a valid material.", parent=self)
            return
        self.result = {
            "name":        name,
            "shape":       self._shape_var.get(),
            "material":    mat,
            "is_detector": self._is_det.get(),
            "det_idx":     self._det_idx.get().strip() or "0",
            **{k: v.get() for k, v in self._dim_vars.items()},
        }
        self.destroy()


# ── Main application ──────────────────────────────────────────────────────────

class GrasshopperGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Grasshopper — Geant4 Simulation Frontend")
        root.minsize(820, 580)

        self._volumes: List[dict] = []
        self._dat_data: Dict[str, list] = {}
        self._proc: Optional[subprocess.Popen] = None
        self._header_icon: Optional[tk.PhotoImage] = None

        # Load icon (figures/icon.png relative to repo root)
        icon_path = Path(__file__).parent.parent / "figures" / "icon.png"
        if icon_path.exists():
            try:
                raw = tk.PhotoImage(file=str(icon_path))
                root.iconphoto(True, raw)
                factor = max(1, raw.width() // 64)
                self._header_icon = raw.subsample(factor, factor)
            except Exception:
                pass

        self._build_ui()
        root.protocol("WM_DELETE_WINDOW", self._save_settings)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header bar ──
        hf = tk.Frame(self.root, bg=_DARK["bg2"], pady=6)
        hf.pack(fill="x")
        if self._header_icon:
            tk.Label(hf, image=self._header_icon,
                     bg=_DARK["bg2"]).pack(side="left", padx=(10, 6))
        tk.Label(hf, text="Grasshopper",
                 font=("TkDefaultFont", 15, "bold"),
                 fg=_DARK["accent"], bg=_DARK["bg2"]).pack(side="left")
        tk.Label(hf, text="  Geant4 Simulation Frontend",
                 font=("TkDefaultFont", 10),
                 fg=_DARK["fg_dim"], bg=_DARK["bg2"]).pack(side="left", pady=2)

        self._nb = ttk.Notebook(self.root)
        self._nb.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        for label, builder in [
            ("Beam & Physics", self._build_beam_tab),
            ("Output Options", self._build_output_tab),
            ("Geometry",       self._build_geometry_tab),
            ("GDML",           self._build_gdml_tab),
            ("Run",            self._build_run_tab),
            ("Visualization",  self._build_visualization_tab),
            ("Analysis",       self._build_analysis_tab),
        ]:
            frame = ttk.Frame(self._nb)
            self._nb.add(frame, text=label)
            builder(frame)
        self._load_settings()

    # ── Settings persistence ──────────────────────────────────────────────────

    def _save_settings(self):
        settings = {
            "particle":  self._particle_var.get(),
            "energy":    self._energy_var.get(),
            "events":    self._events_var.get(),
            "seed":      self._seed_var.get(),
            "bsize":     self._bsize_var.get(),
            "boffx":     self._boffx_var.get(),
            "boffy":     self._boffy_var.get(),
            "boffz":     self._boffz_var.get(),
            "ecut":      self._ecut_var.get(),
            "prodcut":   self._prodcut_var.get(),
            "lightpar":  self._lightpar_var.get(),
            "keepmain":  self._keepmain_var.get(),
            "text_out":  self._text_out_var.get(),
            "brief":     self._brief_var.get(),
            "vrml":      self._vrml_var.get(),
            "surf_hit":  self._surf_hit_var.get(),
            "track":     self._track_var.get(),
            "edep":      self._edep_var.get(),
            "vrml_acc":  self._vrml_acc_var.get(),
            "world_x":   self._world_x.get(),
            "world_y":   self._world_y.get(),
            "world_z":   self._world_z.get(),
            "world_mat": self._world_mat.get(),
            "volumes":   self._volumes,
            "wrl":        self._wrl_var.get() if hasattr(self, "_wrl_var") else "",
            "wrl_viewer": self._wrl_viewer_var.get() if hasattr(self, "_wrl_viewer_var") else "",
            "exe":       self._exe_var.get(),
            "gdml_in":   self._gdml_in_var.get(),
            "root_out":  self._root_out_var.get(),
            "run_seed":  self._run_seed_var.get(),
            "bins":       self._bins_var.get() if hasattr(self, "_bins_var") else "100",
            "logy":       self._logy_var.get() if hasattr(self, "_logy_var") else False,
            "filt1_col":  self._filt1_col_var.get() if hasattr(self, "_filt1_col_var") else "",
            "filt1_min":  self._filt1_min.get() if hasattr(self, "_filt1_min") else "",
            "filt1_max":  self._filt1_max.get() if hasattr(self, "_filt1_max") else "",
            "filt2_col":  self._filt2_col_var.get() if hasattr(self, "_filt2_col_var") else "",
            "filt2_min":  self._filt2_min.get() if hasattr(self, "_filt2_min") else "",
            "filt2_max":  self._filt2_max.get() if hasattr(self, "_filt2_max") else "",
        }
        try:
            _SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        except Exception:
            pass
        self.root.destroy()

    def _load_settings(self):
        if not _SETTINGS_PATH.exists():
            return
        try:
            s = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return

        def sv(var, key):
            if key in s:
                var.set(s[key])

        sv(self._particle_var,  "particle")
        sv(self._energy_var,    "energy")
        sv(self._events_var,    "events")
        sv(self._seed_var,      "seed")
        sv(self._bsize_var,     "bsize")
        sv(self._boffx_var,     "boffx")
        sv(self._boffy_var,     "boffy")
        sv(self._boffz_var,     "boffz")
        sv(self._ecut_var,      "ecut")
        sv(self._prodcut_var,   "prodcut")
        sv(self._lightpar_var,  "lightpar")
        sv(self._keepmain_var,  "keepmain")
        sv(self._text_out_var,  "text_out")
        sv(self._brief_var,     "brief")
        sv(self._vrml_var,      "vrml")
        sv(self._surf_hit_var,  "surf_hit")
        sv(self._track_var,     "track")
        sv(self._edep_var,      "edep")
        sv(self._vrml_acc_var,  "vrml_acc")
        sv(self._world_x,       "world_x")
        sv(self._world_y,       "world_y")
        sv(self._world_z,       "world_z")
        sv(self._world_mat,     "world_mat")
        if hasattr(self, "_wrl_var"):
            sv(self._wrl_var,        "wrl")
        if hasattr(self, "_wrl_viewer_var"):
            sv(self._wrl_viewer_var, "wrl_viewer")
        sv(self._exe_var,       "exe")
        sv(self._gdml_in_var,   "gdml_in")
        sv(self._root_out_var,  "root_out")
        sv(self._run_seed_var,  "run_seed")
        if hasattr(self, "_bins_var"):
            sv(self._bins_var,     "bins")
        if hasattr(self, "_logy_var"):
            sv(self._logy_var,     "logy")
        if hasattr(self, "_filt1_col_var"):
            sv(self._filt1_col_var, "filt1_col")
        if hasattr(self, "_filt1_min"):
            sv(self._filt1_min,    "filt1_min")
        if hasattr(self, "_filt1_max"):
            sv(self._filt1_max,    "filt1_max")
        if hasattr(self, "_filt2_col_var"):
            sv(self._filt2_col_var, "filt2_col")
        if hasattr(self, "_filt2_min"):
            sv(self._filt2_min,    "filt2_min")
        if hasattr(self, "_filt2_max"):
            sv(self._filt2_max,    "filt2_max")

        for v in s.get("volumes", []):
            self._volumes.append(v)
            self._vol_tree.insert("", "end", values=self._vol_tree_values(v))

    # ── Tab: Beam & Physics ───────────────────────────────────────────────────

    def _build_beam_tab(self, parent: ttk.Frame):
        p = dict(padx=10, pady=4)
        inner = ttk.Frame(parent)
        inner.pack(fill="both", expand=True, padx=4, pady=4)

        # Particle
        ttk.Label(inner, text="Particle:").grid(row=0, column=0, sticky="e", **p)
        self._particle_var = tk.StringVar(value="Gamma (γ)")
        ttk.Combobox(
            inner, textvariable=self._particle_var,
            values=list(_PARTICLES.keys()), state="readonly", width=20,
        ).grid(row=0, column=1, sticky="w", **p)

        # Energy
        ttk.Label(inner, text="Beam energy (MeV):").grid(row=1, column=0, sticky="e", **p)
        ef = ttk.Frame(inner)
        ef.grid(row=1, column=1, sticky="w", **p)
        self._energy_var = tk.StringVar(value="0.662")
        ttk.Entry(ef, textvariable=self._energy_var, width=12).pack(side="left")
        ttk.Label(ef, text=" negative → read input_spectrum.txt", foreground="gray").pack(
            side="left", padx=4)

        # Events
        ttk.Label(inner, text="Events to run:").grid(row=2, column=0, sticky="e", **p)
        self._events_var = tk.StringVar(value="100000")
        ttk.Entry(inner, textvariable=self._events_var, width=14).grid(
            row=2, column=1, sticky="w", **p)

        # Seed
        ttk.Label(inner, text="Random seed:").grid(row=3, column=0, sticky="e", **p)
        self._seed_var = tk.StringVar(value="1")
        ttk.Entry(inner, textvariable=self._seed_var, width=10).grid(
            row=3, column=1, sticky="w", **p)

        # Beam size
        ttk.Label(inner, text="Beam size (mm):").grid(row=4, column=0, sticky="e", **p)
        bsf = ttk.Frame(inner)
        bsf.grid(row=4, column=1, sticky="w", **p)
        self._bsize_var = tk.StringVar(value="5")
        ttk.Entry(bsf, textvariable=self._bsize_var, width=10).pack(side="left")
        ttk.Label(bsf, text=" 0=point, -1=fan, -2=isotropic", foreground="gray").pack(
            side="left", padx=4)

        # Beam offsets
        for r, (label, attr, default) in enumerate([
            ("Beam offset X (mm):", "_boffx_var", "0"),
            ("Beam offset Y (mm):", "_boffy_var", "0"),
            ("Beam offset Z (mm):", "_boffz_var", "0"),
        ], start=5):
            ttk.Label(inner, text=label).grid(row=r, column=0, sticky="e", **p)
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            ttk.Entry(inner, textvariable=var, width=10).grid(row=r, column=1, sticky="w", **p)

        ttk.Separator(inner, orient="horizontal").grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=8, padx=8)

        # Physics
        ttk.Label(inner, text="Low energy cutoff (MeV):").grid(row=9, column=0, sticky="e", **p)
        self._ecut_var = tk.StringVar(value="0")
        ttk.Entry(inner, textvariable=self._ecut_var, width=10).grid(
            row=9, column=1, sticky="w", **p)

        ttk.Label(inner, text="Production threshold (keV):").grid(
            row=10, column=0, sticky="e", **p)
        self._prodcut_var = tk.StringVar(value="100")
        pf = ttk.Frame(inner)
        pf.grid(row=10, column=1, sticky="w", **p)
        ttk.Entry(pf, textvariable=self._prodcut_var, width=10).pack(side="left")
        ttk.Label(pf, text=" use >1000 for non-neutron to optimize", foreground="gray").pack(
            side="left", padx=4)

        ttk.Label(inner, text="Light-producing particle (PDG):").grid(
            row=11, column=0, sticky="e", **p)
        lpf = ttk.Frame(inner)
        lpf.grid(row=11, column=1, sticky="w", **p)
        self._lightpar_var = tk.StringVar(value="0")
        ttk.Entry(lpf, textvariable=self._lightpar_var, width=14).pack(side="left")
        ttk.Label(lpf, text=" 0=all", foreground="gray").pack(side="left", padx=4)

        self._keepmain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            inner,
            text="Keep only main particle outside detector (kill secondaries)",
            variable=self._keepmain_var,
        ).grid(row=12, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        inner.columnconfigure(1, weight=1)

    # ── Tab: Output Options ───────────────────────────────────────────────────

    def _build_output_tab(self, parent: ttk.Frame):
        p = dict(padx=14, pady=5)
        self._text_out_var = tk.BooleanVar(value=True)
        self._brief_var    = tk.BooleanVar(value=True)
        self._vrml_var     = tk.BooleanVar(value=False)
        self._surf_hit_var = tk.BooleanVar(value=True)
        self._track_var    = tk.BooleanVar(value=False)
        self._edep_var     = tk.BooleanVar(value=False)

        for r, (text, var) in enumerate([
            ("Write ASCII text output (.dat file)",         self._text_out_var),
            ("Brief output format (fewer columns)",          self._brief_var),
            ("VRML visualization output (.wrl file)",        self._vrml_var),
            ("Save surface-hit track entries",               self._surf_hit_var),
            ("Save individual track-info entries",           self._track_var),
            ("Save total energy-deposited summary entries",  self._edep_var),
        ]):
            ttk.Checkbutton(parent, text=text, variable=var).grid(
                row=r, column=0, columnspan=2, sticky="w", **p)

        ttk.Separator(parent, orient="horizontal").grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=14, pady=6)

        ttk.Label(parent, text="Events to accumulate (VRML):").grid(
            row=7, column=0, sticky="e", **p)
        self._vrml_acc_var = tk.StringVar(value="100")
        ttk.Entry(parent, textvariable=self._vrml_acc_var, width=10).grid(
            row=7, column=1, sticky="w", **p)

    # ── Tab: Geometry ─────────────────────────────────────────────────────────

    def _build_geometry_tab(self, parent: ttk.Frame):
        wf = ttk.LabelFrame(parent, text="World volume (Box)")
        wf.pack(fill="x", padx=8, pady=6)
        p = dict(padx=6, pady=4)
        for col, (label, attr, default) in enumerate([
            ("X (mm):", "_world_x", "300"),
            ("Y (mm):", "_world_y", "300"),
            ("Z (mm):", "_world_z", "300"),
        ]):
            ttk.Label(wf, text=label).grid(row=0, column=col * 2, **p)
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            ttk.Entry(wf, textvariable=var, width=8).grid(row=0, column=col * 2 + 1, **p)
        ttk.Label(wf, text="Material:").grid(row=0, column=6, **p)
        self._world_mat = tk.StringVar(value="G4_AIR")
        ttk.Combobox(wf, textvariable=self._world_mat, values=_MAT_CHOICES,
                     width=18).grid(row=0, column=7, **p)

        # Volume list
        vf = ttk.LabelFrame(parent, text="Volumes")
        vf.pack(fill="both", expand=True, padx=8, pady=4)
        cols = ("Name", "Shape", "Material", "Position (mm)", "Detector?")
        self._vol_tree = ttk.Treeview(vf, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (120, 65, 130, 160, 75)):
            self._vol_tree.heading(c, text=c)
            self._vol_tree.column(c, width=w, anchor="w")
        vsb = ttk.Scrollbar(vf, orient="vertical", command=self._vol_tree.yview)
        self._vol_tree.configure(yscrollcommand=vsb.set)
        self._vol_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._vol_tree.bind("<Double-1>", lambda _: self._on_edit_vol())

        bf = ttk.Frame(parent)
        bf.pack(fill="x", padx=8, pady=4)
        ttk.Button(bf, text="Add volume",     command=self._on_add_vol).pack(side="left", padx=4)
        ttk.Button(bf, text="Edit selected",  command=self._on_edit_vol).pack(side="left", padx=4)
        ttk.Button(bf, text="Delete selected",command=self._on_del_vol).pack(side="left", padx=4)

    def _vol_tree_values(self, v: dict) -> tuple:
        pos = f"({v.get('pos_x','0')}, {v.get('pos_y','0')}, {v.get('pos_z','0')})"
        det = "Yes" if v.get("is_detector") else "No"
        return (v["name"], v["shape"], v["material"], pos, det)

    def _on_add_vol(self):
        dlg = VolumeDialog(self.root)
        if dlg.result:
            self._volumes.append(dlg.result)
            self._vol_tree.insert("", "end", values=self._vol_tree_values(dlg.result))

    def _on_edit_vol(self):
        sel = self._vol_tree.selection()
        if not sel:
            return
        idx = self._vol_tree.index(sel[0])
        dlg = VolumeDialog(self.root, volume=self._volumes[idx])
        if dlg.result:
            self._volumes[idx] = dlg.result
            self._vol_tree.item(sel[0], values=self._vol_tree_values(dlg.result))

    def _on_del_vol(self):
        sel = self._vol_tree.selection()
        if not sel:
            return
        idx = self._vol_tree.index(sel[0])
        self._volumes.pop(idx)
        self._vol_tree.delete(sel[0])

    # ── Tab: GDML ─────────────────────────────────────────────────────────────

    def _build_gdml_tab(self, parent: ttk.Frame):
        bf = ttk.Frame(parent)
        bf.pack(fill="x", padx=6, pady=4)
        ttk.Button(bf, text="Generate GDML", command=self._on_generate_gdml).pack(
            side="left", padx=4)
        ttk.Button(bf, text="Save as…", command=self._on_save_gdml_as).pack(
            side="left", padx=4)
        self._gdml_path_lbl = ttk.Label(bf, text="", foreground="gray")
        self._gdml_path_lbl.pack(side="left", padx=10)

        self._gdml_text = scrolledtext.ScrolledText(
            parent, wrap="none", font=("Courier New", 11),
            bg=_DARK["entry"], fg=_DARK["fg"],
            insertbackground=_DARK["fg"],
            selectbackground=_DARK["sel"], selectforeground=_DARK["fg"])
        self._gdml_text.pack(fill="both", expand=True, padx=6, pady=4)

    # ── Tab: Run ──────────────────────────────────────────────────────────────

    def _build_run_tab(self, parent: ttk.Frame):
        p = dict(padx=8, pady=4)

        def path_row(row: int, label: str, var_attr: str, default: str, browse_cmd):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", **p)
            var = tk.StringVar(value=default)
            setattr(self, var_attr, var)
            ttk.Entry(parent, textvariable=var, width=44).grid(
                row=row, column=1, sticky="ew", **p)
            ttk.Button(parent, text="Browse…", command=browse_cmd).grid(
                row=row, column=2, sticky="w", padx=4)

        path_row(0, "Grasshopper executable:", "_exe_var",      "grasshopper",  self._on_browse_exe)
        path_row(1, "GDML input file:",        "_gdml_in_var",  "default.gdml", self._on_browse_gdml_in)
        path_row(2, "ROOT output file:",       "_root_out_var", "output.root",     self._on_browse_root_out)

        ttk.Label(parent, text="Seed override:").grid(row=3, column=0, sticky="e", **p)
        sf = ttk.Frame(parent)
        sf.grid(row=3, column=1, sticky="w", **p)
        self._run_seed_var = tk.StringVar(value="")
        ttk.Entry(sf, textvariable=self._run_seed_var, width=10).pack(side="left")
        ttk.Label(sf, text=" leave blank to use seed from GDML", foreground="gray").pack(
            side="left", padx=4)

        bbf = ttk.Frame(parent)
        bbf.grid(row=4, column=0, columnspan=3, sticky="w", **p)
        self._run_btn = ttk.Button(bbf, text="▶  Run simulation", command=self._on_run)
        self._run_btn.pack(side="left", padx=4)
        self._stop_btn = ttk.Button(bbf, text="■  Stop", command=self._on_stop,
                                    state="disabled")
        self._stop_btn.pack(side="left", padx=4)
        self._status_lbl = ttk.Label(bbf, text="")
        self._status_lbl.pack(side="left", padx=14)

        ttk.Label(parent, text="Output log:").grid(
            row=5, column=0, columnspan=3, sticky="w", padx=8)
        self._log = scrolledtext.ScrolledText(
            parent, wrap="word", font=("Courier New", 10), height=14,
            bg=_DARK["entry"], fg=_DARK["fg"],
            insertbackground=_DARK["fg"],
            selectbackground=_DARK["sel"], selectforeground=_DARK["fg"])
        self._log.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=8, pady=4)

        parent.rowconfigure(6, weight=1)
        parent.columnconfigure(1, weight=1)

    # ── Tab: Visualization ────────────────────────────────────────────────────

    def _build_visualization_tab(self, parent: ttk.Frame):
        import sys

        # ── File selector row ──
        ff = ttk.Frame(parent)
        ff.pack(fill="x", padx=8, pady=6)
        ttk.Label(ff, text="WRL file:").pack(side="left")
        self._wrl_var = tk.StringVar()
        ttk.Entry(ff, textvariable=self._wrl_var, width=44).pack(side="left", padx=4)
        ttk.Button(ff, text="Browse…",      command=self._on_browse_wrl).pack(side="left")
        ttk.Button(ff, text="Find latest",  command=self._on_find_latest_wrl).pack(
            side="left", padx=(6, 0))

        # ── External viewer row ──
        ef = ttk.Frame(parent)
        ef.pack(fill="x", padx=8, pady=2)
        _defaults = {"darwin": "open", "win32": "start", "linux": "xdg-open"}
        default_viewer = _defaults.get(sys.platform, "open")
        ttk.Label(ef, text="External viewer:").pack(side="left")
        self._wrl_viewer_var = tk.StringVar(value=default_viewer)
        ttk.Entry(ef, textvariable=self._wrl_viewer_var, width=28).pack(side="left", padx=4)
        ttk.Button(ef, text="Open in viewer", command=self._on_open_wrl_external).pack(
            side="left", padx=4)
        ttk.Label(ef, text="(e.g. open, paraview, meshlab)", foreground="gray").pack(
            side="left", padx=4)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=8, pady=4)

        if HAS_VTK:
            try:
                self._build_vtk_viewport(parent)
                self._vtk_embedded = True
            except Exception:
                self._vtk_embedded = False
                self._build_vtk_standalone_btn(parent)
        else:
            self._vtk_embedded = False
            msg = (
                "3D preview requires the vtk package.\n\n"
                "Install with:  pip install vtk\n\n"
                "After installing, restart the GUI.\n\n"
                "In the meantime, use 'Open in viewer' above to view the WRL file\n"
                "in an external application such as ParaView."
            )
            ttk.Label(parent, text=msg, justify="center",
                      font=("TkDefaultFont", 11), foreground="gray").pack(expand=True)

    def _build_vtk_viewport(self, parent: ttk.Frame):
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill="x", padx=8, pady=2)
        ttk.Button(tb, text="Load / Reload", command=self._on_load_wrl).pack(side="left", padx=4)
        ttk.Button(tb, text="Reset camera",  command=self._on_vtk_reset_camera).pack(
            side="left", padx=4)
        self._wrl_status = ttk.Label(tb, text="No file loaded", foreground="gray")
        self._wrl_status.pack(side="left", padx=10)

        # VTK renderer + embedded widget
        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_renderer.SetBackground(0.15, 0.15, 0.15)

        vtk_frame = ttk.Frame(parent)
        vtk_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self._vtk_widget = vtkTkRenderWindowInteractor(vtk_frame, width=600, height=400)
        self._vtk_widget.pack(fill="both", expand=True)

        self._vtk_win = self._vtk_widget.GetRenderWindow()
        self._vtk_win.AddRenderer(self._vtk_renderer)

        style = vtk.vtkInteractorStyleTrackballCamera()
        self._vtk_widget.GetRenderWindowInteractor().SetInteractorStyle(style)
        self._vtk_widget.Initialize()

    def _build_vtk_standalone_btn(self, parent: ttk.Frame):
        """Shown when VTK is installed but libvtkRenderingTk is unavailable."""
        cf = ttk.Frame(parent)
        cf.pack(expand=True)
        ttk.Button(cf, text="Open 3D view (VTK window)",
                   command=self._on_open_vtk_standalone).pack(pady=8)
        self._wrl_status = ttk.Label(cf, text="", foreground="gray")
        self._wrl_status.pack()
        ttk.Label(
            cf,
            text=(
                "vtk is installed but was built without Tk rendering support\n"
                "(libvtkRenderingTk not found).\n\n"
                "Clicking the button above opens a standalone VTK window instead."
            ),
            justify="center", foreground="gray",
        ).pack(pady=6)

    # ── Visualization actions ─────────────────────────────────────────────────

    def _on_browse_wrl(self):
        path = filedialog.askopenfilename(
            title="Select WRL file",
            filetypes=[("VRML files", "*.wrl"), ("All files", "*.*")])
        if path:
            self._wrl_var.set(path)

    def _on_find_latest_wrl(self):
        latest = self._find_latest_wrl()
        if latest:
            self._wrl_var.set(str(latest))
        else:
            messagebox.showinfo("Not found", "No g4_*.wrl files found in the current directory.")

    def _find_latest_wrl(self) -> Optional[Path]:
        candidates = sorted(Path(".").glob("g4_*.wrl"),
                             key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0] if candidates else None

    def _on_open_vtk_standalone(self):
        import sys as _sys
        path = self._wrl_var.get().strip()
        if not path or not Path(path).exists():
            messagebox.showwarning("File not found",
                                   "Please select or find a WRL file first.")
            return
        viewer_script = Path(__file__).parent / "grasshopper_vtk_viewer.py"
        subprocess.Popen([_sys.executable, str(viewer_script), path])
        if hasattr(self, "_wrl_status"):
            self._wrl_status.configure(
                text=f"Opened {Path(path).name} in VTK window", foreground="black")

    def _auto_load_wrl(self):
        latest = self._find_latest_wrl()
        if latest:
            self._wrl_var.set(str(latest))
            if HAS_VTK and getattr(self, "_vtk_embedded", False):
                self._on_load_wrl()

    def _on_open_wrl_external(self):
        import sys
        path = self._wrl_var.get().strip()
        if not path:
            messagebox.showwarning("No file", "Please select or find a WRL file first.")
            return
        viewer = self._wrl_viewer_var.get().strip()
        try:
            if sys.platform == "win32" and viewer == "start":
                subprocess.Popen(["cmd", "/c", "start", "", path], shell=False)
            else:
                subprocess.Popen([viewer, path])
        except FileNotFoundError:
            messagebox.showerror("Viewer not found",
                                 f"Could not launch '{viewer}'.\n"
                                 "Edit the viewer field to point to a valid executable.")

    def _on_load_wrl(self):
        if not HAS_VTK or not getattr(self, "_vtk_embedded", False):
            return
        path = self._wrl_var.get().strip()
        if not path or not Path(path).exists():
            messagebox.showwarning("File not found", f"WRL file not found:\n{path}")
            return
        self._vtk_renderer.RemoveAllViewProps()
        importer = vtk.vtkVRMLImporter()
        importer.SetFileName(path)
        importer.SetRenderWindow(self._vtk_win)
        importer.Update()
        self._vtk_renderer.ResetCamera()
        self._vtk_win.Render()
        self._wrl_status.configure(text=Path(path).name, foreground="black")

    def _on_vtk_reset_camera(self):
        if getattr(self, "_vtk_embedded", False) and hasattr(self, "_vtk_renderer"):
            self._vtk_renderer.ResetCamera()
            self._vtk_win.Render()

    # ── Tab: Analysis ─────────────────────────────────────────────────────────

    def _build_analysis_tab(self, parent: ttk.Frame):
        if not HAS_MPL:
            ttk.Label(
                parent,
                text="matplotlib and numpy are required for the Analysis tab.\n\n"
                     "Install with:  pip install matplotlib numpy\n\nThen restart.",
                font=("TkDefaultFont", 12),
                justify="center",
            ).pack(expand=True)
            return

        # Controls row
        cf = ttk.Frame(parent)
        cf.pack(fill="x", padx=8, pady=6)
        ttk.Button(cf, text="Load .dat file…", command=self._on_load_dat).pack(
            side="left", padx=4)
        self._dat_label = ttk.Label(cf, text="No file loaded", foreground="gray")
        self._dat_label.pack(side="left", padx=8)
        ttk.Label(cf, text="Column:").pack(side="left", padx=(16, 4))
        self._col_var = tk.StringVar()
        self._col_cb  = ttk.Combobox(cf, textvariable=self._col_var,
                                      state="disabled", width=26)
        self._col_cb.pack(side="left")
        ttk.Label(cf, text="Bins:").pack(side="left", padx=(10, 4))
        self._bins_var = tk.StringVar(value="100")
        ttk.Entry(cf, textvariable=self._bins_var, width=6).pack(side="left")
        self._logy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cf, text="Log Y", variable=self._logy_var).pack(side="left", padx=(8, 0))
        ttk.Button(cf, text="Plot", command=self._on_plot).pack(side="left", padx=8)

        # Two-column row filters
        ff = ttk.LabelFrame(parent, text="Row filters — select up to 2 columns to cut on (leave blank to skip)")
        ff.pack(fill="x", padx=8, pady=2)
        self._filt_col_cbs: List[ttk.Combobox] = []
        for i in range(2):
            ttk.Label(ff, text=f"Filter {i+1}:").grid(row=i, column=0, padx=6, pady=3, sticky="e")
            col_var = tk.StringVar()
            setattr(self, f"_filt{i+1}_col_var", col_var)
            col_cb = ttk.Combobox(ff, textvariable=col_var, state="disabled", width=22)
            setattr(self, f"_filt{i+1}_col_cb", col_cb)
            col_cb.grid(row=i, column=1, padx=4, pady=3)
            self._filt_col_cbs.append(col_cb)
            for j, (lbl, attr) in enumerate([("Min:", f"_filt{i+1}_min"), ("Max:", f"_filt{i+1}_max")]):
                ttk.Label(ff, text=lbl).grid(row=i, column=2 + j*2, padx=(8, 2), pady=3)
                var = tk.StringVar()
                setattr(self, attr, var)
                ttk.Entry(ff, textvariable=var, width=10).grid(row=i, column=3 + j*2, padx=2)
        ttk.Label(ff,
                  text="numeric: blank = no limit\n"
                       "string: put match value(s) in Min and/or Max\n"
                       "          (comma-separated = any-of)",
                  foreground="gray", justify="left").grid(
            row=0, column=6, rowspan=2, padx=10, sticky="w")

        # Matplotlib canvas — dark theme
        self._fig = Figure(figsize=(6, 4), dpi=100, facecolor=_DARK["bg"])
        self._ax  = self._fig.add_subplot(111)
        self._style_ax()
        self._canvas = FigureCanvasTkAgg(self._fig, parent)
        toolbar = NavigationToolbar2Tk(self._canvas, parent)
        toolbar.config(background=_DARK["bg2"])
        for w in toolbar.winfo_children():
            try:
                w.config(background=_DARK["bg2"])
            except Exception:
                pass
        self._canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=4)

    def _style_ax(self) -> None:
        """Apply dark-mode colours to the matplotlib axes."""
        D = _DARK
        self._ax.set_facecolor(D["entry"])
        self._ax.tick_params(colors=D["fg"])
        self._ax.xaxis.label.set_color(D["fg"])
        self._ax.yaxis.label.set_color(D["fg"])
        self._ax.title.set_color(D["fg"])
        for spine in self._ax.spines.values():
            spine.set_edgecolor(D["border"])

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_generate_gdml(self):
        try:
            gdml = self._make_gdml()
        except Exception as exc:
            messagebox.showerror("GDML generation error", str(exc))
            return
        self._gdml_text.delete("1.0", "end")
        self._gdml_text.insert("1.0", gdml)
        # Auto-save to default.gdml
        default_path = Path("default.gdml")
        default_path.write_text(gdml, encoding="utf-8")
        self._gdml_in_var.set(str(default_path))
        self._gdml_path_lbl.configure(text=f"Saved to {default_path}")

    def _on_save_gdml_as(self):
        self._on_generate_gdml()
        path = filedialog.asksaveasfilename(
            defaultextension=".gdml",
            filetypes=[("GDML files", "*.gdml"), ("All files", "*.*")],
        )
        if path:
            Path(path).write_text(self._gdml_text.get("1.0", "end"), encoding="utf-8")
            self._gdml_in_var.set(path)
            self._gdml_path_lbl.configure(text=f"Saved to {Path(path).name}")

    def _on_browse_exe(self):
        path = filedialog.askopenfilename(title="Select grasshopper executable")
        if path:
            self._exe_var.set(path)

    def _on_browse_gdml_in(self):
        path = filedialog.askopenfilename(
            title="Select GDML input file",
            filetypes=[("GDML files", "*.gdml"), ("All files", "*.*")])
        if path:
            self._gdml_in_var.set(path)

    def _on_browse_root_out(self):
        path = filedialog.asksaveasfilename(
            title="ROOT output file",
            defaultextension=".root",
            filetypes=[("ROOT files", "*.root"), ("All files", "*.*")])
        if path:
            self._root_out_var.set(path)

    def _on_run(self):
        exe  = self._exe_var.get().strip()
        gdml = self._gdml_in_var.get().strip()
        out  = self._root_out_var.get().strip()
        seed = self._run_seed_var.get().strip()
        if not exe or not gdml or not out:
            messagebox.showwarning("Missing fields",
                                   "Please fill in the executable, GDML, and output fields.")
            return
        cmd = [exe, gdml, out] + ([seed] if seed else [])
        self._log.delete("1.0", "end")
        self._append_log(f"$ {' '.join(cmd)}\n\n")
        self._run_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._status_lbl.configure(text="Running…")
        threading.Thread(target=self._run_thread, args=(cmd,), daemon=True).start()

    def _run_thread(self, cmd: list):
        rc = -1
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in self._proc.stdout:
                self.root.after(0, self._append_log, line)
            self._proc.wait()
            rc = self._proc.returncode
        except FileNotFoundError:
            self.root.after(0, self._append_log,
                            f"\nERROR: executable not found: {cmd[0]}\n")
        except Exception as exc:
            self.root.after(0, self._append_log, f"\nERROR: {exc}\n")
        finally:
            self._proc = None
        self.root.after(0, self._run_done, rc)

    def _append_log(self, text: str):
        self._log.insert("end", text)
        self._log.see("end")

    def _run_done(self, rc: int):
        self._run_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        status = "Finished (exit 0)" if rc == 0 else f"Exited with code {rc}"
        self._status_lbl.configure(text=status)
        self._append_log(f"\n[{status}]\n")
        if rc == 0:
            self._auto_load_wrl()
            if HAS_MPL:
                self._auto_load_dat()

    def _auto_load_dat(self):
        root_path = self._root_out_var.get().strip()
        dat_path = Path(root_path).with_suffix(".dat") if root_path else Path("output.dat")
        if dat_path.exists():
            data = self._parse_dat(str(dat_path))
            if data:
                self._dat_data = data
                cols = list(data.keys())
                self._update_analysis_cols(cols)
                if cols:
                    self._col_var.set(cols[0])
                nrows = len(next(iter(data.values()), []))
                self._dat_label.configure(
                    text=f"{dat_path.name}  ({nrows:,} rows, {len(cols)} cols)",
                    foreground="black")
                self._nb.select(6)  # switch to Analysis tab

    def _on_stop(self):
        if self._proc:
            self._proc.terminate()

    def _on_load_dat(self):
        path = filedialog.askopenfilename(
            title="Open .dat output file",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")])
        if not path:
            return
        data = self._parse_dat(path)
        if data is None:
            return
        self._dat_data = data
        cols = list(data.keys())
        self._update_analysis_cols(cols)
        if cols:
            self._col_var.set(cols[0])
        nrows = len(next(iter(data.values()), []))
        self._dat_label.configure(
            text=f"{Path(path).name}  ({nrows:,} rows, {len(cols)} cols)",
            foreground="black")

    def _parse_dat(self, path: str) -> Optional[Dict[str, list]]:
        rows = []
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(line.split())
        if not rows:
            messagebox.showwarning("Empty file", "The file contains no data.")
            return None
        # Skip header line: first token of a data row is always a float (E_beam)
        try:
            float(rows[0][0])
        except ValueError:
            rows = rows[1:]
        if not rows:
            messagebox.showwarning("Empty file", "The file contains no data rows.")
            return None
        ncols = len(rows[0])
        if ncols <= len(_BRIEF_COLS):
            names = _BRIEF_COLS[:ncols]
        elif ncols <= len(_FULL_COLS):
            names = _FULL_COLS[:ncols]
        else:
            names = _FULL_COLS + [f"col{i}" for i in range(len(_FULL_COLS), ncols)]
        data: Dict[str, list] = {n: [] for n in names}
        for row in rows:
            for i, name in enumerate(names):
                data[name].append(row[i] if i < len(row) else "")
        return data

    def _update_analysis_cols(self, cols: List[str]):
        """Refresh all column selectors in the Analysis tab after loading data."""
        self._col_cb.configure(values=cols, state="readonly")
        for cb in self._filt_col_cbs:
            cb.configure(values=[""] + cols, state="readonly")

    def _on_plot(self):
        if not HAS_MPL:
            return
        col = self._col_var.get()
        if not col or col not in self._dat_data:
            messagebox.showwarning("No data", "Load a .dat file and select a column.")
            return

        # Build row mask from the two column filters
        n = len(next(iter(self._dat_data.values())))
        mask = np.ones(n, dtype=bool)
        for i in (1, 2):
            fcol = getattr(self, f"_filt{i}_col_var").get().strip()
            fmin_s = getattr(self, f"_filt{i}_min").get().strip()
            fmax_s = getattr(self, f"_filt{i}_max").get().strip()
            if not fcol or fcol not in self._dat_data or (not fmin_s and not fmax_s):
                continue

            def _as_float(s):
                try:
                    return float(s)
                except ValueError:
                    return None

            fmin_n = _as_float(fmin_s) if fmin_s else None
            fmax_n = _as_float(fmax_s) if fmax_s else None
            # If either entered value isn't a number, treat as string match:
            # row passes if column value equals any comma-separated token.
            string_mode = (fmin_s and fmin_n is None) or (fmax_s and fmax_n is None)

            if string_mode:
                allowed = set()
                for s in (fmin_s, fmax_s):
                    if s:
                        allowed.update(t.strip() for t in s.split(",") if t.strip())
                mask &= np.array([str(v) in allowed for v in self._dat_data[fcol]])
            else:
                fcol_nums = []
                for v in self._dat_data[fcol]:
                    try:
                        fcol_nums.append(float(v))
                    except ValueError:
                        fcol_nums.append(float("nan"))
                farr = np.array(fcol_nums)
                if fmin_n is not None:
                    mask &= farr >= fmin_n
                if fmax_n is not None:
                    mask &= farr <= fmax_n

        raw = [v for v, keep in zip(self._dat_data[col], mask) if keep]
        nums = []
        for v in raw:
            try:
                nums.append(float(v))
            except ValueError:
                pass

        self._ax.clear()
        self._style_ax()
        if len(nums) >= len(raw) * 0.5:
            arr = np.array(nums)
            try:
                bins = max(1, int(self._bins_var.get()))
            except ValueError:
                bins = 100
            self._ax.hist(arr, bins=bins, facecolor="white",
                          edgecolor="white", histtype="stepfilled", linewidth=.1)
            self._ax.set_xlabel(col)
            self._ax.set_ylabel("Counts")
        else:
            from collections import Counter
            counts = Counter(raw)
            labels, values = zip(*sorted(counts.items(), key=lambda x: -x[1]))
            x = range(len(labels))
            self._ax.bar(x, values, color="steelblue")
            self._ax.set_xticks(list(x))
            self._ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9)
            self._ax.set_ylabel("Counts")
            self._ax.set_xlabel(col)

        self._ax.set_title(col)
        self._ax.set_yscale("log" if self._logy_var.get() else "linear")
        self._fig.tight_layout()
        self._canvas.draw()

    # ── GDML generation ───────────────────────────────────────────────────────

    def _make_gdml(self) -> str:
        pdg = _PARTICLES.get(self._particle_var.get(), 22)

        # Reject divider rows from the material combobox before they make it
        # into the GDML — Geant4 will not load a materialref to "─── … ───".
        world_mat = self._world_mat.get()
        if _is_divider(world_mat):
            raise ValueError("World material is not selected — pick a real material.")
        for v in self._volumes:
            if _is_divider(v["material"]):
                raise ValueError(
                    f"Volume {v['name']!r} has no material selected — pick a real material.")

        # Collect materials used
        mats_used = {world_mat}
        for v in self._volumes:
            mats_used.add(v["material"])

        lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>',
            "",
            '<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '      xsi:noNamespaceSchemaLocation='
            '"../schema/gdml.xsd">',
            "",
        ]

        # Materials
        lines.append(_build_materials_xml(mats_used))
        lines.append("")

        # Define — output
        lines += [
            "  <!-- output settings -->",
            "  <define>",
            f'    <constant name="TextOutputOn"        value="{1 if self._text_out_var.get() else 0}"/>',
            f'    <constant name="BriefOutputOn"       value="{1 if self._brief_var.get() else 0}"/>',
            f'    <constant name="VRMLvisualizationOn" value="{1 if self._vrml_var.get() else 0}"/>',
            f'    <constant name="EventsToAccumulate"  value="{self._vrml_acc_var.get()}"/>',
            "  </define>",
            "",
        ]

        # Define — physics cuts
        lines += [
            "  <!-- physics cuts -->",
            "  <define>",
            f'    <constant name="LightProducingParticle" value="{self._lightpar_var.get()}"/>',
            f'    <constant name="LowEnergyCutoff"        value="{self._ecut_var.get()}"/>',
            f'    <constant name="KeepOnlyMainParticle"   value="{1 if self._keepmain_var.get() else 0}"/>',
            f'    <quantity name="ProductionLowLimit" type="threshold"'
            f' value="{self._prodcut_var.get()}" unit="keV"/>',
            "  </define>",
            "",
        ]

        # Define — output filters
        lines += [
            "  <!-- output filters -->",
            "  <define>",
            f'    <constant name="SaveSurfaceHitTrack"      value="{1 if self._surf_hit_var.get() else 0}"/>',
            f'    <constant name="SaveTrackInfo"            value="{1 if self._track_var.get() else 0}"/>',
            f'    <constant name="SaveEdepositedTotalEntry" value="{1 if self._edep_var.get() else 0}"/>',
            "  </define>",
            "",
        ]

        # Define — beam
        lines += [
            "  <!-- beam definition -->",
            "  <define>",
            f'    <constant name="RandomGenSeed"  value="{self._seed_var.get()}"/>',
            f'    <quantity name="BeamOffsetX" type="coordinate" value="{self._boffx_var.get()}" unit="mm"/>',
            f'    <quantity name="BeamOffsetY" type="coordinate" value="{self._boffy_var.get()}" unit="mm"/>',
            f'    <quantity name="BeamOffsetZ" type="coordinate" value="{self._boffz_var.get()}" unit="mm"/>',
            f'    <quantity name="BeamSize"    type="coordinate" value="{self._bsize_var.get()}" unit="mm"/>',
            f'    <quantity name="BeamEnergy"  type="energy"     value="{self._energy_var.get()}" unit="MeV"/>',
            f'    <constant name="EventsToRun"    value="{self._events_var.get()}"/>',
            f'    <constant name="ParticleNumber" value="{pdg}"/>',
            "    <!-- e- is 11, gamma is 22, neutron is 2112, proton is 2212, alpha is 1000020040 -->",
            "  </define>",
            "",
        ]

        # Solids
        lines.append("  <solids>")
        lines.append(
            f'    <box lunit="mm" name="world_solid"'
            f' x="{self._world_x.get()}" y="{self._world_y.get()}" z="{self._world_z.get()}"/>'
        )
        for v in self._volumes:
            sn = f'{v["name"]}_solid'
            shape = v["shape"]
            if shape == "Box":
                lines.append(
                    f'    <box lunit="mm" name="{sn}"'
                    f' x="{v.get("dim_x","100")}"'
                    f' y="{v.get("dim_y","100")}"'
                    f' z="{v.get("dim_z","100")}"/>'
                )
            elif shape == "Tube":
                lines.append(
                    f'    <tube lunit="mm" name="{sn}"'
                    f' rmin="{v.get("dim_rmin","0")}"'
                    f' rmax="{v.get("dim_rmax","50")}"'
                    f' z="{v.get("dim_z","100")}"'
                    f' startphi="0" deltaphi="360" aunit="deg"/>'
                )
            else:  # Sphere
                lines.append(
                    f'    <sphere lunit="mm" name="{sn}"'
                    f' rmin="{v.get("dim_rmin","0")}"'
                    f' rmax="{v.get("dim_rmax","50")}"'
                    f' startphi="0" deltaphi="360"'
                    f' starttheta="0" deltatheta="180" aunit="deg"/>'
                )
        lines += ["  </solids>", ""]

        # Structure — individual logical volumes
        lines.append("  <structure>")
        for v in self._volumes:
            lines += [
                f'    <volume name="{v["name"]}_log">',
                f'      <materialref ref="{v["material"]}"/>',
                f'      <solidref ref="{v["name"]}_solid"/>',
                "    </volume>",
            ]

        # World logical with physvols
        lines += [
            '    <volume name="world_log">',
            f'      <materialref ref="{self._world_mat.get()}"/>',
            '      <solidref ref="world_solid"/>',
        ]
        for v in self._volumes:
            phys_name = (f'det_phys{v.get("det_idx","0")}'
                         if v.get("is_detector") else f'{v["name"]}_phys')
            lines.append(f'      <physvol name="{phys_name}">')
            lines.append(f'        <volumeref ref="{v["name"]}_log"/>')
            lines.append(
                f'        <position name="{v["name"]}_pos" unit="mm"'
                f' x="{v.get("pos_x","0")}"'
                f' y="{v.get("pos_y","0")}"'
                f' z="{v.get("pos_z","0")}"/>'
            )
            try:
                rx, ry, rz = v.get("rot_x","0"), v.get("rot_y","0"), v.get("rot_z","0")
                if any(float(r) != 0.0 for r in (rx, ry, rz)):
                    lines.append(
                        f'        <rotation name="{v["name"]}_rot" unit="deg"'
                        f' x="{rx}" y="{ry}" z="{rz}"/>'
                    )
            except ValueError:
                pass
            lines.append("      </physvol>")
        lines += [
            "    </volume>",
            "  </structure>",
            "",
            '  <setup name="Default" version="1.0">',
            '    <world ref="world_log"/>',
            "  </setup>",
            "",
            "</gdml>",
        ]
        return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass
    _apply_dark_theme(root)
    GrasshopperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
