#!/bin/zsh

# Thi is a script that runs three simulations and analyzes their outputs as part of a unit test.
# We recommend that the users, after every modification of grasshopper, run this script and compare the outputs for before and after the modification.
# Assuming just procedural (non-physics) modifications the outputs should stay exactly the same.
# After running all the simulations the script prints the following:
# a) md5 sums for the outputs, as well as the md5 sums for PREVIOUS (pre-modification) outputs.  Assuming only minor changes these should match.
# b) output analysis results, as well as the results for the PREVIOUS oututs.  Again, assuming only minor procedural changes the outputs should not change.

# reset DY_LYBRARY_PATH
#.  ~/root-build/bin/thisroot.sh 
. ~/root/root_install/bin/thisroot.sh

# first run the beta simulation
grasshopper beta_lite.gdml beta_test.root 0
echo -n "beta " >> md5out.txt;
md5 beta_test.dat >> md5out.txt
awk '{if(NR>1) {n+=$2;m++;}} END {print "Average beta energy, counts:\t", n/m,m;}' beta_test.dat >> awkout.txt


# next run gamma
grasshopper gamma.gdml gamma_test.root
echo -n "gamma " >> md5out.txt;
md5 gamma_test.dat >> md5out.txt
awk '{if(NR>1 && $2>4) m++;} END {print "Average gamma full energy peak counts:\t", m;}' gamma_test.dat >> awkout.txt

# next run neutrons into 3He, and count the proton tracks
grasshopper test3He.gdml 3He.root
echo -n "proton " >> md5out.txt 
md5 3He.dat >> md5out.txt
awk '{if(NR>1 && $4=="triton") {n+=$2;m++;}} END {print "Average proton energy, counts:\t", n/m,m;}' 3He.dat >> awkout.txt

echo ""
echo "***********************"
echo "RESULTS:"
tail -6 md5out.txt | head -3
echo "*****"
tail -3 md5out.txt
echo "====="
tail -6 awkout.txt | head -3
echo "*****"
tail -3 awkout.txt

# next run gamma
