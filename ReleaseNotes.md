# v11.4.3 Release Notes

Validated against Geant4 11.4.3. First release packaged for [conda-forge](https://conda-forge.org/)
(`conda install -c conda-forge grasshopper grasshopper-gui`).

 *  Versioning now tracks the Geant4 release grasshopper was validated against, with an
    optional fourth component for grasshopper-only fixes (e.g. `11.4.3.1`). The version
    lives in the top-level `VERSION` file and is read by CMake and `pyproject.toml`.
 *  New command-line flags: `grasshopper --version` and `grasshopper --help`. Wrong
    arguments now print the usage text and exit with status 2.
 *  `make install` now installs the GDML schema and the example inputs under
    `<prefix>/share/grasshopper/{schema,examples}` next to the binary.
 *  The example inputs moved from `exec/Examples/` to top-level `examples/`, with their
    schema references pointing to `../../schema/gdml.xsd` so they validate both in the
    source tree and when installed.
 *  CMake: Geant4 11.0 is the minimum. `-DWITH_GEANT4_UIVIS=OFF` now links only core
    Geant4 (VRML `.wrl` output still works); `ctest` runs `tests/smoke_test.sh`, a
    portable 500-event smoke simulation.
 *  The Python GUI is an installable package (`pip install .` or the `grasshopper-gui`
    conda package) with console scripts `grasshopper-gui`, `grasshopper-gui-novis` and
    `grasshopper-vtk-viewer`. GUI settings moved from the source directory to the
    per-user config directory (`~/Library/Application Support/grasshopper/` on macOS,
    `~/.config/grasshopper/` on Linux).
 *  Continuous integration (GitHub Actions) builds against the conda-forge Geant4
    package on Linux and macOS.
 *  Repository cleanup: editor settings, `.DS_Store`, byte-code and unit-test scratch
    outputs are no longer tracked.

# v. 11.3.2 Release Notes

 *  Currently, the simulation produces separate entries for separate detector hits for a given track.  Additionally, if a track hits a detector multiple times, multiple entries will be generated.  This then may require (depending on the goals of the analysis) to combine these tracks during the post-processing, e.g. during the `SaveTrackInfo` mode. 
 *  In future releases this feature may be modified, e.g. combining multiple hits on a given detector by a single track.
