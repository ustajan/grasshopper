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
//
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Areg Danagoulian, 2015
// MIT, NSE
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////


//#include <rw/tvordvec.h>
#include "G4ios.hh"
#include "EventActionMessenger.hh"
#include "EventAction.hh"
#include "G4Event.hh"
#include "G4EventManager.hh"
#include "G4HCofThisEvent.hh"
#include "G4TrajectoryContainer.hh"
#include "G4Trajectory.hh"
#include "G4VVisManager.hh"
#include "G4UImanager.hh"
#include "G4UnitsTable.hh"

#include "AnalysisManager.hh"
 

extern G4bool drawEvent;

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

EventAction::EventAction()
  : drawFlag("all"),eventMessenger(NULL)
{
  eventMessenger = new EventActionMessenger(this);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

EventAction::~EventAction()
{
  delete eventMessenger;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void EventAction::BeginOfEventAction(const G4Event* Ev)
{
  drawEvent=false;
  
  // Analysis
  if (gAnalysisManager) gAnalysisManager->BeginOfEventAction(Ev);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void EventAction::EndOfEventAction(const G4Event* Ev)
{
  
  if (drawEvent){
    const G4Event* evt = fpEventManager->GetConstCurrentEvent();

    
    G4TrajectoryContainer * trajectoryContainer = evt->GetTrajectoryContainer();
    G4int n_trajectories = 0;
    if(trajectoryContainer){ 
      n_trajectories = trajectoryContainer->entries(); 
    }
      
    if(G4VVisManager::GetConcreteInstance()){
      for(G4int i=0; i<n_trajectories; i++) {
	G4Trajectory* trj = (G4Trajectory*)(*(evt->GetTrajectoryContainer()))[i];
	if (drawFlag == "all") trj->DrawTrajectory(); //used to be 50
	else if ((drawFlag == "charged")&&(trj->GetCharge() != 0.))
	  trj->DrawTrajectory(); //used to be 50 
	//	trj->ShowTrajectory(); 
      }
    }
    
  }
  

  // Analysis
  if (gAnalysisManager) gAnalysisManager->EndOfEventAction(Ev);


}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

































