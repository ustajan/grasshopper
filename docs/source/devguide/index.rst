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


Grasshopper Specific Files
-------------------------
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