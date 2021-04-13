#----------------------------------------------------------------------------
# Setup the project
cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(grasshopper)
# Allow User Build Options Here...
option(WITH_GEANT4_UIVIS "Build with Geant4 UI and Vis drivers" ON) # Can switch to OFF if not building with vis drivers --> NOT recommended 
option(WITH_ROOT "Build with ROOT" ON) # Can switch off if ROOT Output not desired 
# Add various compile definitions 
if(WITH_ROOT)
  add_compile_definitions(G4ANALYSIS_USE_ROOT)
  message(STATUS "G4ANALYSIS_USE_ROOT Added to compile Definitions.")
endif()

#Suppress Warnings 
if(${SHOW_WARNINGS})
  message(STATUS "Running make with warning full verbosity")
else()
  message(STATUS "Subduing some warnings")
  add_compile_options(-Wno-unused-variable -Wno-shadow -Wno-unused-parameter)
endif()

#Find Geant4 Package 
# Here you require a Geant4 minimum version... example set to 10.5 
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 10.5 REQUIRED ui_all vis_all)
  message(STATUS "Built Geant4 with UI and Vis Drivers")
else()
  find_package(Geant4 10.5 REQUIRED)
endif()

#----------------------------------------------------------------------------
# Setup Geant4 include directories and compile definitions
#
include(${Geant4_USE_FILE})

# Find ROOT (required package)
if(WITH_ROOT)
  find_package(ROOT CONFIG REQUIRED)
  if(ROOT_FOUND)	
    message(STATUS "ROOT Found.")	
  else()	
    message(STATUS "ROOT NOT Found. --> MAKE WILL FAIL!")
  endif()
  
  include("${ROOT_USE_FILE}")
  include_directories(${PROJECT_SOURCE_DIR}/include	
                      ${Geant4_INCLUDE_DIR}	                   
                      ${ROOT_INCLUDE_DIR}
                     )
                    
  else()
    include_directories(${PROJECT_SOURCE_DIR}/include	
                        ${Geant4_INCLUDE_DIR}	                   
                       )
  
endif()

# Locate Sources and Headers 
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)	
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#----------------------------------------------------------------------------
# Add the executable, and link it to the Geant4 and ROOT libraries
#
add_executable(grasshopper grasshopper.cc ${sources} ${headers})

if(WITH_ROOT)
  target_link_libraries(grasshopper ${Geant4_LIBRARIES} ${ROOT_LIBRARIES})
else()
  target_link_libraries(grasshopper ${Geant4_LIBRARIES})
endif()

#----------------------------------------------------------------------------
# Copy relavant scripts to the build directory, i.e. the directory in which we
# build grasshopper. This is so that we can run the executable directly because it
# relies on these scripts being in the current working directory.
#
  
set(VIS_SCRIPTS
  vis.mac
  )
  

foreach(_script ${VIS_SCRIPTS})
configure_file(
  ${PROJECT_SOURCE_DIR}/${_script}
  ${PROJECT_BINARY_DIR}/${_script}
  COPYONLY
  )
endforeach()

#----------------------------------------------------------------------------
# Install the executable to 'bin' directory under CMAKE_INSTALL_PREFIX
#
install(TARGETS grasshopper DESTINATION bin)
