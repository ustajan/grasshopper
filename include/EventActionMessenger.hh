// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//
// Potassium-doped Scintillator Simulation
//
// Alexei Klimenko 2004
//
// v. 0.01 08/23/2004
//
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////


// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//
// DESCRIPTION
// -----------
//
// The SSAEventActionMessenger is instatiated by the SSARunManager and introduces 
// into the UI event menu additional command to control the drawing of event
// trajectory. User can choose one from
//       1) none: no particle trajectory will be drawn.
//       2) charged: only for charged particles.
//       3) all: for all particles
// The default option is for all particles.  
//        A
// The SSAEventActionMessenger modifies the state of the event Drawing flag 
// according to UI menu command issued by the user.
//
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//
// PUBLIC MEMBER FUNCTIONS
// -----------------------
//
// SSAEventActionMessenger (SSAEventAction*)
//    Constructor:  Defines the commands available to change the DrawFlag
//    status. 
//
// ~SSAEventActionMessenger ()
//    Destructor deletes G4UIdirectory and G4UIcommand objects.
//
// void SetNewValue (G4UIcommand *command, G4String newValues)
//    Identifies the command which has been invoked by the user, extracts the
//    parameters associated with that command (held in newValues, and uses
//    these values with the appropriate member function.
//
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//

#ifndef EventActionMessenger_h
#define EventActionMessenger_h 1

#include "globals.hh"
#include "G4UImessenger.hh"
#include "G4ApplicationState.hh"

class EventAction;
class G4UIcmdWithAString;

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

class EventActionMessenger: public G4UImessenger
{
  public:
    EventActionMessenger(EventAction*);
   ~EventActionMessenger();
    
    void SetNewValue(G4UIcommand*, G4String);
    
  private:
    EventAction*   eventAction;   
    G4UIcmdWithAString* DrawCmd;
};

#endif






