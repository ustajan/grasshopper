# Grasshopper

This application is based on the Geant4 development toolkit, which allows to program complex particle
tracking (e.g. gamma, electrons, protons, etc) and particle-matter interaction, Monte Carlo (MC) simulations.
Grasshopper is a simple Geant4 application, where all the geometries and even generators parameters are 
defined in a Geometry Description Markup Language (GDML) file, with the purpose of setting up quick and 
simple simulations.  The goal is to allow users with no C++ and Geant4 knowledge quickly set up and run simulations.

Author:  		Areg Danagoulian

Creation time:  11/2015  
Last update:    Continuous Development since 11/2015

For copyright and licensing see files COPYRIGHT and LICENSE.

## External Documentation
A ReadTheDocs resources on Grasshopper is available at: https://grasshopper.readthedocs.io/en/latest/.

This website seeks to be an exhaustive resource on using Grasshopper. Please reach out if you have 
improvements in mind.


## Installation

The user is required to have the following on their machine

	* xerces.  This will allow the GDML parser capability.
	* Built and installed geant4 libraries.  Also, in the cmake stage, the following flag needs to be passed:
	`-DGEANT4_USE_GDML=ON`.  In some cases you also have to also add the location for Xerces with flags such as 	
        `-DXERCESC_INCLUDE_DIR=/usr/local/include/ -DXERCESC_LIBRARY=/usr/local/lib/libxerces-c.so`.  See the geant4 instructions on how 	to add Xerces for more detail on the paths.
	* ROOT -- optional.  Has been tested with version 6.16.  If you do not have ROOT the make process will recognize that and exclude 		it from the build.
	* When building grasshopper, the compiler might not find the GDML header files.  In that case just determine the actual file directories, and add them to the include list by appending `-I/directory_to_headers` to the `CPPFLAGS` env variable.

__Important note__:  These days Geant4 primarily works via the cmake framework.  However Grasshopper uses the older Makefile framework.  It is important that you source the appropriate shell script in Geant4 directories to enable all the env. Variables that are necessary for Makefile to work correctly.  In my particular case I have the following line in my .bashrc file, please modify this accordingly for your build/configuration:

`. /usr/local/geant4/geant4.10.05-install/share/Geant4-10.5.0/geant4make/geant4make.sh`

If all the regular Geant4 installations and configurations are ready, then the user can get the code by

`> git clone git@github.com:ustajan/grasshopper.git`

## Building Grasshopper

```
$ cd grasshopper/
$ make -j4
```

## Running Grasshopper

```
$ grasshopper input.gdml output.root
```

