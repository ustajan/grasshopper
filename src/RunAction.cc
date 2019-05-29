// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//
// Potassium-doped Scintillator Simulation
//
// Alexei Klimenko  2004
//
// v. 0.01 08/23/2004
//
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////

#include "RunAction.hh"

#include "G4Run.hh"
#include "G4UImanager.hh"
#include "G4VVisManager.hh"
#include "G4ios.hh"

#include "fstream"
#include "iomanip"
#include "vector"

//using namespace std;

extern G4String filename;
 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

RunAction::RunAction()
{
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

RunAction::~RunAction()
{}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void RunAction::BeginOfRunAction(const G4Run* aRun)
{
 
  G4int RunN = aRun->GetRunID();
  if ( RunN % 1000 == 0 ) 
    G4cout << "### Run : " << RunN << G4endl;

  if (G4VVisManager::GetConcreteInstance())
    {
      G4UImanager* UI = G4UImanager::GetUIpointer(); 
      UI->ApplyCommand("/vis/clear/view");
      UI->ApplyCommand("/vis/draw/current");
    } 

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void RunAction::EndOfRunAction(const G4Run* )
{
  
  //  if (G4VVisManager::GetConcreteInstance())
  //  G4UImanager::GetUIpointer()->ApplyCommand("/vis/show/view");

  /*
  std::ofstream outscat(filename, std::ios::app);

  for (G4int i=0; i<Particles.size();i++) {
    outscat 
      << std::setiosflags(std::ios::fixed)
      << std::setprecision(3)
      << std::setiosflags(std::ios::right)
      << std::setw(12)
      << Energies[i]
      << std::setw(12)<<std::setprecision(4) 
      << std::setiosflags(std::ios::scientific)
      << std::setiosflags(std::ios::right)
      << Weights[i]
      << std::setw(12)<<std::setprecision(4)
      << std::setiosflags(std::ios::scientific)
      << std::setiosflags(std::ios::right)
      << Times[i] << "     "
      << Particles[i]
      << G4endl ;    
  }
  outscat << G4endl;
  outscat.close();
  */
}
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....












