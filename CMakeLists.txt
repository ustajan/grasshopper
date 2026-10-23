#----------------------------------------------------------------------------
# grasshopper: a Geant4 front end driven entirely by GDML input files.
#
# Build:
#   cmake -S . -B build [-DWITH_GEANT4_UIVIS=OFF] [-DWITH_ROOT=ON]
#   cmake --build build && cmake --install build
#
# The version is read from the top-level VERSION file (single source of truth
# shared with pyproject.toml). It tracks the Geant4 release grasshopper was
# validated against, with an optional fourth component for grasshopper-only
# fixes (e.g. 11.4.3.1).
#----------------------------------------------------------------------------
cmake_minimum_required(VERSION 3.17 FATAL_ERROR)

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" GRASSHOPPER_VERSION LIMIT_COUNT 1)
string(STRIP "${GRASSHOPPER_VERSION}" GRASSHOPPER_VERSION)
project(grasshopper VERSION ${GRASSHOPPER_VERSION} LANGUAGES CXX)

include(GNUInstallDirs)
include(CheckIncludeFileCXX)

# Keep the directories of the linked Geant4 (and ROOT) shared libraries in the
# installed binary's RPATH, so `make install` produces a runnable executable
# without the user having to set (DY)LD_LIBRARY_PATH.
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
if(APPLE)
  set(CMAKE_MACOSX_RPATH TRUE)
endif()

#----------------------------------------------------------------------------
# User options
#----------------------------------------------------------------------------
# WITH_GEANT4_UIVIS requests Geant4's interactive UI and vis drivers
# (OpenGL/X11/Qt). It is NOT needed for the VRML .wrl file output grasshopper
# produces, which only requires core Geant4. Package builds (conda-forge) turn
# this OFF to keep the link set minimal.
option(WITH_GEANT4_UIVIS "Request Geant4 interactive UI and vis drivers" ON)
option(WITH_ROOT "Build with ROOT output support" OFF)
option(BUILD_TESTING "Build the smoke test (ctest)" ON)
option(SHOW_WARNINGS "Do not suppress selected compiler warnings" OFF)

if(WITH_ROOT)
  add_compile_definitions(G4ANALYSIS_USE_ROOT)
  message(STATUS "G4ANALYSIS_USE_ROOT added to compile definitions.")
endif()

if(SHOW_WARNINGS)
  message(STATUS "Running make with warning full verbosity")
else()
  message(STATUS "Subduing some warnings")
  add_compile_options(-Wno-unused-variable -Wno-shadow -Wno-unused-parameter)
endif()

#----------------------------------------------------------------------------
# Geant4 (built with GDML support, i.e. -DGEANT4_USE_GDML=ON)
#----------------------------------------------------------------------------
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 11.0 REQUIRED gdml ui_all vis_all)
  message(STATUS "Geant4 found with UI and vis drivers requested")
else()
  find_package(Geant4 11.0 REQUIRED gdml)
  message(STATUS "Geant4 found (core + GDML only; VRML file output still available)")
endif()
include(${Geant4_USE_FILE})

# Visualization in grasshopper means writing VRML files via the VRML2FILE
# driver, which lives in core Geant4. Always enable it.
add_compile_definitions(G4VIS_USE)

set(CMAKE_REQUIRED_INCLUDES ${Geant4_INCLUDE_DIRS} ${Geant4_INCLUDE_DIR})
check_include_file_cxx("G4DAWNFILE.hh" HAVE_G4DAWNFILE_HH)
check_include_file_cxx("G4VRML2.hh" HAVE_G4VRML2_HH)
check_include_file_cxx("G4VRML2File.hh" HAVE_G4VRML2FILE_HH)
if(HAVE_G4DAWNFILE_HH)
  add_compile_definitions(G4VIS_USE_DAWNFILE)
endif()
if(HAVE_G4VRML2_HH)
  add_compile_definitions(G4VIS_USE_VRML)
endif()
if(HAVE_G4VRML2FILE_HH)
  add_compile_definitions(G4VIS_USE_VRMLFILE)
endif()

#----------------------------------------------------------------------------
# ROOT (optional)
#----------------------------------------------------------------------------
if(WITH_ROOT)
  find_package(ROOT CONFIG REQUIRED)
  include("${ROOT_USE_FILE}")
endif()

#----------------------------------------------------------------------------
# Target
#----------------------------------------------------------------------------
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

add_executable(grasshopper grasshopper.cc ${sources} ${headers})
target_include_directories(grasshopper PRIVATE ${PROJECT_SOURCE_DIR}/include)
target_compile_definitions(grasshopper PRIVATE
  GRASSHOPPER_VERSION="${PROJECT_VERSION}"
  GRASSHOPPER_DATADIR="${CMAKE_INSTALL_FULL_DATADIR}/grasshopper"
)
if(WITH_ROOT)
  target_include_directories(grasshopper PRIVATE ${ROOT_INCLUDE_DIRS})
  target_link_libraries(grasshopper PRIVATE ${Geant4_LIBRARIES} ${ROOT_LIBRARIES})
else()
  target_link_libraries(grasshopper PRIVATE ${Geant4_LIBRARIES})
endif()

#----------------------------------------------------------------------------
# Install: binary, GDML schema, example inputs, docs.
# The examples reference the schema as ../../schema/gdml.xsd, which resolves
# both in the source tree and under <prefix>/share/grasshopper/.
#----------------------------------------------------------------------------
install(TARGETS grasshopper RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY ${PROJECT_SOURCE_DIR}/schema/
        DESTINATION ${CMAKE_INSTALL_DATADIR}/grasshopper/schema)
install(DIRECTORY ${PROJECT_SOURCE_DIR}/examples/
        DESTINATION ${CMAKE_INSTALL_DATADIR}/grasshopper/examples
        FILES_MATCHING
          PATTERN "*.gdml"
          PATTERN "*.txt"
          PATTERN "*.mac"
          PATTERN "debug" EXCLUDE)
install(FILES README.md ReleaseNotes.md LICENSE COPYRIGHT
        DESTINATION ${CMAKE_INSTALL_DOCDIR})

#----------------------------------------------------------------------------
# Smoke test: a 500-event electron run on examples/beta/beta_lite.gdml.
# Requires the Geant4 datasets (G4LEDATA etc.) to be visible in the
# environment, as for any Geant4 run.
#----------------------------------------------------------------------------
if(BUILD_TESTING)
  enable_testing()
  add_test(NAME smoke
           COMMAND bash ${PROJECT_SOURCE_DIR}/tests/smoke_test.sh
                   $<TARGET_FILE:grasshopper> ${PROJECT_SOURCE_DIR})
endif()
