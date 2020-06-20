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
  G4double r0;
  G4double phi0;
  G4double cth0;
  G4double x0,y0,z0;
  G4double phi1;
  G4double cth1;
  G4double x1,y1,z1;
  G4bool randomizePrimary;
  G4float beam_offset_x,beam_offset_y,beam_size,source_width;
  float energy;
  bool doing_continuous_spectrum;
  bool interpolate;
  bool fan_beam,isotropic_beam,isotropic_extended,omnidirectional;

  std::vector<float> e,dNde,N; //the input from the file

  void ReadInputSpectrumFile(std::string);


};
///////////////////////////////////////////////////////////////////////////////
//
#endif
 