Tutorial
==
The best way to learn how to use grasshopper is by using the tutorial on the project wiki, 
[here](https://github.com/ustajan/grasshopper/wiki).  

You can also get there by going to Wiki link above.

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
 * output.dat  -- depending on the settings in the gdml file, it can also generate a simple ASCII file, output.dat,  which can then be read into python/matlab/etc.
 * g4_00.wrl.  This is the VRML visualization file.  The settings for this file's content are defined in the gdml file.
   The wrl file can be loaded in paraview (http://www.paraview.org/download/), thus allowing for a rendering of the
   geometries and some particle tracks.

The root output structure (which is identical to the ASCII output) can be somewhat complex. The output of the simulation can be
thought of as a table -- where every line is an entry corresponding to a **particular set of information**
within an event. To visualize the structure of the root output, below is the (reduced) set of entries in the ASCII output from a simulation of a 0.5MeV photon hitting a 2" NaI detector:


  E\_incident(MeV)   E\_deposited(MeV) ...    z_incident   EventID    TrackID   ParticleID   ParticleName  CreatorProcessName   IsEdepositedTotalEntry    IsSurfaceHitTrack
  
  0.15937          0.033281        28.87   0       1       22      gamma   EventGenerator          0       1

-1e+06   0.15888         -1e+06          0       2       11      e-      compt   0       0

-1e+06   0.22764         -1e+06          0       3       11      e-      compt   0       0

-1e+06   0.12621         -1e+06          0       4       11      e-      phot    0       0

-1       0.546   -1      0       -1      -1      -1      EventGenerator/compt/compt/phot/        1       0

0.30516          0.037719        31.902          1       1       22      gamma   EventGenerator          0       1

-1e+06   0.23628         -1e+06          1       2       11      e-      compt   0       0

-1e+06   0.272   -1e+06          1       3       11      e-      phot    0       0

-1       0.546   -1      1       -1      -1      -1      EventGenerator/compt/phot/      1       0

There are three type of entries:
 * IsSurfaceHitTrack.  These entries are registered when a track enters the detector volume.  To filter out these events, simply search for all entries where IsSurfaceHitTrack==1
 * regular tracks.  At the end of an event all the tracks inside the detector can be recorded in the form of individual entries.  All entries for which IsSurfaceHitTrack!=1 && IsEdepositedTotalEntry!=1 are regular track entries.  These entries are useful for debugging and diagnostic purposes, as well as for general studies of the interaction physics of the detector.
 * IsEdepositedTotalEntry.  At the end of an event all the relevant tracks' deposited energies is summed into E\_deposited variable, and a dedicated entry is made in the tree with this information.  By filtering IsEdepositedTotalEntry==1, all the deposition energy entries can be selected.  This would be useful for studying the detector response function.  These entries have the additional feature of including a concatenation of all the processes which contributed to the deposited energy.  For example, for EventID=0 the energy deposition was achieved via the main track (EventGenerator), a compton scatter and a photoelectric effect (see the last line above).

The variables in the tree/table are as following:
 * E\_incident    -- only for IsSurfaceHitTrack==1 entries this is the energy of the particle at the detector entrance.  Good way to study the flux of the particles along a surface.
 * E\_deposited   -- the deposited energy in the detector
 * x\_incident    -- for IsSurfaceHitTrack==1 the hit position on the detector
 * y\_incident    --  same
 * z\_incident    --  same
 * theta          --  same
 * EventID        -- this is the # of the event in the simulation history
 * TrackID        -- for a particular event, many tracks may be produced.  They will all have the same EventID and different TrackIDs
 * ParticleID     -- for a particular track, this is the ParticleID, based on LLNL Particle Data Group definitions.
 * ParticleName   -- the actual name (which is more useful than the ParticleID)
 * CreatorProcessName         -- the name of the process which created this track
 * IsEdepositedTotalEntry     -- the flag for total deposited energy entries
 * IsSurfaceHitTrack          -- the flag for surface hit entries

The CreatorProcessName for IsEdepositedTotalEntry==1 entries contains a concatenation of all the processes which contributed to the deposited energy.  This is a good way to study the various effecst which, for example, contribute to the photopeak and the Compton continuum in a gamma detector.

Finally, it is also possible to request a brief output, in the form of EventID, Energy, ParticleName, and CreatorProcessName.  To do this set the BriefOutputOn flag to 1, in the gdml input.

The output can be modified to be only limited for just one or two of these entry types.  The gdml file allows to do this using the SaveSurfaceHitTrack, SaveTrackInfo, SaveEdepositedTotalEntry variables.  For example, for a simulation where the flux is to be determined, only SaveSurfaceHitTrack needs to be set.  For studying the energy deposition distribution
for a particular type of detector the SaveEdepositedTotalEntry needs to be set.  The use of these variables can significantly simplify the analysis of the MC output.



General status
==
In its current form, the code has been tested with <12MeV photons, neutrons, gammas, and electrons.  Very
general checks indicate that most processes are being simulated correctly.


A few known problems:
==
 * When running with neutrons >16MeV the code will hang.
 * The code is optimized to run in two configurations
   *  SurfaceHit analysis - providing energy/position/momentum information on the flux of particles through a "detector" surface.  It will generate multiple entries for multiple tracks crossing a surface for a single MC event.  However, if one of the tracks then backscatters and crosses the surface again it will be ignored.
   *  EnergyDeposited analysis - providing deposited energy for every event.  Here the code is less sharp - if multiple tracks enter the detector, it will combine their deposited energies.  As long as you specify which particle type's energy deposition is of interest (e.g. electrons for photons, or protons for neutrons) this is sufficiently accurate as most detectors will not be able to time-resolve the multiple hits from tracks that originate from a single track.  This, however can fail for a) very fast detectors or b) when you have a process which produces a low energy electron and a photon.  If you have to deal with complex processes like (b) then grasshopper is probably not the best thing to use (least you want to modify the code or see if various cuts on particle type allow you to isolate individual responses).
 * More importantly, the above circumstance results in some (mostly minor) issues where the user tries to determine the energy deposition for a whole range of energies of incident particle.  If the incident particle creaters an electromagnetic or hadronic shower, then an E_incident vs. E_deposited comparison may yield strange results, as E_deposited>E_incident in some cases - this is due to the fact that E_deposited may have captured deposited energy from multiple tracks, while E_incident is the energy of an individual track. 

To Do List
==
Below is a prioritized list of future tasks.

Output
- [x] Implement "simple" ASCII text output, along with ROOT 
- [x] Make the code be able to reliably switch between ROOT (when ROOT is available) and ASCII output
Front End
- [ ] Write the python front end to generate the GDML
- [ ] Check the physics, by comparing to data and validated geant4 simulations
(this is the main point of the thesis project by J. Miske)
Visualization
- [x] Automatic wrl generation (even in batch mode), limited to 300 tracks
Other
- [x] Implement the keeper list, which should allow to dramatically speed up the simulations
- [ ] Replace the char arrays in TTree with actual strings

 
Requirements for the Python front-end
==
The Python front end will read in a simple ASCII text file with "human readable" descriptions, parse it,
populate a GDML file based on some template, and run the Geant4 simulation.  The ASCII input file needs
to have the following fields and sections

	* Particle Event Generator parameters
	  + Particle type definition.  Ideally, this should include ions.  A list should be provided in a separate .md document
	  + Particle energy
	  + Directionality.  For simplicity, limit it to:  parallel;  isotropic.
	  + Beam source x,y,z
	  + Beam width
	* Geometries
	  + Number of geometries -- N (default:1).  No daughter geometries.
		If people want to do that, they can modify the gdml directly.
	  + Materials: *only* limited to NIST materials, provided by a (long) list.
		If people want custom materials, they can modify the gdml directly.
	  + Geometry1:
		- Sensitive?  If yes, its energy deposition will be measured and added to the output.
		  An additional branch needs to be added, which will list the detector name.
		- volume -- shape
		- logical -- add material.
		- physical placement in the world.  If this is a sensitive volume, then the name needs to
		  end with _number.  This number will go into the tree branch.
	  + Geometry2, etc...
	* Keeper list and cuts
	  + This list should contain the following:  particle type; energy threshold E_th; volume volname
	  + Now, for every particle type, only tracks with E>E_th *inside* volname will be tracked
	  + Everything else will be killed
	  + Example of how this will look:
	  	- neutron:  0.1 MeV,  everywhere
	  	- gamma  :  0.1 MeV,  everywhere
	  	- e-     :  0.1 MeV,  detector_volume
	  	- proton :  1.0 MeV,  detector_volume
	  + The code will generate a vector, and for every step will loop over the vector, checking if these
	    conditions are met.  If not, it will kill the track.
		


