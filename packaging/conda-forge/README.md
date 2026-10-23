# conda-forge recipe for grasshopper

This directory holds the recipe that is submitted to
[conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes). After the
first merge, conda-forge creates `grasshopper-feedstock`, and that repository (not this
directory) becomes the source of truth; keep this copy in sync for reference.

Two packages are produced from one recipe:

| package           | contents                                                     |
|-------------------|--------------------------------------------------------------|
| `grasshopper`     | the executable, `share/grasshopper/{schema,examples}`, docs  |
| `grasshopper-gui` | noarch Python package with the `grasshopper-gui*` scripts    |

## Submitting a new release

1. Validate upstream against the target Geant4 release, set `VERSION`, update
   `ReleaseNotes.md`, tag `vX.Y.Z` and create a GitHub Release.
2. First time only: copy `recipes/grasshopper/` into a fork of staged-recipes, fill in
   `sha256` (see below), open a PR. CI builds linux-64, osx-64 and osx-arm64.
3. Later releases: the conda-forge autotick bot opens a version-bump PR on the feedstock
   when it sees the new tag. Review and merge.

```bash
VERSION=$(cat VERSION)
curl -sL https://github.com/ustajan/grasshopper/archive/refs/tags/v${VERSION}.tar.gz | shasum -a 256
```

## Testing the recipe locally

```bash
micromamba create -n rb -c conda-forge rattler-build
micromamba install -n rb -c conda-forge conda-forge-pinning   # supplies python_min, c_stdlib, compiler variants
micromamba run -n rb rattler-build build --recipe packaging/conda-forge/recipes/grasshopper \
  --variant-config ~/micromamba/envs/rb/conda_build_config.yaml --test native   # the pinning file sets the channels
```

To build from the working tree before a tag exists, temporarily replace the `source:`
block with `path: ../../../..` (relative to the recipe directory).

## Versioning

The grasshopper version is the Geant4 release it was validated against (`11.4.3`), with
an optional fourth component for grasshopper-only fixes (`11.4.3.1`). The recipe pins
`geant4` to that release in `host:`, and the conda-forge `geant4` package's
`run_exports` pins the runtime dependency to the same patch release. Recipe-only changes
bump `build.number` instead.
