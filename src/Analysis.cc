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
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Author:
// Areg Danagoulian, 2015
// MIT, NSE
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
///////////////////////////////////////////////////////////////////////////////

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

#include "Analysis.hh"

#include "G4SystemOfUnits.hh"
#include "G4ios.hh"

#include "G4RunManager.hh"
#include "G4VPhysicalVolume.hh"
#include "G4Event.hh"
#include "G4Run.hh"
#include "G4Track.hh"
#include "G4ClassificationOfNewTrack.hh"
#include "G4TrackStatus.hh"
#include "G4Step.hh"
#include "G4Types.hh"
#include "G4ThreeVector.hh"

#include "G4GDMLParser.hh"

#include "G4ParticleGun.hh"

#include <time.h>
#include <vector>

#if defined(G4ANALYSIS_USE_ROOT)

#include "TROOT.h"
#include "TApplication.h"
#include "TSystem.h"
#include "TH1.h"
#include "TPad.h"
//  #include "TCanvas.h"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TMath.h"
#endif /* defined (G4ANALYSIS_USE_ROOT) */

#include <iostream>
#include <fstream>

extern G4String RootOutputFile;
extern G4GDMLParser parser;

//#define OLD_CODE //switch from the old code to the new code

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

Analysis::Analysis(G4ParticleGun *particle_gun)
{
	LastDoItTime = (time_t)0;

	file_even = 100000;

	nextinline = 1;

	counter = 1;
	particle_gun_local = particle_gun;

	LightProducingParticle = parser.GetConstant("LightProducingParticle");
	EventGeneratorParticle = parser.GetConstant("ParticleNumber");
	LowEnergyCutoff = parser.GetConstant("LowEnergyCutoff");
	if (parser.GetConstant("KeepOnlyMainParticle") == 0)
		KeepOnlyMainParticle = false;
	else
		KeepOnlyMainParticle = true;

	SaveSurfaceHitTrack = false;
	SaveTrackInfo = false;
	SaveEdepositedTotalEntry = false;
	if (parser.GetConstant("SaveSurfaceHitTrack") == 1)
		SaveSurfaceHitTrack = true;
	if (parser.GetConstant("SaveTrackInfo") == 1)
		SaveTrackInfo = true;
	if (parser.GetConstant("SaveEdepositedTotalEntry") == 1)
		SaveEdepositedTotalEntry = true;

	// file for the text output

#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

	// open the output data file

	TString outfile_name = RootOutputFile;

	f = new TFile(outfile_name.Data(), "RECREATE");

	// create a "tree" for the data to be stored into

	tree = new TTree("tree", "main tree");

	// defines "branches" of the tree

	//  tree->Branch("npart",&npart,"npart/I");
	tree->Branch("E_beam", &E_beam, "E_beam/D");
	tree->Branch("E_incident", &E, "E_incident/D");
	tree->Branch("E_deposited", &Edep, "E_deposited/D");
	tree->Branch("x_incident", &x, "x_incident/D");
	tree->Branch("y_incident", &y, "y_incident/D");
	tree->Branch("z_incident", &z, "z_incident/D");
	tree->Branch("theta", &theta, "theta/D");
	tree->Branch("Time", &Time, "Time/F");
	tree->Branch("EventID", &EventID, "EventID/L");
	tree->Branch("TrackID", &TrackID, "TrackID/L");
	tree->Branch("ParticleID", &ID, "ParticleID/L");
	//  char *tmp=(char*)ParticleName_placeholder.c_str(); //same as below -- set the pointer to the placeholder for particle name
	//  tree->Branch("ParticleName",tmp,"ParticleName/C");
	tree->Branch("ParticleName", &ParticleName);
	tree->Branch("CreatorProcessID", &ProcID, "CreatorProcessID/L"); // obsolete
	//  char *tmp2=(char*)CreatorProcessName.c_str(); //a tmp pointer at the creatorprocessname, which will be updated at the end of every track
	tree->Branch("CreatorProcessName", &CreatorProcessName);
	tree->Branch("IsEdepositedTotalEntry", &IsSummaryEntry, "IsEdepositedTotalEntry/O");
	tree->Branch("IsSurfaceHitTrack", &IsSurfaceHitTrack, "IsSurfaceHitTrack/O");
	tree->Branch("channel", &channel, "channel/l");

#endif /* defined (G4ANALYSIS_USE_ROOT) */
	textoutput = parser.GetConstant("TextOutputOn");
	briefoutput = parser.GetConstant("BriefOutputOn");

	if (textoutput)
	{
		std::string data_file_name;
		std::string rootoutputfile = (std::string)RootOutputFile;
		if (rootoutputfile.find(".root") < rootoutputfile.length())
		{
			data_file_name = (std::string)rootoutputfile.substr(0, rootoutputfile.find(".root"));
			data_file_name += ".dat";
		}
		else
			data_file_name = (std::string)RootOutputFile + ".dat";

		data_file.open(data_file_name.c_str(), std::ofstream::out | std::ofstream::trunc); // open the text file
		if (briefoutput)
			data_file << "E_beam(MeV)\tE(MeV)\tEventID\tParticleName\tCreatorProcessName\tTime(ns)\t detector#" << std::endl;
		else
			data_file << "E_beam(MeV)\tE_incident(MeV)\tE_deposited(MeV)\tx_incident\ty_incident\tz_incident\ttheta\tTime\tEventID\tTrackID\tParticleID\tParticleName\tCreatorProcessName\tIsEdepositedTotalEntry\tIsSurfaceHitTrack\tdetector#" << std::endl;
	}
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

Analysis::~Analysis()
{
	// OnceAWhileDoIt();

#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

	f->Write();
	f->Close();
#endif /* defined (G4ANALYSIS_USE_ROOT) */
	if (textoutput)
		data_file.close();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::Construct(const G4VPhysicalVolume *theWorldWolume)
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::ConstructParticle()
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::ConstructProcess()
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::SetCuts()
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::GeneratePrimaries(const G4Event *anEvent)
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::BeginOfEventAction(const G4Event *anEvent)
{
	E_beam = particle_gun_local->GetParticleEnergy(); // We get the energy of the particle at the onset of the event

	EventID = anEvent->GetEventID();
	ResetEverything(); // reset all the class variables

#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::EndOfEventAction(const G4Event *anEvent)
{

	for (unsigned int i = 0; i < Ev.size(); ++i)
	{ // looping over all the tracks in the detector
		if (IsSurfaceHit.at(i))
			E = Ev.at(i); // fill the incident energy variable ONLY for incident hit entries
		Edep = Edepv.at(i);
		x = xv.at(i);
		y = yv.at(i);
		z = zv.at(i);
		theta = thetav.at(i);
		ID = IDv.at(i);
		TrackID = TrackIDv.at(i);
		//    EventID=EventIDv.at(i); //defined in the beginning
		ProcID = ProcIDv.at(i);
		CreatorProcessName = ProcessNamev.at(i); // copy over the name to the placeholder
		ParticleName = ParticleNamev.at(i);		 // same here
		Time = Timev.at(i);
		IsSurfaceHitTrack = IsSurfaceHit.at(i);
		channel = detector_hit.at(i);

		if (detector_hit.at(i) >= 0 && ((IsSurfaceHitTrack && SaveSurfaceHitTrack) || SaveTrackInfo))
		{ // filter out the empty stuff
			if (textoutput)
			{
				if (briefoutput)
				{
					if (SaveTrackInfo)
						E = Edep; // if this is tracking mode then we actually want to keep the deposited energy, not the incident energy
					data_file << std::setprecision(5);
					data_file << E_beam
							  << "\t" << E // earlier we changed this to Edep, that is not correct, will give wrong answers for surfacehit tracks.  This however is also a bug -- it slaps the main track's energy (when it enters the volume onto the individual tracks
							  << "\t" << EventID
							  << "\t" << ParticleName.c_str()
							  << "\t" << CreatorProcessName.c_str()
							  << "\t" << Time
							  << "\t" << detector_hit.at(i)
							  << std::endl;
				}
				else
				{
					data_file << std::setprecision(5);
					data_file << E_beam
							  << "\t" << E
							  << "\t" << Edep
							  << "\t" << x
							  << "\t" << y
							  << "\t" << z
							  << "\t" << theta
							  << "\t" << Time
							  << "\t" << EventID
							  << "\t" << TrackID
							  << "\t" << ID
							  << "\t" << ParticleName.c_str()
							  << "\t" << CreatorProcessName.c_str()
							  << "\t" << 0
							  << "\t" << IsSurfaceHitTrack
							  << "\t" << detector_hit.at(i)
							  << std::endl;
				}
			}
#if defined(G4ANALYSIS_USE_ROOT)
			else
				tree->Fill();
#endif
		}
	}
	// Now, fill the summary entry
	if (SaveEdepositedTotalEntry)
	{
		IsSummaryEntry = true;
		IsSurfaceHitTrack = false;
		Edep = 0; // set it to zero
		CreatorProcessName = "";
		for (unsigned int i = 0; i < Ev.size(); ++i)
		{																			// add ALL the deposited energies from ALL the tracks that hit the detector
			if (detector_hit.at(i) >= 0 &&											// make sure we are inside the detector
				(IDv.at(i) == LightProducingParticle ||								// this is the designated light producing particle, OR
				 LightProducingParticle == 0 ||										// the light producing particle has been set to 0 (i.e. everything), OR
				 (LightProducingParticle == 2212 && ProcessNamev.at(i) == "hIoni")) // this is an hadron ionization track from a proton
			)
			{
				Edep += Edepv.at(i);
				CreatorProcessName += ProcessNamev.at(i) + "/";
			}
		}
#if defined(G4ANALYSIS_USE_ROOT)
		if (gSystem)
			gSystem->ProcessEvents();
#endif /* defined (G4ANALYSIS_USE_ROOT) */
		if (Edep > 0)
		{

			if (textoutput)
			{
				if (briefoutput)
				{
					data_file << std::setprecision(5);
					data_file << E_beam
							  << "\t" << Edep
							  << "\t" << EventID
							  << "\t" << -1
							  << "\t" << CreatorProcessName.c_str()
							  << std::endl;
				}
				else
				{
					data_file << std::setprecision(5);
					data_file << E_beam << "\t"
							  << -1
							  << "\t" << Edep
							  << "\t" << -1
							  << "\t" << -1
							  << "\t" << -1
							  << "\t" << -1
							  << "\t" << Time
							  << "\t" << EventID
							  << "\t" << -1
							  << "\t" << -1
							  << "\t" << -1
							  << "\t" << CreatorProcessName.c_str()
							  << "\t" << 1
							  << "\t" << 0
							  << std::endl;
				}
			}
#if defined(G4ANALYSIS_USE_ROOT)
			else
				tree->Fill();
#endif
		}
	}
#if defined(G4ANALYSIS_USE_ROOT)
	if (tree->GetEntries() % 500000 == 1)
		tree->AutoSave("SaveSelf");
#endif

	if (anEvent->GetEventID() % 100 == 0)
		std::cout << "\r\tEvent, and tracks:\t" << anEvent->GetEventID() << "\t\t" << Ev.size() << std::flush;

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::ClassifyNewTrack(
	const G4Track *aTrack,
	G4ClassificationOfNewTrack *classification_ptr)
{
	// G4ClassificationOfNewTrack &classification = (*classification_ptr);

#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

	G4String particleName = aTrack->GetDefinition()->GetParticleName();

	if (particleName == "opticalphoton")
	{
		const G4double LambdaE = 2.0 * 3.14159265358979323846 * 1.973269602e-16 * m * GeV;

		Double_t aWaveLength = 0.0;										// will be in [nanometer]
		aWaveLength = (LambdaE / aTrack->GetTotalEnergy()) / nanometer; // in [nanometer]
																		// aWaveLength = (LambdaE / aTrack->GetKineticEnergy()) / nanometer; // in [nanometer]
																		//      if (hOPWaveLength) hOPWaveLength->Fill(aWaveLength, aTrack->GetWeight()); // Wavelength of the produced optical photon
	}

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::NewStage()
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::PrepareNewEvent()
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::PreUserTrackingAction(const G4Track *aTrack)
{
#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::PostUserTrackingAction(const G4Track *aTrack,
									  G4TrackStatus *status_ptr)
{
	// G4TrackStatus &status = (*status_ptr);

#if defined(G4ANALYSIS_USE_ROOT)

	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */

	OnceAWhileDoIt();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::UserSteppingAction(const G4Step *aStep)
{

	if (aStep == NULL)
	{
		std::cout << "Null aStep pointer in Analysis::UserSteppingAction, exiting \n";
		exit(8);
	}

	long unsigned int trackid = aStep->GetTrack()->GetTrackID();

	if (TrackMustDie(aStep))
	{ // apply the cuts here
		aStep->GetTrack()->SetTrackStatus(fStopAndKill);
		return;
	}

#ifdef OLD_CODE
	std::string tmp1 = aStep->GetTrack()->GetDefinition()->GetParticleName();
	//	std::string tmp2=aStep->GetTrack()->GetCreatorProcess()->GetProcessName();
	float tmp3 = aStep->GetTrack()->GetGlobalTime() / ns;
	//	if ((long unsigned int)Ev.size() < trackid)
	if (IsThisANewTrack(trackid))
	{							 // a new track.  trackid starts from 1.
		CreateNewEntry(trackid); // create a new entry in the vector
	}

	if (EnteringDetector(aStep)) // stepping into det for the first time
	{

		IsSurfaceHit[trackid - 1] = true;
		detector_hit[trackid - 1] = GetDetectorNumber(aStep);;

		Ev[trackid - 1] = aStep->GetPreStepPoint()->GetKineticEnergy() / (MeV);

		X = aStep->GetPostStepPoint()->GetPosition(); // take the position from the post step position
		xv[trackid - 1] = X.x() / (mm);
		yv[trackid - 1] = X.y() / (mm);
		zv[trackid - 1] = X.z() / (mm);
		Timev[trackid - 1] = aStep->GetTrack()->GetGlobalTime() / ns;
		p = aStep->GetPreStepPoint()->GetMomentum();
		thetav[trackid - 1] = asin(sqrt(pow(p.x(), 2) + pow(p.y(), 2)) / p.mag()); // the angle of the particle relative to the Z axis
		if (aStep->GetTrack()->GetDefinition()->GetParticleName() == "gamma")
		{
			if (theta > 3.14159 / 4.)
			{
				std::cout << "Potentially dangerous behavior:  killing gammas >45deg" << std::endl;
				aStep->GetTrack()->SetTrackStatus(fStopAndKill); // kill all gammas that are >45deg
			}
		}

		ParticleNamev[trackid - 1] = aStep->GetTrack()->GetDefinition()->GetParticleName();
		if (aStep->GetTrack()->GetTrackID() > 1)
			ProcessNamev[trackid - 1] = aStep->GetTrack()->GetCreatorProcess()->GetProcessName();
		else
			ProcessNamev[trackid - 1] = "EventGenerator";

		entry++;
	}

	if (IsInDetector(aStep)) // in the det

	{
		IDv[trackid - 1] = aStep->GetTrack()->GetDefinition()->GetPDGEncoding();
		ParticleNamev[trackid - 1] = aStep->GetTrack()->GetDefinition()->GetParticleName();
		if (aStep->GetTrack()->GetTrackID() > 1)
			ProcessNamev[trackid - 1] = aStep->GetTrack()->GetCreatorProcess()->GetProcessName();
		else
			ProcessNamev[trackid - 1] = "EventGenerator";
		TrackIDv[trackid - 1] = aStep->GetTrack()->GetTrackID();
		Edepv[trackid - 1] += aStep->GetTotalEnergyDeposit() / (MeV);

		if (Ev[trackid - 1] == -1e+6)
		{																			// this track was just born
			Ev[trackid - 1] = aStep->GetPreStepPoint()->GetKineticEnergy() / (MeV); // record the _starting_ energy
			Timev[trackid - 1] = aStep->GetTrack()->GetGlobalTime() / ns;			// save the time, but only once!
			//	    std::cout << aStep->GetTrack()->GetTrackID() << "\t" << aStep->GetTrack()->GetGlobalTime() << "\t" << trackid << std::endl;
			X = aStep->GetPostStepPoint()->GetPosition(); // take the position from the post step position
			xv[trackid - 1] = X.x() / (mm);
			yv[trackid - 1] = X.y() / (mm);
			zv[trackid - 1] = X.z() / (mm);
			p = aStep->GetPreStepPoint()->GetMomentum();
			thetav[trackid - 1] = asin(sqrt(pow(p.x(), 2) + pow(p.y(), 2)) / p.mag()); // the angle of the particle relative to the Z axis

			// here we want to determine the detector number that the track hit or was created in.  This is done only once in track's history, at its inseption
//			std::string detector_name = aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName();
//			std::string detector_base_name = "det_phys";
//			int detector_number = atoi(detector_name.substr(detector_name.find("det_phys") + detector_base_name.length()).c_str());
			detector_hit[trackid - 1] = GetDetectorNumber(aStep);
		}
	}
#else
	if (EnteringDetector(aStep)) // stepping into det for the first time
	{
		CreateNewEntry(trackid);	 // create a new entry in the vector, independent of whether it's new track or not.
		entry = TrackIDv.size() - 1; // this is the number of entries in the vector, not the track id

		IsSurfaceHit[entry] = true;
		detector_hit[entry] = GetDetectorNumber(aStep);

		Ev[entry] = aStep->GetPreStepPoint()->GetKineticEnergy() / (MeV);

		X = aStep->GetPostStepPoint()->GetPosition(); // take the position from the post step position
		xv[entry] = X.x() / (mm);
		yv[entry] = X.y() / (mm);
		zv[entry] = X.z() / (mm);
		Timev[entry] = aStep->GetTrack()->GetGlobalTime() / ns;
		p = aStep->GetPreStepPoint()->GetMomentum();
		thetav[entry] = asin(sqrt(pow(p.x(), 2) + pow(p.y(), 2)) / p.mag()); // the angle of the particle relative to the Z axis
		if (aStep->GetTrack()->GetDefinition()->GetParticleName() == "gamma")
		{
			if (theta > 3.14159 / 4.)
			{
				std::cout << "Potentially dangerous behavior:  killing gammas >45deg" << std::endl;
				aStep->GetTrack()->SetTrackStatus(fStopAndKill); // kill all gammas that are >45deg
			}
		}

		ParticleNamev[entry] = aStep->GetTrack()->GetDefinition()->GetParticleName();
		if (aStep->GetTrack()->GetTrackID() > 1)
			ProcessNamev[entry] = aStep->GetTrack()->GetCreatorProcess()->GetProcessName();
		else
			ProcessNamev[entry] = "EventGenerator";
	}

	if (IsInDetector(aStep)) // in the det

	{
		//first check if this is a new track, if so, create a new entry
		if (IsThisANewTrackInThisDetector(aStep))
		{
			CreateNewEntry(trackid); // create a new entry in the vector
			entry = TrackIDv.size() - 1; // this is the number of entries in the vector, not the track id
		}
		else
			entry = TrackIDv.size()-1; // this is the number of entries in the vector, not the track id
		IDv[entry] = aStep->GetTrack()->GetDefinition()->GetPDGEncoding();
		ParticleNamev[entry] = aStep->GetTrack()->GetDefinition()->GetParticleName();
		if (aStep->GetTrack()->GetTrackID() > 1)
			ProcessNamev[entry] = aStep->GetTrack()->GetCreatorProcess()->GetProcessName();
		else
			ProcessNamev[entry] = "EventGenerator";
		TrackIDv[entry] = aStep->GetTrack()->GetTrackID();
		Edepv[entry] += aStep->GetTotalEnergyDeposit() / (MeV);

		if (Ev[entry] == -1e+6)
		{																	  // this track was just born
			Ev[entry] = aStep->GetPreStepPoint()->GetKineticEnergy() / (MeV); // record the _starting_ energy
			Timev[entry] = aStep->GetTrack()->GetGlobalTime() / ns;			  // save the time, but only once!
			//	    std::cout << aStep->GetTrack()->GetTrackID() << "\t" << aStep->GetTrack()->GetGlobalTime() << "\t" << trackid << std::endl;
			X = aStep->GetPostStepPoint()->GetPosition(); // take the position from the post step position
			xv[entry] = X.x() / (mm);
			yv[entry] = X.y() / (mm);
			zv[entry] = X.z() / (mm);
			p = aStep->GetPreStepPoint()->GetMomentum();
			thetav[entry] = asin(sqrt(pow(p.x(), 2) + pow(p.y(), 2)) / p.mag()); // the angle of the particle relative to the Z axis

			detector_hit[entry] = GetDetectorNumber(aStep);
		}
	}
#endif
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....

void Analysis::OnceAWhileDoIt(const G4bool DoItNow)
{
	time_t Now = time(0); // get the current time (measured in seconds)
	if ((!DoItNow) && (LastDoItTime > (Now - 10)))
		return; // every 10 seconds
	LastDoItTime = Now;

#if defined(G4ANALYSIS_USE_ROOT)
	if (gSystem)
		gSystem->ProcessEvents();

#endif /* defined (G4ANALYSIS_USE_ROOT) */
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo....
bool Analysis::TrackMustDie(const G4Step *aStep)
{

	int particleid = aStep->GetTrack()->GetDefinition()->GetPDGEncoding();
	bool verbose = false;
	std::string volumename = aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName(); // changed this from PostStep to PreStep, that way non-light producing particles can still be recorded at the surface, in SurfaceHit mode
	if (volumename.compare(0, 8, "det_phys") != 0 && particleid != EventGeneratorParticle && KeepOnlyMainParticle)
	{ // outside the detector, and not the main track, and we want only the main track
		return true;
	}
	else if (aStep->GetTrack()->GetDefinition()->GetPDGEncoding() == EventGeneratorParticle && // Energy cuts
			 aStep->GetTrack()->GetKineticEnergy() / MeV < LowEnergyCutoff)
	{ // for the main track, kill it off below some limit
		return true;
	}
	else if (aStep->GetPostStepPoint() == NULL || aStep->GetPostStepPoint()->GetPhysicalVolume() == NULL) // we get segfaults at World exit
	{
		if (verbose)
		{
			std::cout
				<< EventID << "\t"
				<< aStep->GetTrack()->GetCurrentStepNumber() << "\t"
				<< aStep->GetTrack()->GetDefinition()->GetParticleName() << "\t"
				<< aStep->GetTrack()->GetTrackID() << "\t"
				//		<< aStep->GetTrack()->GetCreatorProcess()->GetProcessName() << "\t"
				<< aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName()
				<< std::endl;
		}
		return true;
	}
	else
		return false;
}
bool Analysis::EnteringDetector(const G4Step *aStep) // check if we are entering the detector for the first time
{
	long unsigned int trackid = aStep->GetTrack()->GetTrackID();

#ifdef OLD_CODE
	if (aStep->GetPostStepPoint()->GetPhysicalVolume()->GetName().compare(0, 8, "det_phys") == 0 &&
		aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName().compare(0, 8, "det_phys") != 0 && // modified the code so it checks the detector entrance by comparing the Pre!=detector && Post==detector
		IsSurfaceHit[trackid - 1] == false)
#else
	if (aStep->GetPostStepPoint()->GetPhysicalVolume()->GetName().compare(0, 8, "det_phys") == 0 &&
		aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName().compare(0, 8, "det_phys") != 0) // modified the code so it checks the detector entrance by comparing the Pre!=detector && Post==detector
#endif
	{
		return true;
	}
	return false;
}
bool Analysis::IsInDetector(const G4Step *aStep)
{ // check if we are in the detector
	return aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName().compare(0, 8, "det_phys") == 0;
}
void Analysis::ResetEverything()
{
	// reset all the class variables
	entry = 0;
	E = -1;
	x = -1e5;
	y = -1e5;
	z = -1e5;
	theta = -1e5;
	ID = -100000;
	TrackID = -10;
	ProcID = -1;
	Time = -1;
	IsSummaryEntry = false;
	IsSurfaceHitTrack = false;
	Ev.clear();
	Edepv.clear();
	xv.clear();
	yv.clear();
	zv.clear();
	thetav.clear();
	IDv.clear();
	ParticleNamev.clear();
	ParticleName = "n/a";
	ProcessNamev.clear();
	CreatorProcessName = "n/a";
	TrackIDv.clear();
	EventIDv.clear();
	ProcIDv.clear();
	Timev.clear();
	detector_hit.clear();
	IsSurfaceHit.clear();
	IsNewTrack.clear();
}
void Analysis::CreateNewEntry(long unsigned int trackid)
{
#ifdef OLD_CODE
	Ev.resize(trackid, -1e+6);
	Edepv.resize(trackid, 0);
	xv.resize(trackid, -1e+6);
	yv.resize(trackid, -1e+6);
	zv.resize(trackid, -1e+6);
	thetav.resize(trackid, -1e+6);
	IDv.resize(trackid, -1e+6);
	ParticleNamev.resize(trackid, "");
	ProcessNamev.resize(trackid, "");
	TrackIDv.resize(trackid, -1e+6);
	EventIDv.resize(trackid, -1e+6);
	ProcIDv.resize(trackid, -1e+6);
	Timev.resize(trackid, -1e+6);
	detector_hit.resize(trackid, -1e+6);
	IsSurfaceHit.resize(trackid, false);
	IsNewTrack.resize(trackid, false);
#else
	Ev.push_back(-1e+6);
	Edepv.push_back(0);
	xv.push_back(-1e+6);
	yv.push_back(-1e+6);
	zv.push_back(-1e+6);
	thetav.push_back(-1e+6);
	IDv.push_back(-1e+6);
	ParticleNamev.push_back("");
	ProcessNamev.push_back("");
	TrackIDv.push_back(trackid);
	EntryID.push_back("");
	EventIDv.push_back(-1e+6);
	ProcIDv.push_back(-1e+6);
	Timev.push_back(-1e+6);
	detector_hit.push_back(-1e+6);
	IsSurfaceHit.push_back(false);
	IsNewTrack.push_back(false);

#endif
}
#ifdef OLD_CODE
bool Analysis::IsThisANewTrack(long unsigned int trackid)
{
	if ((long unsigned int)Ev.size() < trackid)
		return true;
	else
		return false;
}
#else
bool Analysis::IsThisANewTrackInThisDetector(const G4Step *aStep)
{
	long unsigned int trackid = aStep->GetTrack()->GetTrackID();
	std::string detector_name = aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName();
	std::string detector_base_name = "det_phys";
	int detector_number = atoi(detector_name.substr(detector_name.find("det_phys") + detector_base_name.length()).c_str());

	for (unsigned int i = 0; i < TrackIDv.size(); ++i)
	{
		if (TrackIDv.at(i) == trackid && detector_number == detector_hit.at(i))
			return false;
	}
	return true;
}
#endif
int Analysis::GetDetectorNumber(const G4Step *aStep)
{
	std::string detector_name = aStep->GetPreStepPoint()->GetPhysicalVolume()->GetName();
	std::string detector_base_name = "det_phys";
	int detector_number = atoi(detector_name.substr(detector_name.find("det_phys") + detector_base_name.length()).c_str());
	return detector_number;
}