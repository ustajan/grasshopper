.. _devguide:

======================
Dev Guide
======================

.. toctree::
    :numbered:
    :maxdepth: 3


This Dev Guide serves to brief Grasshopper users on the functionality of each file
in the codebase of the Grasshopper program. For devs, the shorthand for Grasshopper
will be GRSHPR, a recursive acronym for "Grasshopper Realistically Simulates High-Energy
Particles & Radiation".

# Bugs
Grasshoppers hate bugs. The code has been tested fairly well, however there are probably still some bugs in it.
If you run against a strange behavior, please prepare a brief report with the following information

- the platform you are running it on
- the gdml file (attach it)
- a description of the symptoms, along with the relevant part of the screen output

Email the bug report to mailto:aregjan@mit.edu.

Please generate a GitHub pull request if you believe that you have source code changes
to make in order to avoid the bug.

Grasshopper Specific Files
--------------------------

The base of Grasshopper which interacts with G4 is written in C++.

The files included in the src/ and include/ directories from root are as follows.

src/

Analysis.cc

AnalysisManager.cc

DADEphysicsList.cc

DMXMaxTimeCuts.cc

DMXMinEkineCuts.cc

DMXPhysicsList.cc

EventAction.cc

EventActionMessenger.cc

GammaNuclearPhysics.cc

PhysicsList.cc

PrimaryGeneratorAction.cc

RunAction.cc

StackingAction.cc

SteppingAction.cc

VisManager.cc


src/

Analysis.hh

AnalysisManager.hh

DADEphysicsList.hh

DetectorConstruction.hh

DMXMaxTimeCuts.hh

DMXMinEkineCuts.hh

DMXPhysicsList.hh

DMXSpecialCuts.hh

EventAction.hh

EventActionMessenger.hh

GammaNuclearPhysics.hh

PhysicsList.hh

PhysicsListLowEnergy.hh

PrimaryGeneratorAction.hh

RunAction.hh

StackingAction.hh

SteppingAction.hh

VisManager.hh