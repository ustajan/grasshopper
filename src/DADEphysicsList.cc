// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Zach Hartwig, 2015
// MIT, NSE
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////


#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

#include "G4DecayPhysics.hh"

#include "G4EmStandardPhysics.hh"
#include "G4EmExtraPhysics.hh"
#include "G4EmProcessOptions.hh"

#include "G4HadronPhysicsQGSP_BIC_HP.hh"
#include "G4HadronPhysicsQGSP_BIC.hh"
#include "G4HadronElasticPhysics.hh"
#include "G4HadronElasticPhysicsHP.hh"
#include "G4NeutronCrossSectionXS.hh"
#include "G4NeutronTrackingCut.hh"
#include "G4StoppingPhysics.hh"
#include "G4ProtonInelasticProcess.hh"
#include "GammaNuclearPhysics.hh"

#include "G4OpticalPhysics.hh"

#include "G4LossTableManager.hh"
#include "G4ProcessTable.hh"
#include "G4ProcessManager.hh"
#include "G4ProcessVector.hh"

#include "G4ParticleTypes.hh"
#include "G4ParticleTable.hh"
#include "G4Gamma.hh"
#include "G4Electron.hh"
#include "G4Positron.hh"

#include "G4StepLimiter.hh"

#include "DADEphysicsList.hh"

#include "G4ParticleDefinition.hh"

// Processes

#include "G4PhotoNuclearProcess.hh"
#include "G4CascadeInterface.hh"


physicsList::physicsList(G4bool neutronHP,
			 G4bool scintillation) 
  : G4VModularPhysicsList()
{
  defaultCutValue = 0.7*mm;
  cutForGamma = defaultCutValue;
  cutForElectron = defaultCutValue;
  cutForPositron = defaultCutValue;
  cutForProton = defaultCutValue;

  useNeutronHP = neutronHP;
  useScintillation = scintillation;
  verboseLevel = 0;

  ConstructPhysics();
}


physicsList::~physicsList()
{ delete decayPhysics; }


void physicsList::ConstructParticle()
{
  // G4DecayPhysics::ConstructParticle method builds ALL particles.
  // Unintuitive but convenient method for particle construction.
  decayPhysics = new G4DecayPhysics("decay");
  decayPhysics->ConstructParticle();
}


void physicsList::ConstructPhysics()
{
  /////////////////////
  // Transportation  //
  /////////////////////

  AddTransportation();
  

  //////////////////////////////
  // Electronmagnetic physics //
  //////////////////////////////
  
  // Standard EM
  RegisterPhysics(new G4EmStandardPhysics(verboseLevel));

  // Synchrotron and gamma-nuclear physics
  RegisterPhysics(new G4EmExtraPhysics(verboseLevel));


  //////////////////////
  // Hadronic Physics //
  //////////////////////

  // QGSP model with the Binary Ion Cascase (BIC) with high precision
  // neutron transport (HP). Note the required use of complementary of
  // HP version for hadron elastic physics
  if(useNeutronHP){
    RegisterPhysics( new G4HadronPhysicsQGSP_BIC_HP());
    RegisterPhysics( new G4HadronElasticPhysicsHP(verboseLevel) );
  }
  
  // QGSP model with BIC, standard hadron elastic physics, and the
  // extended neutron XS data set for improved non-HP neutron physics
  else{
    RegisterPhysics( new G4HadronPhysicsQGSP_BIC());
    RegisterPhysics( new G4HadronElasticPhysics(verboseLevel) );
    RegisterPhysics( new G4NeutronCrossSectionXS(verboseLevel));
  }
  // Gamma physics
  // doesn't add the photonuclear processes
  //  RegisterPhysics( new GammaNuclearPhysics("gamma"));

  
  //proton inelastic
  //  RegisterPhysics( new G4ProtonInelasticProcess()); //breaks (antiquated)
  // Ion stopping-in-matter physics
  RegisterPhysics( new G4StoppingPhysics(verboseLevel) );
//  RegisterPhysics( new G4HadronPhysicsQGSP_BIC_AllHP(verb)); //breaks

  // Neutron tracking cuts for optimized simulation
  G4NeutronTrackingCut *theNeutronTrackingCut = new G4NeutronTrackingCut(verboseLevel);
  theNeutronTrackingCut->SetTimeLimit(10*microsecond);
  theNeutronTrackingCut->SetKineticEnergyLimit(0.01*eV);
  //RegisterPhysics( theNeutronTrackingCut );


  /////////////////////
  // Optical Physics //
  /////////////////////
  
  // Optical (scintillation/cerenkov/photon transport) physics.
  if(useScintillation){
    opticalPhysics = new G4OpticalPhysics();
    opticalPhysics->SetScintillationByParticleType(false);
    opticalPhysics->SetMaxNumPhotonsPerStep(500);
    opticalPhysics->SetMaxBetaChangePerStep(10.0);
    opticalPhysics->SetTrackSecondariesFirst(kCerenkov,true);
    opticalPhysics->SetTrackSecondariesFirst(kScintillation,true);
    RegisterPhysics(opticalPhysics);
  }
  
  ///////////////////
  // Decay Physics //
  ///////////////////

  // Decay physics for all particles
  RegisterPhysics(new G4DecayPhysics);
  

  ////////////////////
  // Custom Physics //
  ////////////////////
  
  // Particle specific processes

  /*
  auto theParticleIterator=GetParticleIterator();  
  
  theParticleIterator->reset();
  while( (*theParticleIterator)() ) {
    G4ParticleDefinition *particle = theParticleIterator->value();
    G4ProcessManager *particleProcessMgr = particle->GetProcessManager();
    G4String particleName = particle->GetParticleName();
    G4ProcessManager* pManager = particle->GetProcessManager();//G4Gamma::Gamma()->GetProcessManager();
    //
    G4PhotoNuclearProcess* process = new G4PhotoNuclearProcess();
    //
    G4CascadeInterface* bertini = new G4CascadeInterface();
    bertini->SetMaxEnergy(100*keV);
    //    process->RegisterMe(bertini); //screw bertini
    //
    pManager->AddDiscreteProcess(process);
  }
 
  

  }
  */
}


void physicsList::SetCuts()
{
  SetCutValue(cutForGamma, "gamma");
  SetCutValue(cutForElectron, "e-");
  SetCutValue(cutForPositron, "e+");
  SetCutValue(cutForProton, "proton");
}
