// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Areg Danagoulian, 2015
// MIT, NSE
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////


#ifndef PrimaryGeneratorAction_h
#define PrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"

#include "G4IonTable.hh"
#include "G4Ions.hh"

#include "G4ParticleGun.hh"

#include "Analysis.hh"

class G4Event;

///////////////////////////////////////////////////////////////////////////////
class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
  PrimaryGeneratorAction();
  ~PrimaryGeneratorAction();
  
public:
  void GeneratePrimaries(G4Event* anEvent);
  inline double GetBeamEnergy(){return energy;}
  inline G4ParticleGun* GetParticleGun(){return particleGun;}
  protected:

  G4ParticleGun*                particleGun;
  G4int                         particlePDG = 0;
  G4double r0 = 0, phi0 = 0, cth0 = 0;
  G4double x0 = 0, y0 = 0, z0 = 0;
  G4double phi1 = 0, cth1 = 0;
  G4double x1 = 0, y1 = 0, z1 = 0;
  G4bool randomizePrimary = false;
  G4float beam_offset_x = 0, beam_offset_y = 0, beam_size = 0, source_width = 0;
  float energy = 0;
  bool doing_continuous_spectrum = false;
  bool interpolate = false, inter2ndOrder = false;
  bool fan_beam = false, isotropic_beam = false, isotropic_extended = false, omnidirectional = false;
  G4double worldRadius = 0.0;

  std::vector<float> e,dNde,N; //the input from the file

  void ReadInputSpectrumFile(std::string);


};
///////////////////////////////////////////////////////////////////////////////
//
#endif
 





