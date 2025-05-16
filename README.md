grasshopper
===========

This application is based on the geant4 development toolkit, which allows to program complex particle
tracking (e.g. gamma, electrons, protons, etc) and particle-matter interaction MC simulations.
Grasshopper is a simple geant4 application, where all the geometries and even generators parameters are 
defined in a gdml file, with the purpose of setting up quick and simple simulations.  The
goal is to allow users with no C++ and Geant4 knowledge *quickly* set up and run simulations.

Author:  		Areg Danagoulian

Creation time:  11/2015  
Last update:    continous

For copyright and licensing see files COPYRIGHT and LICENSE.

To install
==

The user is required/advised to have the following:
	
* xerces.  This will allow the GDML parser capability.
* Built and installed geant4 libraries.  
	* In the cmake configuration stage, the following flag needs to be passed: `-DGEANT4_USE_GDML=ON`.  
	* Here's an example of what a Geant4 cmake command looks like(to be ran from `geant_build`): `cmake -DGEANT4_USE_GDML=ON -DGEANT4_INSTALL_DATA=ON -DCMAKE_INSTALL_PREFIX=../geant4-v11.3.2-install ../geant4-v11.3.2 `
* ROOT -- optional.  Has been tested with version 6.32.12.  If you do not have ROOT the make process will recognize that and exclude it from the build.

__Geant4 compatibility__:  most recently, grasshopper and been built against and tested with **Geant4 versions 11.2.2 and 11.3.2**.

__Important note__:  these days geant4 primarily works via the cmake framework.  However grasshopper can also use the older Makefile framework.  It is important that you source the appropriate shell script in geant4 directories to enable all the env. variables that are necessary for Makefile to work correctly.  In my particular case I have the following line in my .bashrc file, please modify this accordingly for your build/configuration:

`. ~/geant4/geant4-v11.3.2-install/share/Geant4/geant4make/geant4make.sh `

If all the regular geant4 installations and configurations are ready, then the user can get the code by

`git clone https://github.com/ustajan/grasshopper.git`

To build with GNUmake
==
```
cd grasshopper
make -jN
```
where N is the number of your cores.

To build with CMake
==
```
cd grasshopper
mkdir RunGrasshopper && cd RunGrasshopper
cmake .. && make -jN
```
where N is the number of your cores.  This will locally generate a binary, `grasshopper`, which you can then run something like the following:

`./grasshopper ../exec/Examples/beta/beta_lite.gdml test.root`

Note: cmake build doesn't include visualization.  See Issues.

To run
==
`grasshopper input.gdml output.root`


