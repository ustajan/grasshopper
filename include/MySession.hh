#ifndef MySession_h
#define MySession_h 1

#include "G4UIsession.hh"
//#include "G4ios.hh"
#include <fstream>


class MySession : public G4UIsession
{
public:
MySession();
~MySession();

public:
G4int ReceiveG4cout(const G4String& coutString); // the const and & were key here
G4int ReceiveG4cerr(const G4String& cerrString);

private:
std::ofstream logFile;
std::ofstream errFile;

};


#endif
