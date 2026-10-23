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
#include "G4RunManagerFactory.hh"
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
#include "PhysicsList.hh"
#include "PrimaryGeneratorAction.hh"
#include "EventAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"
#include "StackingAction.hh"
#include "MySession.hh"
#include "G4UIsession.hh"

#include "Randomize.hh"

#include "vector"

#include <iostream>
#include <fstream>

#include "G4GDMLParser.hh"
#include "G4Version.hh"
#include <filesystem>
#include <string>

// Set by CMake from the top-level VERSION file and the install prefix.
#ifndef GRASSHOPPER_VERSION
#define GRASSHOPPER_VERSION "unknown"
#endif
#ifndef GRASSHOPPER_DATADIR
#define GRASSHOPPER_DATADIR "<prefix>/share/grasshopper"
#endif

G4bool drawEvent;
G4String RootOutputFile;

G4GDMLParser parser;

static void print_usage(std::ostream& os)
{
  os << "Usage: grasshopper <gdml_configuration_file> <output_name> [seed]\n"
        "       grasshopper --version | --help\n"
        "\n"
        "The GDML file defines everything: geometry, materials, beam, physics cuts\n"
        "and output options. See the examples for a starting point:\n"
        "  GitHub:    https://github.com/ustajan/grasshopper/tree/master/examples\n"
        "  Installed: " GRASSHOPPER_DATADIR "/examples\n"
        "\n"
        "Arguments:\n"
        "  <gdml_configuration_file>  GDML input (validated against schema/gdml.xsd,\n"
        "                             resolved relative to the GDML file)\n"
        "  <output_name>              Output base name; a trailing .root is stripped\n"
        "  [seed]                     Random seed; overrides RandomGenSeed in the GDML\n"
        "\n"
        "Output (in the current directory):\n"
        "  <output_name>.dat          tab-separated results, when TextOutputOn=1\n"
        "  <output_name>.root         ROOT TTree, only when built with ROOT support\n"
        "  g4_NN.wrl                  VRML geometry + tracks, when VRMLvisualizationOn=1\n"
        "\n"
        "Files read from the current directory on demand:\n"
        "  input_spectrum.txt         energy spectrum, used when BeamEnergy < 0\n"
        "  beam_width.txt             extended isotropic source width (BeamSize < -3)\n"
        "  vis.mac                    extra Geant4 visualization commands, if present\n"
        "\n"
        "Reference: A. Danagoulian et al., IEEE NSS/MIC 2021,\n"
        "           doi:10.1109/NSS/MIC44867.2021.9875720\n"
        "Homepage:  https://github.com/ustajan/grasshopper\n";
}

//#define G4VIS_USE //in principle this should be passed by the compiler, during cmake

#ifdef G4VIS_USE
#include "VisManager.hh"
#include "G4TrajectoryDrawByParticleID.hh"
#endif


//#include "AnalysisManager.hh"
#include "Analysis.hh"

G4String gOutName;

int main(int argc,char** argv)
{

  bool commandlineseed = false;
  G4int seed;
  
  clock_t t0,t1,t2;
  G4int start_time = time(NULL);
  t0=clock();
  if (argc >= 2) {
    const std::string arg1 = argv[1];
    if (arg1 == "--version" || arg1 == "-v") {
      std::cout << "grasshopper " << GRASSHOPPER_VERSION << " (" << G4Version << ")" << std::endl;
      return 0;
    }
    if (arg1 == "--help" || arg1 == "-h") {
      print_usage(std::cout);
      return 0;
    }
  }

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
    std::cerr << "Wrong input!\n\n";
    print_usage(std::cerr);
    return 2;
  }

  G4int run_evnt;
  std::string rootoutputfile = (std::string)RootOutputFile;
  if(rootoutputfile.find(".root")<rootoutputfile.length()){
	  gOutName=(std::string)rootoutputfile.substr(0, rootoutputfile.find(".root"));
	  
  }
	else gOutName=(std::string)RootOutputFile;
  
  if (!commandlineseed)
    seed = parser.GetConstant("RandomGenSeed");



  run_evnt = parser.GetConstant("EventsToRun");


  //Welcome message, along with reference and copyright
  std::cout << "\n  ==========================================\n"
               "  Welcome to grasshopper!\n"
               "  Copyright   : (c) 2015-2024 Areg Danagoulian\n"
               "  Reference   :  A. Danagoulian, J. N. Miske and E. A. Klein, Grasshopper, a Geant4 Front End: Validation and Benchmarking, 2021 IEEE Nuclear Science Symposium and Medical Imaging Conference (NSS/MIC), Piscataway, NJ, USA, 2021, pp. 1-7, \n"
               "  doi         :  10.1109/NSS/MIC44867.2021.9875720 \n"
               "  GitHub      :  https://github.com/ustajan/grasshopper  \n"
               "  ==========================================\n";

  // output configuration information
  std::cout<<"\nRandomGenSeed: "<<seed;
  std::cout<<"\nEventsToRun: "<<run_evnt;

  // choose the Random engine
  CLHEP::HepRandom::setTheEngine(new CLHEP::RanluxEngine);
  CLHEP::HepRandom::setTheSeed(seed);

  // Construct the default run manager
  G4RunManager* runManager = new G4RunManager; //goes crazy when being deleted
