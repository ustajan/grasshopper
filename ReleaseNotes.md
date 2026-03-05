#  v. 11.3.2 Release Notes

 *  Currently, the simulation produces separate entries for separate detector hits for a given track.  Additionally, if a track hits a detector multiple times, multiple entries will be generated.  This then may require (depending on the goals of the analysis) to combine these tracks during the post-processing, e.g. during the `SaveTrackInfo` mode. 
 *  In future releases this feature may be modified, e.g. combining multiple hits on a given detector by a single track. 