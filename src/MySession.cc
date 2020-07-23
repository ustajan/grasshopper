#include "MySession.hh"
#include "G4UImanager.hh"
//#include <iostream>
#include "G4ios.hh"
#include <fstream>

extern G4String gOutName;

MySession::MySession() : G4UIsession()
{
        logFile.open(gOutName);
        errFile.open("Error.log");
}

MySession::~MySession()
{
        logFile.close();
        errFile.close();

}

G4int MySession::ReceiveG4cerr(const G4String& cerrString)
{

        errFile << cerrString << std::flush;
        return 0;
}
G4int MySession::ReceiveG4cout(const G4String& coutString)
{
        logFile << coutString << std::flush;
        return 0;
}
