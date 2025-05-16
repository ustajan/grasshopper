#!/bin/bash
filepattern=$1 #this needs to be a pattern with wildcards etc.  on the command line it goes into "" quotes
fileout=$2 #the final file



if [[ $filepattern == *".root"* ]] #check whether this is a .root file we are stitching
then
    echo "Stitching root files";
    
    filelist="";
    counter=0;
    for file in `ls ${filepattern}`; 
    do
	filelist="${filelist} $file";
	((counter++));
    done
    
    echo $filelist;
    eval "hadd -f ${fileout} ${filelist}";
    echo "Added " $counter " files";

elif [[ $filepattern == *".dat"* ]] #ascii .dat files?
then
    echo "Stitching dat files!";
    sleep 1;
    counter=0;
    for file in `ls ${filepattern}`;
    do
	 sed '1,1d' $file >> $fileout;
	 ((counter++));
    done
    echo "Added " $counter " .dat files into " $fileout;
else
    echo "Hmm, the files you want to stitch are neither root, nor dat. Please specify the correct file pattern.  Btw, here's the usage:"
    echo "stitch.sh <\"filepattern\"> <fileout>";
fi