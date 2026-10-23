# conda-forge deployment: status report

**Date:** 2026-10-23
**Overall state:** release published, recipe submitted to conda-forge, waiting for volunteer review.
Companion page with the full plan and background: [Conda-Forge-Packaging](Conda-Forge-Packaging.md).

## Summary

grasshopper is being made installable with `conda install -c conda-forge grasshopper grasshopper-gui`.
Homebrew and Debian/Ubuntu were ruled out because neither carries Geant4 (license questions on their
side, Debian ITP stalled since 2020), whereas conda-forge already ships Geant4 11.4.3 with GDML support
and all datasets for Linux (x86_64, aarch64) and macOS (Intel, Apple silicon).

Everything on the grasshopper side is done and verified. The remaining step, review and merge of the
recipe by conda-forge volunteers, is outside our control and typically takes days to a few weeks.

## What was delivered

| Item | Where |
|---|---|
| Repository changes (build system, CLI flags, examples move, GUI package, CI, hygiene) | [PR #25](https://github.com/ustajan/grasshopper/pull/25), merged into `master` as `3f893b9` |
| Release tag and GitHub Release | [v11.4.3](https://github.com/ustajan/grasshopper/releases/tag/v11.4.3) |
| Source tarball checksum used by the recipe | `644dee6b0b9f65cc9b6fb19851d86ee267adbc92535b43dec34b39b4e9a6c34d` |
| conda-forge recipe (copy kept in the repo) | `packaging/conda-forge/recipes/grasshopper/` |
| conda-forge submission | [staged-recipes #35332](https://github.com/conda-forge/staged-recipes/pull/35332), from the fork `ustajan/staged-recipes`, branch `grasshopper` |
| Continuous integration | `.github/workflows/ci.yml`, builds against the conda-forge Geant4 on four runners |

### Repository changes in brief

- Version lives in `VERSION` (11.4.3, tracking the Geant4 release validated against). CMake and
  `pyproject.toml` read it. `grasshopper --version` and `--help` were added; `--help` points to the
  examples on GitHub and to the installed copy.
- `make install` now installs `share/grasshopper/{schema,examples}` next to the binary and keeps the
  Geant4 library path in the binary's RPATH.
- `exec/Examples` became top-level `examples/`; schema references are `../../schema/gdml.xsd` everywhere.
- `-DWITH_GEANT4_UIVIS=OFF` links core Geant4 only; VRML `.wrl` output still works. This is what the
  conda package uses, so it needs no OpenGL/X11/Qt.
- The GUI is the installable package `grasshopper-gui` (`gui/grasshopper_gui/`), with console scripts
  `grasshopper-gui`, `grasshopper-gui-novis`, `grasshopper-vtk-viewer`. Settings moved to the per-user
  config directory.
- `tests/smoke_test.sh` runs a 500-event simulation; it is used by `ctest`, by CI and by the recipe test.
- Editor settings, `.DS_Store`, byte-code and unit-test scratch outputs are no longer tracked.

## Verification performed

| Check | Result |
|---|---|
| Build, `ctest`, install, smoke test against the local Geant4 11.3.2 | pass |
| Build, `ctest`, install, smoke test against conda-forge Geant4 11.4.3 (micromamba env) | pass |
| `pip install` of `grasshopper-gui` into a venv and into the conda env; `pip check` | pass |
| `rattler-build` of both outputs with the conda-forge pinning, embedded package tests | pass (osx-arm64) |
| Fresh env from the local build channel; installed example run with VRML output; GUI entry points | pass |
| GitHub Actions on PR #25: ubuntu-latest, ubuntu-24.04-arm, macos-14, macos-15-intel | all green (run 39908163846) |
| conda-forge CI on staged-recipes #35332: linter, linux_64 (both packages), osx_64; win skipped by design | all green |

Two problems were found and fixed along the way:

- The installed binary initially had no RPATH and could not find `libG4*.dylib`; fixed with
  `CMAKE_INSTALL_RPATH_USE_LINK_PATH` in `CMakeLists.txt`.
- On the Apple-silicon GitHub runner, CMake read an old `expat.h` from the macOS SDK and rejected
  Geant4's dependency check; fixed in CI by passing `EXPAT_ROOT`, `ZLIB_ROOT`, `XercesC_ROOT` and
  `Freetype_ROOT` set to the conda prefix. The conda-forge build itself was unaffected.

## conda-forge review status

- PR #35332 is labeled `review-requested`; the conda-forge bot pinged the staged-recipes team and a
  comment mentions `conda-forge/help-c-cpp`.
- The author (`ustajan`) posted the required maintainer confirmation.
- Watch progress on the PR page or with `gh pr view 35332 --repo conda-forge/staged-recipes`.
- If there is no response after about a week, comment `@conda-forge-admin, please ping team` again
  or ask on the conda-forge Zulip chat.

## What happens after the merge

1. conda-forge creates `conda-forge/grasshopper-feedstock` and adds `ustajan` as maintainer.
2. Packages appear on the channel within about an hour. Verify on a Mac or Linux box:
   `micromamba create -n x -c conda-forge grasshopper grasshopper-gui`, run an example from
   `$CONDA_PREFIX/share/grasshopper/examples`, open the `.wrl` with `grasshopper-vtk-viewer`
   (after `micromamba install vtk`).
3. Check that `linux_aarch64` and `osx_arm64` are enabled in the feedstock's `conda-forge.yml`;
   open a rerender PR if not.
4. Update the status table in [Conda-Forge-Packaging](Conda-Forge-Packaging.md) and the README badge, if any.

## How to release the next version

1. Validate grasshopper against the target Geant4 release (update the `geant4=` pin in
   `.github/workflows/ci.yml` and let CI run).
2. Set `VERSION` (for example `11.4.4`, or `11.4.3.1` for a grasshopper-only fix), add a section to
   `ReleaseNotes.md`, merge to `master`.
3. `git tag -a vX.Y.Z && git push origin vX.Y.Z`, then `gh release create vX.Y.Z`.
4. The conda-forge bot opens a version-bump PR on the feedstock. If the Geant4 version changed, edit
   `geant4_version` in that PR's `recipe.yaml`. Merge once its CI is green.
5. Keep `packaging/conda-forge/recipes/grasshopper/` in sync with the feedstock for reference.

## Open items and known limitations

- The conda package has no ROOT support (ASCII `.dat` output only). Users who need `.root` files build
  from source with `-DWITH_ROOT=ON`.
- GDML files copied away from the examples tree print non-fatal `G4GDML: VALIDATION ERROR` lines unless
  their schema path is adjusted. A `--no-validate` flag is a possible later addition.
- `gui/grasshopper_gui/novis.py` duplicates most of `app.py`; it ships as a second entry point and
  should be consolidated eventually.
- The feedstock will pin each grasshopper build to the exact Geant4 patch release it was built against,
  so every Geant4 patch bump on conda-forge calls for a new grasshopper tag and rebuild.
