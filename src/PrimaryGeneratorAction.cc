// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Areg Danagoulian, 2015
// MIT, NSE
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////


#include "PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4ParticleGun.hh"
#include "G4UImanager.hh"
#include "globals.hh"
#include "Randomize.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4GDMLParser.hh"

extern G4GDMLParser parser;

//////////////////////////////////////////////////////////////////////////////
//
PrimaryGeneratorAction::PrimaryGeneratorAction()
{

  G4int n_particle = 1;
  particleGun = new G4ParticleGun(n_particle);

  G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
  G4String particleName;

  int  particleNumber=parser.GetConstant("ParticleNumber");
  //  particle = particleTable->FindParticle(particleName="e-");
  G4ParticleDefinition *particle = particleTable->FindParticle(particleNumber);
  //  particle = particleTable->FindParticle(particleName="geantino");
  particleGun->SetParticleDefinition(particle);


  particleGun->SetParticleDefinition(particle);

  energy = parser.GetQuantity("BeamEnergy");
  if(energy<0){
	  doing_continuous_spectrum=true;
    if (energy/CLHEP::MeV == -3) {
      interpolate=0;
      inter2ndOrder=0;
    } else if (energy/CLHEP::MeV == -2) {
      interpolate=1;
      inter2ndOrder=1;
    } else {
      interpolate=1;
      inter2ndOrder=0;
    }
	  ReadInputSpectrumFile("input_spectrum.txt");
  }
  else doing_continuous_spectrum=false;

  z0 = parser.GetQuantity("BeamOffsetZ")*CLHEP::mm;
  //std::cout<<"x0: "<<x0<<" y0: "<<y0<<" z0: "<<z0<<"\n";
  beam_offset_x = parser.GetQuantity("BeamOffsetX");
  beam_offset_y = parser.GetQuantity("BeamOffsetY");
  beam_size = parser.GetQuantity("BeamSize");
  source_width=0; //by default the width along Z is zero

  if(beam_size/CLHEP::mm == -1){ //the user wants to do a fan beam
	  beam_size=0;
	  fan_beam=true;
	  isotropic_beam=false;
	  isotropic_extended=false;
    omnidirectional=false;
  }
  else if(beam_size/CLHEP::mm == -2){ // the user wants an isotropic source
    beam_size=0;
    isotropic_beam=true;
    fan_beam=false;
    isotropic_extended=false;
    omnidirectional=false;
  }
  else if(beam_size/CLHEP::mm == -3){ // the user wants an omnidirectional background source
    /*
     During analysis, correct for world volume and number of Monte Carlo particles:
     phi = background flux (counts per unit area per unit time)
     N = # of MC particles (EventsToRun)
     R = WorldRadius
     then,
     weight per particle = (4*pi*R^2) * phi/N
     for instance,
     Measured Integrated Detector Flux (n/s) = Detected MC count * weight
     */
    beam_size=0;
    isotropic_beam=false;
    fan_beam=false;
    omnidirectional=true;
    isotropic_extended=false;
  }
  else if(beam_size/CLHEP::mm < 0 ){ // any negative number other than -1, -2 --> the user wants an isotropic, extended source
    beam_size= fabs(beam_size/(CLHEP::mm)); //actual spot size
    isotropic_beam=false;
    fan_beam=false;
    isotropic_extended=true;
    //now, check if there is a beam_width.txt file.  If so, set beam_width to the content
    //Eventually we should migrate this into the .gdml file too.
    std::ifstream f("beam_width.txt");
    if(f.is_open()) { //check that the file is open, i.e. it's there
      while(!f.eof()) {
    	  float a;
    	  f>>a;
    	  source_width=a*CLHEP::mm;
      }
    }
    else {
    	source_width=0; //zero, as before
    }
    f.close();

  }
  else{  // do a pencil beam
    fan_beam=false;
    isotropic_beam=false;  
  }  

}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
  delete particleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{

#if defined (G4ANALYSIS_USE_ROOT)
  const float pi=TMath::Pi();
#else
  const float pi=acos(-1);
#endif


  // set particle kinetic energy to the gun
  if(doing_continuous_spectrum){//sample from dNde <- this gets called only if energy<0 in input.  Otherwise this gets skipped
    double random=G4UniformRand()*N[N.size()-1];
    //determine which value of energy this corresponds to.
    for(unsigned int i=0;i<N.size();i++) {
      if(N[i]>random) {
        if (interpolate) {
          if (inter2ndOrder && dNde[i] != dNde[i-1]) {
            // second order interpolation
            float a = 0.5*(dNde[i] - dNde[i-1]) / (e[i] - e[i-1]);
            float b = dNde[i-1] - 2*a*e[i-1];
            float c = N[i-1] - random - dNde[i-1]*e[i-1] + a*e[i-1]*e[i-1];
            energy = (-b + pow(b*b - 4*a*c, 0.5)) / (2*a);
          } else {
            // first order interpolation
            float f = (random - N[i-1]) / (N[i] - N[i-1]);
            energy = f*e[i] + (1-f)*e[i-1];
          }
        } else {
          // no interpolation
          energy = e[i];
        }
        break;
      }
    }
  }
  particleGun->SetParticleEnergy(energy);

  G4double r, ph;
  G4double x_r, y_r, z_r;

  if (omnidirectional){
    r = parser.GetQuantity("WorldRadius"); // WORLD RADIUS
    
    ph = 360.*G4UniformRand()*CLHEP::deg;
    G4double u = 2*G4UniformRand()-1;
    x_r = r*pow((1 - u*u), 0.5)*cos(ph);
    y_r = r*pow((1 - u*u), 0.5)*sin(ph);
    z_r = r*u;
  }
  else{
    r = beam_size*acos(G4UniformRand())/pi*2.;
    ph = 360.*G4UniformRand()*CLHEP::deg;

    x_r = r*cos(ph);
    y_r = r*sin(ph);
    z_r = source_width*(G4UniformRand()-0.5);
  }
  
  particleGun->SetParticlePosition(G4ThreeVector(x_r+beam_offset_x,y_r+beam_offset_y,z_r+z0));
  
  G4double theta;
  G4double phi;
  G4ThreeVector vDir;
  
  if(fan_beam){ //let's do a fan beam
	  theta = acos(0.5*(G4UniformRand()-0.5))-90.*CLHEP::deg;
	  phi   = 0.005*(G4UniformRand()-0.5);
  }
  else if(isotropic_beam || isotropic_extended){ //isotropic
    theta = acos(2*G4UniformRand()-1); //truly isotropic
    //	  theta = acos(0.05*G4UniformRand()+0.95);
	  phi   = 2*acos(-1)*G4UniformRand();
    vDir = G4ThreeVector(sin(theta)*cos(phi),sin(theta)*sin(phi),cos(theta));
  }
  else if (omnidirectional){
    theta = acos(-pow(1 - G4UniformRand(), 0.5));
    phi   = 2*acos(-1)*G4UniformRand();
    vDir = G4ThreeVector(sin(theta)*cos(phi),sin(theta)*sin(phi),cos(theta));
    vDir.rotate(acos(z_r / r), G4ThreeVector(-(y_r+beam_offset_y), x_r+beam_offset_x, 0));
  }
  else{
	  theta = 0.*CLHEP::deg;
	  phi = 0.*CLHEP::deg;
    vDir = G4ThreeVector(sin(theta)*cos(phi),sin(theta)*sin(phi),cos(theta));
  }
  
  particleGun->SetParticleMomentumDirection(vDir);
   
  particleGun->GeneratePrimaryVertex(anEvent);
   
}
void PrimaryGeneratorAction::ReadInputSpectrumFile(std::string filename){
// This method, if a negative energy is specified for the particle,
	// opens and reads the default input spectrum file (asci txt)
	// To be implemented.

  std::ifstream f(filename);
  if(f.is_open()) { //check that the file is open
    std::cout<<"oooooooooooooo Reading input file for beam energies oooooooooooo"<<std::endl;
    while(!f.eof()) {
      float a,b;
      f>>a>>b;
      e.push_back(a);
      dNde.push_back(b);
    }
    if (interpolate) N.push_back(0);
    else N.push_back(dNde.at(0));
    for(unsigned int i=1;i<e.size();i++) {
      if (interpolate) {
        float dx = e.at(i) - e.at(i-1);
        float yAvg = 0.5*(dNde.at(i) + dNde.at(i-1));
        N.push_back(N.at(i-1) + dx*yAvg);
      } else {
        N.push_back(N.at(i-1) + dNde.at(i));
      }
    }
  } else {
    std::cout<<"Input file expected, however open failed, exiting."<<std::endl;
    exit(8);
  }
  
  f.close();
}
