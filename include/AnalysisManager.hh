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

#ifndef AnalysisManager_h
#define AnalysisManager_h 1

class G4VPhysicalVolume;
class G4Event;
class G4Run;
class G4Track;
class G4Step;

#include "G4ClassificationOfNewTrack.hh"
#include "G4TrackStatus.hh"

class AnalysisManager;
extern AnalysisManager *gAnalysisManager; // global AnalysisManager

class AnalysisManager {
  
public:
  AnalysisManager() {
    if (gAnalysisManager)
      delete gAnalysisManager;
    gAnalysisManager = this;
  }
  
  virtual ~AnalysisManager() {
    if (gAnalysisManager == this)
      gAnalysisManager = (AnalysisManager *)0;
  }
  
  static AnalysisManager *GetAnalysisManager() {
    return gAnalysisManager;
  }
  
public:
  // G4VUserDetectorConstruction
  virtual void Construct(const G4VPhysicalVolume *theWorldWolume) {;}
  
  // G4VUserPhysicsList
  virtual void ConstructParticle() {;}
  virtual void ConstructProcess() {;}
  virtual void SetCuts() {;}
  
  // G4VUserPrimaryGeneratorAction
  virtual void GeneratePrimaries(const G4Event *anEvent) {;}
  
  // G4UserRunAction
  virtual void BeginOfRunAction(const G4Run *aRun) {;}
  virtual void EndOfRunAction(const G4Run *aRun) {;}
  
  // G4UserEventAction
  virtual void BeginOfEventAction(const G4Event *anEvent) {;}
  virtual void EndOfEventAction(const G4Event *anEvent) {;}
  
  // G4UserStackingAction
  virtual void ClassifyNewTrack(
		   const G4Track *aTrack,
		   G4ClassificationOfNewTrack *classification) {;}
  virtual void NewStage() {;}
  virtual void PrepareNewEvent() {;}
  
  // G4UserTrackingAction
  virtual void PreUserTrackingAction(const G4Track *aTrack) {;}
  virtual void PostUserTrackingAction(const G4Track *aTrack,
				      G4TrackStatus *status) {;}
  
  // G4UserSteppingAction
  virtual void UserSteppingAction(const G4Step *aStep) {;}
  
};

#endif
