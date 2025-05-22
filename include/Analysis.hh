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

#ifndef Analysis_h
#define Analysis_h 1

#include "AnalysisManager.hh"
#include "G4ThreeVector.hh"

class G4VPhysicalVolume;
class G4Event;
class G4Run;
class G4Track;
class G4Step;

#include "G4ClassificationOfNewTrack.hh"
#include "G4TrackStatus.hh"
#include "G4Types.hh"
#include "G4ParticleGun.hh"


#include <iostream>
#include <fstream>
#include <vector>

#if defined (G4ANALYSIS_USE_ROOT)

#include "TROOT.h"
#include "TApplication.h"
#include "TSystem.h"
#include "TH1.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TMath.h"
#include "TString.h"
#include "TRandom.h"
#endif

#include <time.h>

#if defined (G4UI_USE_ROOT) || defined (G4UI_BUILD_ROOT_SESSION)
#if !defined (G4ANALYSIS_USE_ROOT)
#define G4ANALYSIS_USE_ROOT 1
#endif /* !defined (G4ANALYSIS_USE_ROOT) */
#endif /* defined (G4UI_USE_ROOT) || defined (G4UI_BUILD_ROOT_SESSION) */

#if defined (G4ANALYSIS_USE_ROOT)

class TH1D;
class TFile;
class TTree;
class TBranch;


#endif /* defined (G4ANALYSIS_USE_ROOT) */

class Analysis : public AnalysisManager {
  
public:
  Analysis(G4ParticleGun*);
  ~Analysis();
  
public:
  // G4VUserDetectorConstruction
  void Construct(const G4VPhysicalVolume*);
  
  // G4VUserPhysicsList
  void ConstructParticle();
  void ConstructProcess();
  void SetCuts();
  
  // G4VUserPrimaryGeneratorAction
  void GeneratePrimaries(const G4Event*);
  
  // G4UserRunAction
//  void BeginOfRunAction(const G4Run*);
//  void EndOfRunAction(const G4Run*);
  
  // G4UserEventAction
  void BeginOfEventAction(const G4Event*);
  void EndOfEventAction(const G4Event*);
  
  // G4UserStackingAction
  void ClassifyNewTrack(const G4Track*, G4ClassificationOfNewTrack*);
  void NewStage();
  void PrepareNewEvent();
  
  // G4UserTrackingAction
  void PreUserTrackingAction(const G4Track*);
  void PostUserTrackingAction(const G4Track*, G4TrackStatus*);
  
  // G4UserSteppingAction
  void UserSteppingAction(const G4Step*);
  
  void CreateNewEntry(long unsigned int trackid);
  bool IsThisANewTrack(long unsigned int trackid);
  bool IsThisANewTrackInThisDetector(G4Step *aStep);

  bool EnteringDetector(const G4Step *aStep);
  bool IsInDetector(const G4Step *aStep);
  int GetDetectorNumber(const G4Step *aStep);

private:
  void ResetEverything();

  // once a while do "something"
  void OnceAWhileDoIt(const G4bool DoItNow = false);
  bool TrackMustDie(const G4Step*);

  time_t LastDoItTime; // used in OnceAWhileDoIt method

//  TH1D *hStepLength; // Step Length
//  TH1D *hStepTotELoss; // Step Total Energy Loss
//  TH1D *hTotELossNorm; // Total Energy Loss per Step Length Unit

#if defined (G4ANALYSIS_USE_ROOT)
  TFile *f; // output file
  TTree *tree;
#endif
  std::ofstream data_file;
  bool textoutput,briefoutput;

  unsigned long entry;
  G4ParticleGun* particle_gun_local;
  G4double E,Edep,E_beam;
  G4double x;
  G4double y;
  G4double z;
  G4double theta;
  G4float Time;
  long long ID;
  long long TrackID;
  long long EventID;
  long long ProcID;
  std::vector<double> Ev,Edepv,xv,yv,zv,thetav;
  std::vector<long long> IDv,TrackIDv,EventIDv,ProcIDv;
  std::vector<std::string> ParticleNamev,ProcessNamev;
  std::vector<std::string> EntryID;
  std::vector<bool> IsSurfaceHit,IsNewTrack;
  std::string ParticleName,CreatorProcessName;
  std::vector<float> Timev;
  std::vector<long long> detector_hit;
  bool IsSummaryEntry,IsSurfaceHitTrack;
  unsigned long LightProducingParticle, EventGeneratorParticle;
  unsigned long channel;
  float LowEnergyCutoff;
  bool KeepOnlyMainParticle;

  bool SaveSurfaceHitTrack;
  bool SaveTrackInfo;
  bool SaveEdepositedTotalEntry;


  G4ThreeVector p;
  G4ThreeVector X;

  G4int counter;


  G4int file_even;
  G4int nextinline;


};

#endif