Tutorial
==
The best way to learn how to use grasshopper is by using the tutorial on the project wiki, [here](https://github.com/ustajan/grasshopper/wiki).  You can also get there by going to Wiki link above.

Input
==
 * input.gdml -- the geometry definition markup language file.  This file defines
   * the geometries of the objects and detectors, as well as their materials and the positioning
   * the particle type, energy, and direction
   * various computational optimization options
   * output formats
 * input\_spectrum.txt -- this is currently a fixed file name.  The user can define the energy of the particle.
   If the energy is set negative, the code defaults to reading the energy spectrum from "input\_spectrum.txt" and samples
   the energy from that spectrum.
   
Output
==
The code will generate three files:

 * output.root -- The code will always generate a root file, as specified in the input arguments.
 * output.dat  -- depending on the settings in the gdml file, it can also generate a simple ascii file, output.dat,  which can then be read into python/matlab/etc.
 * g4_00.wrl.  This is the VRML visualization file.  The settings for this file's content are defined in the gdml file.
   The wrl file can be loaded in paraview (http://www.paraview.org/download/), thus allowing for a rendering of the
   geometries and some particle tracks.

The root output structure (which is identical to the ascii output) can be somewhat complex. The output of the simulation can be
thought of as a table -- where every line is an entry corresponding to a **particular set of information**
within an event. Below is a set of entries in the ASCII output from a simulation of a 40meV neutron beam undergoing capture inside two 3He ionization chamber (numbered 5 and 37):

![alt text](https://github.com/ustajan/grasshopper/blob/master/documentation/ascii_long.png?raw=true)

By enabling the BriefOutput flag in the gdml, it's is possible to get the shorter version of the above:

![alt text](https://github.com/ustajan/grasshopper/blob/master/documentation/ascii_short.png?raw=true)


There are three type of entries:
 * IsSurfaceHitTrack.  These entries are registered when a track enters the detector volume.  To filter out these events, simply search for all entries where IsSurfaceHitTrack==1
 * regular tracks.  At the end of an event all the tracks inside the detector can be recorded in the form of individual entries.  All entries for which IsSurfaceHitTrack!=1 && IsEdepositedTotalEntry!=1 are regular track entries.  These entries are useful for debugging and diagnostic purposes, as well as for general studies of the interaction physics of the detector.
 * IsEdepositedTotalEntry.  At the end of an event all the relevant tracks' deposited energies is summed into E\_deposited variable, and a dedicated entry is made in the tree with this information.  By filtering IsEdepositedTotalEntry==1, all the deposition energy entries can be selected.  This would be useful for studying the detector response function.  These entries have the additional feature of including a concatenation of all the processes which contributed to the deposited energy.  For example, for EventID=0 the energy deposition was achieved via the main track (EventGenerator), a compton scatter and a photoelectric effect (see the last line above).

The variables in the tree/table are as following:
 * E\_beam -- the energy of the particle produced by the event generator
 * E\_incident    -- only for IsSurfaceHitTrack==1 entries this is the energy of the particle at the detector entrance.  Good way to study the flux of the particles along a surface.
 * E\_deposited   -- the deposited energy in the detector
 * x\_incident    -- for IsSurfaceHitTrack==1 or SaveTrackInfo==1 the hit position on the detector, in mm
 * y\_incident    --  same
 * z\_incident    --  same
 * theta          --  same (radians)
 * Time           --  the (flight) time from the inception of the event
 * EventID        -- this is the # of the event in the simulation history
 * TrackID        -- for a particular event, many tracks may be produced.  They will all have the same EventID and different TrackIDs
 * ParticleID     -- for a particular track, this is the ParticleID, based on LLNL Particle Data Group definitions.
 * ParticleName   -- the actual name (which is more useful than the ParticleID)
 * CreatorProcessName         -- the name of the process which created this track
 * IsEdepositedTotalEntry     -- the flag for total deposited energy entries
 * IsSurfaceHitTrack          -- the flag for surface hit entries
 * detector#       -- the number of the detector.  The code assumes that all detector volumes are named **det_phys#**, where **#** is the detector number.  The code trunkates the **det_phys** and thus extracts the detector number.

The CreatorProcessName for IsEdepositedTotalEntry==1 entries contains a concatenation of all the processes which contributed to the deposited energy.  This is a good way to study the various effecst which, for example, contribute to the photopeak and the Compton continuum in a gamma detector.

Finally, it is also possible to request a brief output, in the form of EventID, Energy, ParticleName, and CreatorProcessName.  To do this set the BriefOutputOn flag to 1, in the gdml input.

The output can be modified to be only limited for just one or two of these entry types.  The gdml file allows to do this using the SaveSurfaceHitTrack, SaveTrackInfo, SaveEdepositedTotalEntry variables.  For example, for a simulation where the flux is to be determined, only SaveSurfaceHitTrack needs to be set.  For studying the energy deposition distribution
for a particular type of detector the SaveEdepositedTotalEntry needs to be set.  The use of these variables can significantly simplify the analysis of the MC output.



General status
==
In its current form, the code has been tested with <12MeV photons, neutrons, gammas, and electrons.  Very general checks indicate that most processes are being simulated correctly.


To do
==
Below is a prioritized list of future tasks.

* Write the python/javascript front end to the gdml? <<===== need a UROP
* General code improvements

