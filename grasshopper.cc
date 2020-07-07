// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Areg Danagoulian, 2015
// MIT, NSE
// Input:
//    gdml file
//    the root output file.  If text output requested in gdml input, a .dat ASCII file will be produced instead
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////
//
// ********************************************************************
// * DISCLAIMER                                                       *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.                                                             *
// *                                                                  *
// * By copying,  distributing  or modifying the Program (or any work *
// * based  on  the Program)  you indicate  your  acceptance of  this *
// * statement, and all its terms.                                    *
// ********************************************************************
//



#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4UIterminal.hh"
#include "G4UItcsh.hh"
#include "G4ios.hh"
#include "time.h"

#ifdef G4UI_USE_GAG
#include "G4UIGAG.hh"
#endif

#ifdef G4UI_USE_XM
#include "G4UIXm.hh"
#endif

#ifdef G4UI_USE_TCSH
#include "G4UItcsh.hh"
#endif

#include "DetectorConstruction.hh"
//#include "PhysicsList.hh"
#include "DADEphysicsList.hh"
#include "PrimaryGeneratorAction.hh"
#include "EventAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"
#include "StackingAction.hh"

#include "Randomize.hh"

#include "vector"

#include <iostream>
#include <fstream>

#include "G4GDMLParser.hh"

G4bool drawEvent;
G4String RootOutputFile;

G4GDMLParser parser;

#ifdef G4VIS_USE
#include "VisManager.hh"
#include "G4TrajectoryDrawByParticleID.hh"
#endif


//#include "AnalysisManager.hh"
#include "Analysis.hh"

int main(int argc,char** argv)
{

  bool commandlineseed = false;
  G4int seed;

  clock_t t0,t1,t2;
  G4int start_time = time(NULL);
  t0=clock();
  // check that the number of input parameters is consistent with expected
  if(argc==3 || argc==4){  // output configurations information:  either no seed (read from gdml) or set seed explicitly
    parser.Read(argv[1]);
    RootOutputFile = argv[2];
    if (argc==4)
      {
	seed = atoi(argv[3]);
	commandlineseed = true;
      }
  }
  else{
    std::cout<<"Wrong input! Usage:\n grasshopper <gdml_configuration_file> <root_output_filename> [seed] \n\n";
    return -1;
  }

  G4int run_evnt;

  if (!commandlineseed)
    seed = parser.GetConstant("RandomGenSeed");



  run_evnt = parser.GetConstant("EventsToRun");

  // output configuration information
  std::cout<<"\nRandomGenSeed: "<<seed;
  std::cout<<"\nEventsToRun: "<<run_evnt;

  // choose the Random engine
  CLHEP::HepRandom::setTheEngine(new CLHEP::RanluxEngine);
  CLHEP::HepRandom::setTheSeed(seed);

  // Construct the default run manager
  G4RunManager* runManager = new G4RunManager;


  // exporting geometry from specified GDML file
  runManager->SetUserInitialization(new DetectorConstruction(parser.GetWorldVolume()));

  runManager->SetUserInitialization(new physicsList(true,false)); //<- DADE's version, not very different from DMX (used to be (false,false))





  
#ifdef G4VIS_USE
  // visualization manager
  G4VisManager* visManager = new VisManager;
  visManager->Initialize();

  G4TrajectoryDrawByParticleID* model = new G4TrajectoryDrawByParticleID;

  model->SetDefault("cyan");
  model->Set("neutron","green");
  model->Set("gamma", "red");
  model->Set("e+", "magenta");
  model->Set("e-", "blue");

  visManager->RegisterModel(model);
  visManager->SelectTrajectoryModel(model->Name());
#endif
  

  // set mandatory user action class
  PrimaryGeneratorAction *primary_action=new PrimaryGeneratorAction();
  runManager->SetUserAction(primary_action);

  // start filling ntuple
  Analysis *analysis = new Analysis(primary_action->GetParticleGun());


  runManager->SetUserAction(new RunAction);
  runManager->SetUserAction(new EventAction);
  runManager->SetUserAction(new SteppingAction);
  runManager->SetUserAction(new StackingAction);


  // Initialize G4 kernel
  runManager->Initialize();


  // run timer
  G4int beam_on_start_time = time(NULL);
  t1=clock();

  //get the UImanager going, run a few events, produce a VRML file, and then delete everything.
  if(parser.GetConstant("VRMLvisualizationOn")){
    G4UImanager* UI = G4UImanager::GetUIpointer();
    UI->ApplyCommand("/vis/scene/create");
    UI->ApplyCommand("/vis/open VRML2FILE");
    UI->ApplyCommand("/vis/viewer/flush");
    UI->ApplyCommand("/tracking/storeTrajectory 1");
    UI->ApplyCommand("/vis/scene/add/trajectories");
    UI->ApplyCommand("/vis/scene/endOfEventAction accumulate");
    std::string command="/run/beamOn "+std::to_string((int)parser.GetConstant("EventsToAccumulate"));
    UI->ApplyCommand(command.c_str());
    UI->ApplyCommand("/vis/disable");
    UI->ApplyCommand("exit");
  }
  runManager->BeamOn(run_evnt); //now do the big run

  //DONE
  //Now do a cleanup, print CPU/time diagnostics, and exit

  if (analysis == AnalysisManager::GetAnalysisManager())
  	delete analysis;

  // job termination
	
#ifdef G4VIS_USE
  delete visManager;
#endif
	

  delete runManager;

  G4int stop_time = time(NULL);
  t2=clock();

  std::cout << " The initialization took:\t" << beam_on_start_time - start_time <<"s"<< std::endl;
  std::cout<<" The MC took:\t\t" << stop_time - beam_on_start_time <<"s"<< std::endl;

  std::cout << " The initialization took:\t" 	<< (float)(t1-t0)/CLOCKS_PER_SEC <<" CPU seconds"<< std::endl;
  std::cout <<" The MC took:\t\t" 			<< (float)(t2-t1)/CLOCKS_PER_SEC <<" CPU seconds"<< std::endl;

  G4cout << " Run completed!"<< G4endl;

  return 0;
}





