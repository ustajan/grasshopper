# grasshopper-validation
.gdml files for Grasshopper validation

The neutron-trans.gdml file simulates the output of one million neutrons in the form of a 5mm pencil beam. The energy spectrum is set by input_spectrum.txt which should consist of two columns, E & (dN/dE), and in the referenced paper (ADD CITATION) consists of integer E values from 1 to 20 with a column of ones for dN/dE (this column is normalized by grasshopper). The geometry setup consists of a 5 mm thick, 10 cm diameter target (either HEU or WGPu) and a 6-Li glass detector (for the simulations in the paper, a 1.0cm thick HEU target was used). When the SaveSurfaceHitTrack flag is set to 1, the detector response is not accounted for in the simulation. The world volume uses near vacuum (\textit{i.e.} \verb|G4_Galactic| material), in order to simplify comparison of the output to transmission calculations using $\exp{[-\sigma(E)\rho x N_A/A]}$, where $\sigma(E)$ is the energy dependent total interaction cross section of the neutrons in the target material, and rho is the density of the target.

The isotopic compositions of the highly enriched uranium (HEU) and weapons grade plutonium (WGPu) are defined in the .gdml file and presented below:
HEU (19.05 g/cm^3): 93.4% 235U, 5.6% 238U, and 1.0% 234U
WGPu (18.00 g/cm^3): 93.3% 239Pu, 6.0% 240Pu, 0.44% 241Pu, 0.015% 242Pu, 0.005% 238Pu, and 0.25% 16O
