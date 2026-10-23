# Conda-forge packaging

Plan and current state of publishing grasshopper as a conda-forge package.
Status is as of **2026-10-23**, branch `conda-forge-packaging` (uncommitted, nothing pushed yet).

**Contents**

- [Why conda-forge (and not Homebrew/apt)](#why-conda-forge-and-not-homebrewapt)
- [What users will do](#what-users-will-do)
- [Versioning policy](#versioning-policy)
- [Status](#status)
- [Phase A: upstream changes](#phase-a-upstream-changes)
- [Phase B: the recipe](#phase-b-the-recipe)
- [Phase C: submission and maintenance](#phase-c-submission-and-maintenance)
- [Verification](#verification)
- [Risks and open questions](#risks-and-open-questions)
- [Links](#links)

---

## Why conda-forge (and not Homebrew/apt)

The original goal was "install grasshopper with a package manager instead of building Geant4 and grasshopper by hand", with Homebrew and apt as the obvious candidates. Both are blocked on **Geant4 itself**, not on grasshopper:

| Channel | State of Geant4 | Consequence for grasshopper |
|---|---|---|
| Homebrew | `geant4` was dropped from homebrew-core years ago over the Geant4 Software License. The Geant4 project says an official tap is "coming"; none exists. Only personal taps (e.g. cxwx/cxbrew) carry it. | We would have to maintain our own Geant4 formula and bottles. |
| Debian / Ubuntu | Open ITP, [Debian bug #965964](https://bugs.debian.org/965964) (filed 2020), stalled on a DFSG dispute (patent clause), a 1.5 GB source and the datasets. Ubuntu has no archive package, only a personal PPA. | We would have to maintain our own Geant4 `.deb`s. |
| conda-forge | `geant4` **11.4.3** is already published by the [geant4-feedstock](https://github.com/conda-forge/geant4-feedstock) (maintainers chrisburr, tkittel): built with `GEANT4_USE_GDML=ON` (xerces-c), multithreaded, shared libraries, datasets pulled in via `geant4-data-*` run dependencies, for `linux-64`, `linux-aarch64`, `osx-64`, `osx-arm64`. Its `run_exports` pin dependents to the **exact patch version**. ROOT is also on conda-forge if ever wanted. | Only grasshopper itself needs a recipe. |

See also the package-manager section of the [Geant4 installation guide](https://geant4.web.cern.ch/documentation/dev/ig_html/InstallationGuide/index.html).

**Decisions**

- conda-forge is the only distribution channel. The README states that Homebrew and apt packages are not offered until Geant4 is available there.
- One recipe produces two packages: `grasshopper` (binary + GDML schema + examples) and `grasshopper-gui` (noarch Python).
- Version numbers track Geant4 (see [Versioning policy](#versioning-policy)).
- No ROOT in the package (`-DWITH_ROOT=OFF`); output is ASCII `.dat` only. Users who need `.root` output build from source.

Verified non-issues before starting: `include/Analysis.hh` only forced `G4ANALYSIS_USE_ROOT` when Geant4 was built with a ROOT UI session (never on conda-forge; the block has since been deleted), and `G4VRML2File.hh` still exists in Geant4 11, so VRML `.wrl` output works with core Geant4 libraries only, no X11/Qt.

---

## What users will do

Once the feedstock exists:

```bash
conda create -n grasshopper -c conda-forge grasshopper grasshopper-gui
conda activate grasshopper
grasshopper --help
```

- `grasshopper-gui` is optional. Add `vtk` to the install line for the 3D `.wrl` viewer (`grasshopper-vtk-viewer`). `micromamba`/`mamba` work the same way.
- Geant4 and all its datasets are installed as dependencies; the `G4*DATA` environment variables are set by the `geant4-data-*` activation scripts.
- Example inputs are installed under `$CONDA_PREFIX/share/grasshopper/examples/` (same files as [examples/ on GitHub](https://github.com/ustajan/grasshopper/tree/master/examples)); the schema is at `$CONDA_PREFIX/share/grasshopper/schema/gdml.xsd`. Run an example in place or copy the directory:

  ```bash
  cp -r $CONDA_PREFIX/share/grasshopper/examples/beta . && cd beta
  grasshopper beta_lite.gdml test        # writes test.dat (and g4_NN.wrl if VRMLvisualizationOn=1)
  ```

- `input_spectrum.txt` (when `BeamEnergy < 0`), `beam_width.txt` and `vis.mac` are read from the current directory.
- **ROOT output is not included.** The conda build uses `-DWITH_ROOT=OFF`; `<output>.root` is only produced by a from-source build with `-DWITH_ROOT=ON`.
- Console scripts shipped by `grasshopper-gui`: `grasshopper-gui`, `grasshopper-gui-novis`, `grasshopper-vtk-viewer` (each supports `--version`). GUI settings are stored per user in `~/Library/Application Support/grasshopper/gui_settings.json` (macOS) or `$XDG_CONFIG_HOME/grasshopper/` (Linux, default `~/.config/grasshopper/`).

---

## Versioning policy

| Form | Meaning | Example |
|---|---|---|
| `X.Y.Z` | The Geant4 release grasshopper was validated against. Each new Geant4 patch on conda-forge requires a new grasshopper release because the `geant4` run_export pins the exact patch. | `11.4.3` |
| `X.Y.Z.N` | A grasshopper-only fix on top of the same Geant4 release. | `11.4.3.1` |
| conda `build_number` | Recipe-only changes (no new tarball). | `build: number: 1` |

- The single source of truth is the top-level `VERSION` file, read by `CMakeLists.txt` (`project(... VERSION ...)`) and by `pyproject.toml` (`dynamic = ["version"]`).
- Git tag = `v` + `VERSION` (e.g. `v11.4.3`). The recipe's `source.url` points at the tag tarball.
- `grasshopper --version` prints both numbers, e.g. `grasshopper 11.4.3 ($Name: geant4-11-03-patch-02 [MT]$)` on the dev machine (Geant4 11.3.2); against the conda package it must show `geant4-11-04-patch-03`.
- Previous tags on the repo (`v1.0`, `v2.0`, `v2.9`, `v11.2.2`) predate this policy.

---

## Status

As of 2026-10-23. Everything in the "Done" rows lives uncommitted in the working tree of branch `conda-forge-packaging`; nothing has been pushed, tagged or released.

| # | Item | State |
|---|---|---|
| A1 | `VERSION` file (`11.4.3`), `exec/Examples` moved to `examples/`, schema paths rewritten, junk untracked, `.gitignore` extended, `GNUmakefile` marked legacy | Done |
| A2 | `CMakeLists.txt` rewritten (version from file, GNUInstallDirs, Geant4 11.0 minimum, core-only build option, install rules, ctest smoke test, compile definitions) | Done |
| A2' | Installed binary RPATH (`CMAKE_INSTALL_RPATH_USE_LINK_PATH`) so the installed executable finds `libG4*.dylib` / `.so` | Done (verified: installed binary runs from an unrelated directory, both with the local Geant4 11.3.2 and with the conda-forge 11.4.3 package) |
| A3 | `grasshopper --version` / `--help`, usage on wrong arguments (exit 2), dead `G4UI_USE_ROOT` block removed | Done |
| A4 | GUI as an installable Python package (`gui/grasshopper_gui/`, root `pyproject.toml`, console scripts, per-user settings dir); verified with `pip install` into a venv | Done |
| A5 | `tests/smoke_test.sh` (portable bash, 500-event `beta_lite` run); `ctest` passes locally in about 4 s against Geant4 11.3.2 | Done |
| A6 | `.github/workflows/ci.yml` (4-runner matrix, micromamba env with `geant4=11.4.3`) | Written, **not yet run** (nothing pushed) |
| A7 | README (conda install section, versioning, build options), `gui/README.md`, `ReleaseNotes.md` (v11.4.3 section), `CLAUDE.md` | Done |
| A8 | Local build against the conda-forge `geant4` package (micromamba installed at `~/.local/bin/micromamba`, env `g4` under `~/micromamba`) | Done: configure/build/ctest/install/smoke test and GUI `pip install` all pass; needed `-DCMAKE_PREFIX_PATH=$CONDA_PREFIX` so CMake does not pick the macOS SDK libexpat |
| A9 | Commit, push, GitHub Actions green on all runners | Todo |
| A10 | Tag `v11.4.3`, create GitHub Release, record tarball sha256 | Todo |
| B1 | `recipe.yaml` + `build_grasshopper.sh` written under `packaging/conda-forge/recipes/grasshopper/` (with a `packaging/conda-forge/README.md`); `sha256` is a placeholder until the tag exists | Done (unsubmitted) |
| B2 | Local `rattler-build` of both outputs from the working tree (`path:` source) with the conda-forge pinning variant config; embedded package tests (`--version`, file checks, 500-event smoke run, GUI imports/`pip check`) pass; both `.conda` files installed into a fresh env from a local channel and an installed example run end to end with VRML output | Done (osx-arm64 only; conda-forge CI covers the rest) |
| C1 | PR to `conda-forge/staged-recipes` | Todo |
| C2 | Feedstock created, `linux_aarch64` confirmed, first packages on the channel | Todo |
| C3 | End-to-end check from the conda-forge channel (install, run example, open `.wrl` with the VTK viewer) | Todo (done locally from the rattler-build output channel; repeat after publication) |

---

## Phase A: upstream changes

Goal: make the repository releasable and installable with `cmake --install`, so the conda recipe is a thin wrapper. All of this is one PR followed by the `v11.4.3` tag.

### Layout and hygiene

| File / path | Change | Why |
|---|---|---|
| `VERSION` | New, contains `11.4.3`. | Single source of truth for CMake, `pyproject.toml` and the tag name. |
| `exec/Examples/` -> `examples/` | Moved with `git mv`; `xsi:noNamespaceSchemaLocation` in every example (and in `exec/unit_test/*.gdml`) now reads `../../schema/gdml.xsd`. | The repo layout now equals the installed layout (`share/grasshopper/{schema,examples}`), so xerces resolves the schema relative to the GDML file in both places. |
| `.gitignore` | Added `.DS_Store`, `__pycache__/`, `*.pyc`, `.vscode/`, `.fuse_hidden*`, `awkout*.txt`, `md5out.txt`, `build/`, `dist/`, `*.egg-info/`, `gui/grasshopper_gui_settings.json`. Tracked copies of these were removed with `git rm --cached`. | Clean tarball. |
| `GNUmakefile` | Kept, header marks it as the legacy geant4make build; CMake is the supported build. | |
| `documentation/GDMLmanual.pdf` | Kept in the repo, not installed (it is CERN's). | |

### `CMakeLists.txt`

- `file(STRINGS VERSION ...)` -> `project(grasshopper VERSION ... LANGUAGES CXX)`; `include(GNUInstallDirs)`; CMake 3.17 minimum.
- `find_package(Geant4 11.0 REQUIRED gdml)`; `ui_all vis_all` are only requested when `WITH_GEANT4_UIVIS=ON` (default ON for developers). Requesting them is what drags OpenGL/X11/Qt into the link set; the conda build turns the option OFF. `G4VIS_USE` is always defined and the `G4DAWNFILE.hh` / `G4VRML2.hh` / `G4VRML2File.hh` header checks always run, because VRML file output needs only core Geant4. Verified: a core-only build still writes `.wrl` files.
- Options: `WITH_GEANT4_UIVIS` (ON), `WITH_ROOT` (OFF), `BUILD_TESTING` (ON), `SHOW_WARNINGS` (OFF).
- Compile definitions on the target: `GRASSHOPPER_VERSION="<version>"` and `GRASSHOPPER_DATADIR="<CMAKE_INSTALL_FULL_DATADIR>/grasshopper"` (conda's prefix relocation rewrites the baked-in prefix at install time).
- Install rules: binary -> `bin/`; `schema/` -> `share/grasshopper/schema/`; `examples/` (`*.gdml`, `*.txt`, `*.mac` only, `debug/` excluded) -> `share/grasshopper/examples/`; `README.md`, `ReleaseNotes.md`, `LICENSE`, `COPYRIGHT` -> `share/doc/grasshopper/`.
- `enable_testing()` + `add_test(NAME smoke COMMAND bash tests/smoke_test.sh $<TARGET_FILE:grasshopper> ${PROJECT_SOURCE_DIR})`.
- `CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE` (+ `CMAKE_MACOSX_RPATH` on Apple), added after finding that the installed binary had no RPATH and dyld could not locate `libG4*.dylib` when run from the install prefix. Verified after the fix.
- The dead `VIS_SCRIPTS` loop was dropped.

### `grasshopper.cc` and `include/Analysis.hh`

- `--version` / `-v`: prints `grasshopper <GRASSHOPPER_VERSION> (<G4Version>)` (needs `G4Version.hh`).
- `--help` / `-h`: usage line `grasshopper <gdml_configuration_file> <output_name> [seed]`; what is written (`<output_name>.dat`, `.root` only with ROOT support, `g4_NN.wrl` when `VRMLvisualizationOn=1`); files read from the cwd on demand (`input_spectrum.txt`, `beam_width.txt`, `vis.mac`); example locations (GitHub link and the installed `GRASSHOPPER_DATADIR/examples`); citation DOI and homepage.
- Wrong argument count: "Wrong input!" followed by the usage text on stderr, exit status 2.
- The dead `G4UI_USE_ROOT` block in `include/Analysis.hh` was deleted.

### GUI as a Python package

```
pyproject.toml                        (repo root; name grasshopper-gui, version from VERSION)
gui/grasshopper_gui/__init__.py
gui/grasshopper_gui/_paths.py         (config dir, settings path, icon path, package version)
gui/grasshopper_gui/app.py            (was gui/grasshopper_gui.py)
gui/grasshopper_gui/novis.py          (was gui/grasshopper_gui_novisualization.py)
gui/grasshopper_gui/vtk_viewer.py     (was gui/grasshopper_vtk_viewer.py, now has main())
gui/grasshopper_gui/assets/icon.png
```

- Build backend `setuptools>=77`; `requires-python >=3.9`; dependencies `numpy>=1.21`, `matplotlib>=3.5`, `platformdirs>=3`; optional extra `vtk` (`vtk>=9.0`); console scripts `grasshopper-gui`, `grasshopper-gui-novis`, `grasshopper-vtk-viewer`, each with `--version` (from `importlib.metadata`) so the conda test has a headless check.
- Settings moved out of the (read-only when installed) source directory to the per-user config directory via `platformdirs.user_config_dir("grasshopper")`, with a fallback to `~/Library/Application Support/grasshopper` (macOS) or `$XDG_CONFIG_HOME/grasshopper` (elsewhere).
- Icon loaded with `importlib.resources`; default executable is `shutil.which("grasshopper")`; the viewer is launched as `python -m grasshopper_gui.vtk_viewer` (no `sys.path` hack).
- Wrong organisation link in `gui/README.md` fixed. Verified with `pip install` into a venv.

### `tests/smoke_test.sh`

Portable bash (`set -euo pipefail`). Usage `smoke_test.sh [grasshopper-binary] [root-dir]` where `root-dir` contains `schema/` and `examples/` (the source tree or `<prefix>/share/grasshopper`). It copies `examples/beta/beta_lite.gdml` to a temp dir with `EventsToRun=500`, `VRMLvisualizationOn=0` and the schema location rewritten to an absolute path, runs `--version`, runs the simulation with seed `12345`, and fails on `VALIDATION ERROR` in the log or a `.dat` with no data rows. Prints the row count and md5 (`md5sum` or `md5 -q`). Used by ctest, GitHub Actions and the conda recipe test. `exec/unit_test/unit_test.sh` remains the long physics regression test.

### `.github/workflows/ci.yml`

Triggers: push to `master`, tags `v*`, pull requests. Matrix: `ubuntu-latest`, `ubuntu-24.04-arm`, `macos-14`, `macos-15-intel` (`fail-fast: false`). Steps: `mamba-org/setup-micromamba@v2` with `cache-environment: true` and `geant4=11.4.3 xerces-c clhep expat zlib cmake ninja cxx-compiler python>=3.10 pip setuptools tk numpy matplotlib-base platformdirs` from conda-forge; configure with `-DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DWITH_GEANT4_UIVIS=OFF -DWITH_ROOT=OFF`; build; `ctest`; install; `grasshopper --version`, `--help`, `smoke_test.sh grasshopper $CONDA_PREFIX/share/grasshopper`; `pip install --no-deps --no-build-isolation .` and `grasshopper-gui --version`. This proves the exact dependency set the recipe declares. Environment caching matters because the Geant4 datasets are about 2 GB. **Not run yet.**

### Docs

README gained an "Install with conda (recommended)" section, the versioning policy, a note that Homebrew/apt are unavailable, the "no ROOT in the conda package" note and the CMake options. `ReleaseNotes.md` has a v11.4.3 section. `gui/README.md` and `CLAUDE.md` updated.

### Release steps (todo)

1. Install micromamba locally and build against the conda-forge `geant4` package (see [Verification](#verification)).
2. Commit, push, confirm GitHub Actions is green on all four runners.
3. `git tag -a v11.4.3`, push the tag, create a GitHub Release from it in the web UI (`gh` is not installed on the dev machine).
4. Record the tarball checksum for the recipe:
   ```bash
   curl -sL https://github.com/ustajan/grasshopper/archive/refs/tags/v11.4.3.tar.gz | shasum -a 256
   ```

---

## Phase B: the recipe

Submitted to a fork of [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes) as `recipes/grasshopper/recipe.yaml` (v1 format, built by rattler-build) plus `recipes/grasshopper/build_grasshopper.sh`. A copy is to be kept in this repo under `packaging/conda-forge/` for reference (the feedstock becomes the authoritative copy after merge). Both files exist under `packaging/conda-forge/recipes/grasshopper/`; the listing below mirrors them.

### `build_grasshopper.sh`

```bash
#!/usr/bin/env bash
set -euxo pipefail

cmake -S "$SRC_DIR" -B build -G Ninja ${CMAKE_ARGS} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DWITH_GEANT4_UIVIS=OFF \
  -DWITH_ROOT=OFF \
  -DBUILD_TESTING=OFF
cmake --build build --parallel "${CPU_COUNT}"
cmake --install build
```

### `recipe.yaml` (draft)

```yaml
schema_version: 1
context:
  version: "11.4.3"          # == Geant4 version validated against; keep in sync
recipe:
  name: grasshopper
  version: ${{ version }}
source:
  url: https://github.com/ustajan/grasshopper/archive/refs/tags/v${{ version }}.tar.gz
  sha256: <FILL>
build:
  number: 0
outputs:
  - package: { name: grasshopper }
    build:
      skip: win
      script: { file: build_grasshopper.sh }
    requirements:
      build: [ "${{ compiler('cxx') }}", "${{ stdlib('c') }}", cmake, ninja ]
      # No explicit clhep: geant4 pins it exactly and the global pinning would conflict.
      # xerces-c/expat/zlib/freetype are only needed so Geant4Config.cmake's
      # find_dependency() calls succeed; grasshopper links them through Geant4.
      host:  [ "geant4 ${{ geant4_version }}.*", xerces-c, expat, zlib, freetype ]
      run:   [ geant4 ]   # geant4's run_exports adds the exact-patch pin
      ignore_run_exports: { from_package: [ xerces-c, expat, zlib, freetype ] }
    tests:
      - script:
          - grasshopper --version
          - grasshopper --help
          - test -f $PREFIX/share/grasshopper/schema/gdml.xsd
          - test -f $PREFIX/share/grasshopper/examples/beta/beta_lite.gdml
          - bash tests/smoke_test.sh grasshopper $PREFIX/share/grasshopper
        files: { source: [ tests/ ] }
  - package: { name: grasshopper-gui }
    build:
      noarch: python
      skip: not (linux and x86_64)       # build the noarch package once
      script: python -m pip install . -vv --no-deps --no-build-isolation
      python:
        entry_points:
          - grasshopper-gui = grasshopper_gui.app:main
          - grasshopper-gui-novis = grasshopper_gui.novis:main
          - grasshopper-vtk-viewer = grasshopper_gui.vtk_viewer:main
    requirements:
      host: [ "python ${{ python_min }}.*", pip, "setuptools >=77" ]
      run:  [ "python >=${{ python_min }}", tk, "numpy >=1.21", "matplotlib-base >=3.5", "platformdirs >=3", grasshopper ]
      run_constraints: [ "vtk >=9.0" ]
    tests:
      - python: { imports: [ grasshopper_gui ], pip_check: true, python_version: "${{ python_min }}.*" }
      - script: [ grasshopper-gui --version ]
about:
  homepage: https://github.com/ustajan/grasshopper
  repository: https://github.com/ustajan/grasshopper
  license: GPL-3.0-or-later
  license_file: LICENSE
  summary: Geant4 front end driven by GDML files, with text output and VRML visualization
  description: |
    (short paragraph + citation doi:10.1109/NSS/MIC44867.2021.9875720)
extra:
  recipe-maintainers: [ ustajan ]
```

Notes on the draft:

- Host dependencies are minimal because `WITH_GEANT4_UIVIS=OFF` stops `Geant4Config.cmake` from resolving OpenGL/X11/Qt targets. If the Linux configure step still demands `X11::X11` / `OpenGL::GL`, copy the Linux host list from the geant4-feedstock (`libgl-devel`, `xorg-libx11`, `xorg-libxmu`, ...).
- The Qt vs no-Qt `geant4` variant is irrelevant once only core libraries are linked; do not mention `geant4-qt-mutex`.
- The smoke test needs the datasets: `geant4` pulls `geant4-data-*`, whose activation scripts set `G4*DATA`. If the ~2 GB test-phase download times out on conda-forge CI, reduce the conda test to `--version` plus the file checks and keep the simulation test in GitHub Actions.
- `linux-aarch64` is cross-compiled on conda-forge; script tests are skipped there automatically.
- No explicit `run` dependency on `geant4` is needed: its `run_exports` adds `geant4 >=11.4.3,<11.4.4` (exact patch) to the `grasshopper` package.

---

## Phase C: submission and maintenance

Reference: [conda-forge docs, "Contributing packages"](https://conda-forge.org/docs/maintainer/adding_pkgs/).

### Submission

1. Fork `conda-forge/staged-recipes`, add `recipes/grasshopper/{recipe.yaml,build_grasshopper.sh}`, open a PR titled "Add grasshopper and grasshopper-gui".
2. PR checklist: tag tarball URL + sha256; SPDX license identifier (`GPL-3.0-or-later`) and `LICENSE` file; tests present for both outputs; maintainer (`ustajan`) has confirmed willingness in the PR.
3. staged-recipes CI builds `linux-64`, `osx-64`, `osx-arm64`. When green, ping the C/C++ review team (`conda-forge/help-c-cpp`) as the PR template instructs.
4. After merge a `conda-forge/grasshopper-feedstock` repository is created automatically with `ustajan` as maintainer; packages appear on the channel within about an hour.
5. Confirm `linux_aarch64` is enabled in the feedstock's `conda-forge.yml`; if not, open a rerender PR (comment `@conda-forge-admin, please rerender`).
6. Add a second maintainer when possible.

### Releasing a new version

**New Geant4 patch or minor release on conda-forge (e.g. 11.4.4 or 11.5.0).** Because `geant4`'s run_export is an exact-patch pin, existing grasshopper builds will not install with the new Geant4; grasshopper must be rebuilt.

1. Upstream: bump `geant4=11.4.4` in `.github/workflows/ci.yml`, confirm CI is green.
2. Set `VERSION` to `11.4.4`, add a ReleaseNotes section, commit, tag `v11.4.4`, create the GitHub Release.
3. The conda-forge **autotick bot** (regro-cf-autotick-bot) watches the GitHub tags, opens a PR on the feedstock that bumps `context.version` and the sha256 and resets `build.number` to 0. The `geant4 ${{ version }}.*` host pin follows automatically because it is derived from the version.
4. Review the bot PR, wait for CI, merge. The old `grasshopper 11.4.3` keeps installing with `geant4 11.4.3` as long as that build remains on the channel.

**Grasshopper-only fix.** Set `VERSION` to `11.4.3.1`, tag `v11.4.3.1`; the bot opens the PR; merge.

**Recipe-only fix** (dependency tweak, test change). PR on the feedstock bumping `build.number`; no upstream tag needed.

---

## Verification

### Phase A on the development Mac (micromamba at `~/.local/bin/micromamba`, root prefix `~/micromamba`)

```bash
curl -Ls https://micro.mamba.pm/install.sh | bash          # install micromamba
micromamba create -n g4 -c conda-forge geant4=11.4.3 xerces-c clhep expat zlib \
    cmake ninja cxx-compiler python tk numpy matplotlib-base platformdirs pip
micromamba activate g4

cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" -DWITH_GEANT4_UIVIS=OFF -DWITH_ROOT=OFF
cmake --build build --parallel
ctest --test-dir build --output-on-failure
cmake --install build

grasshopper --version        # must print: grasshopper 11.4.3 (... geant4-11-04-patch-03 ...)
bash tests/smoke_test.sh grasshopper "$CONDA_PREFIX/share/grasshopper"
pip install --no-deps --no-build-isolation .
grasshopper-gui --version
grasshopper-gui              # confirm settings land in ~/Library/Application Support/grasshopper/
```

Then push and require GitHub Actions green on all four runners before tagging.

### Phase B locally (rattler-build)

```bash
micromamba create -n rb -c conda-forge rattler-build
micromamba activate rb
cd staged-recipes
micromamba install -n rb -c conda-forge conda-forge-pinning   # provides python_min, c_stdlib, compilers
rattler-build build --recipe packaging/conda-forge/recipes/grasshopper \
  --variant-config ~/micromamba/envs/rb/conda_build_config.yaml --test native   # native osx-arm64
# or: python build-locally.py
```

Both `.conda` artifacts must pass their embedded tests. Then install them into a fresh environment and rerun the smoke test by hand:

```bash
micromamba create -n x -c conda-forge -c ./output grasshopper grasshopper-gui
micromamba activate x
bash tests/smoke_test.sh grasshopper "$CONDA_PREFIX/share/grasshopper"
```

### Phase C from the channel

```bash
micromamba create -n x -c conda-forge grasshopper grasshopper-gui vtk
micromamba activate x
cp -r "$CONDA_PREFIX/share/grasshopper/examples/beta" . && cd beta
# set VRMLvisualizationOn=1 in beta_lite.gdml, then:
grasshopper beta_lite.gdml test
grasshopper-vtk-viewer g4_00.wrl
```

---

## Risks and open questions

| Risk | Mitigation |
|---|---|
| **osx-64 deployment target.** `grasshopper.cc` uses `std::filesystem` (macOS 10.15+). If conda-forge's osx-64 `c_stdlib_version` is lower, the build fails. | Add `variants.yaml` with `c_stdlib_version: "10.15"` for osx x86_64, mirroring the geant4-feedstock. |
| **Installed binary RPATH.** First install lacked an RPATH; dyld could not find `libG4*.dylib`. | `CMAKE_INSTALL_RPATH_USE_LINK_PATH` added and verified. conda-build/rattler-build also relocate RPATHs at package time, so this mainly matters for plain `cmake --install`. |
| **Schema lookup.** xerces resolves `noNamespaceSchemaLocation` relative to the GDML file. Installed examples work in place; copies elsewhere print non-fatal `G4GDML: VALIDATION ERROR` lines. | Documented in `--help`. Optionally add a `--no-validate` flag (`parser.Read(file, false)`) in a later release. |
| **Dataset size** (~2 GB) in GitHub Actions and in the conda test phase. | `cache-environment: true` in CI; trim the conda test to `--version` + file checks if the test phase times out. |
| **noarch output in a multi-platform recipe.** The output-level `skip: not (linux and x86_64)` avoids duplicate uploads. | If the linter rejects it, drop the skip and rely on the upload step's duplicate handling. |
| **GUI duplication.** `novis.py` is a near-copy of `app.py`. | Shipped as-is; flagged for consolidation later. |
| **Exact-patch coupling to Geant4.** Every Geant4 patch on conda-forge requires a grasshopper release and a feedstock PR. | Accepted by design; the autotick bot does most of the work. |
| **Single maintainer.** | Add a second feedstock maintainer when possible. |
| Open: does the Linux configure step pull in X11/OpenGL even with `WITH_GEANT4_UIVIS=OFF`? | Will be answered by the first CI run; fallback is the geant4-feedstock host list. |
| Resolved: built, tested and installed against the conda-forge Geant4 11.4.3 package in a local micromamba env (item A8). |

---

## Links

- conda-forge: [Contributing packages](https://conda-forge.org/docs/maintainer/adding_pkgs/), [staged-recipes](https://github.com/conda-forge/staged-recipes)
- [geant4-feedstock](https://github.com/conda-forge/geant4-feedstock)
- [Debian ITP bug #965964](https://bugs.debian.org/965964) (Geant4 in Debian)
- [Geant4 installation guide](https://geant4.web.cern.ch/documentation/dev/ig_html/InstallationGuide/index.html) (package-manager section)
- [grasshopper examples on GitHub](https://github.com/ustajan/grasshopper/tree/master/examples)
- Citation: A. Danagoulian et al., "Grasshopper, a Geant4 Front End: Validation and Benchmarking," IEEE NSS/MIC 2021, doi:[10.1109/NSS/MIC44867.2021.9875720](https://doi.org/10.1109/NSS/MIC44867.2021.9875720)