//  auto runManager =
//    G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);
  G4UImanager* UIS = G4UImanager::GetUIpointer();
  MySession* LoggedSession = new MySession;
  UIS->SetCoutDestination(LoggedSession);


  // exporting geometry from specified GDML file
  runManager->SetUserInitialization(new DetectorConstruction(parser.GetWorldVolume()));

  runManager->SetUserInitialization(new physicsList()); 

  
#ifdef G4VIS_USE
  std::cout << std::endl << " == Setting up visualization. ==" << std::endl;

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

  // initialize the analysis
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
  G4UImanager* UI = G4UImanager::GetUIpointer();
  if(parser.GetConstant("VRMLvisualizationOn")){
    bool opened_vrml = false;
#ifdef G4VIS_USE
    const std::vector<std::string> vrml_drivers = {"VRML2FILE", "VRML2"};
    for (const std::string& driver : vrml_drivers) {
      if (UI->ApplyCommand(("/vis/open " + driver).c_str()) == 0) {
        opened_vrml = true;
        std::cout << std::endl << " == Opened visualization driver " << driver << ". ==" << std::endl;
        break;
      }
    }
#endif
    if (opened_vrml) {
      UI->ApplyCommand("/vis/drawVolume");
      UI->ApplyCommand("/tracking/storeTrajectory 1");
      UI->ApplyCommand("/vis/scene/add/trajectories");
      UI->ApplyCommand("/vis/scene/endOfEventAction accumulate");
      UI->ApplyCommand("/vis/viewer/flush");
      std::string command="/run/beamOn "+std::to_string((int)parser.GetConstant("EventsToAccumulate"));
      UI->ApplyCommand(command.c_str());
      UI->ApplyCommand("/vis/close");
      UI->ApplyCommand("/vis/disable");
      std::cout << std::endl << " == Produced a visualization wrl file. ==" << std::endl;
    } else {
      std::cout << std::endl << " == Unable to open a VRML visualization driver. No wrl file was produced. ==" << std::endl;
    }
  }
  if (std::filesystem::exists("vis.mac"))
  {
    UI->ApplyCommand("/control/execute vis.mac");
    std::cout << std::endl << " == Found and executed vis.mac == " << std::endl;
  }
  else  {
    std::cout << std::endl << " == No vis.mac file found. ==" << std::endl;
  }
//  UI->ApplyCommand("/process/had/particle_hp/use_NRESP71_model true");
/*  std::string command="/run/beamOn "+std::to_string((int)parser.GetConstant("EventsToAccumulate"));
  UI->ApplyCommand(command.c_str());
  UI->ApplyCommand("exit");
*/

  runManager->BeamOn(run_evnt); //now do the big run

  //DONE
  //Now do a cleanup, print CPU/time diagnostics, and exit

  if (analysis == AnalysisManager::GetAnalysisManager()){
    std::cout << "\nDeleting the analysis object.\n";
  	delete analysis; //causes errors
  }

  // job termination
	

#ifdef G4VIS_USE
//  delete visManager; //deleting it causes a huge "non-critical" error
  std::cout << "Deleting the visManager object.\n";
#endif


//  delete runManager; //deleting it causes a huge "non-critical" error
//  delete LoggedSession;

  G4int stop_time = time(NULL);
  t2=clock();

  std::cout << " The initialization took:\t" << beam_on_start_time - start_time <<"s"<< std::endl;
  std::cout << " The MC took:\t\t" << stop_time - beam_on_start_time <<"s"<< std::endl;

  std::cout << " The initialization took:\t" 	<< (float)(t1-t0)/CLOCKS_PER_SEC <<" CPU seconds"<< std::endl;
  std::cout << " The MC took:\t\t" 			<< (float)(t2-t1)/CLOCKS_PER_SEC <<" CPU seconds"<< std::endl;

  std::cout << " Run completed!"<< std::endl;

  return 0;
}


