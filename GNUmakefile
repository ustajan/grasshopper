# $Id: GNUmakefile,v 1.5 2000/06/14 17:51:35 flei Exp $
# --------------------------------------------------------------
# GNUmakefile for examples module.  Gabriele Cosmo, 06/04/98.
# --------------------------------------------------------------


G4UI_USE_QT=
G4VIS_USE_OPENGLQT=
#ROOTSYS= #uncomment to disable root

name := grasshopper
G4TARGET := $(name)
G4EXLIB := true

ifndef G4INSTALL
  G4INSTALL = ../../../../../../../..
endif


.PHONY: all
all: lib bin

# Deal with Geant4 version parsing.  Inelegant, but should work
G4V := $(shell geant4-config --version)
G4VS := $(subst ., ,$(G4V))
G4MAJV := $(word 1,$(G4VS))
G4MINV := $(word 2,$(G4VS))
G4SUBV := $(word 3,$(G4VS))

#include $(G4WORKDIR)/binmake.gmk
include $(G4INSTALL)/config/binmake.gmk

CPPFLAGS += -O0 -g # -g -O0
CPPFLAGS += -DG4MAJV=$(G4MAJV) -DG4MINV=$(G4MINV) -DG4SUBV=$(G4SUBV)

########################### ROOT #################################
ifdef ROOTSYS
ifndef G4UI_USE_ROOT
CPPFLAGS += -DG4ANALYSIS_USE_ROOT $(shell $(ROOTSYS)/bin/root-config --cflags)
ROOTLIBS = $(shell $(ROOTSYS)/bin/root-config --nonew --glibs) -lMinuit -lHtml
ROOTLIBS := $(filter-out -lNew,$(ROOTLIBS))
ROOTLIBS := $(filter-out -lpthread,$(ROOTLIBS))
LDLIBS += $(ROOTLIBS)
endif
endif

# end of file GNUmakefile by Jacek M. Holeczek
