# Install script for directory: /home/eoffor/apbs-pdb2pqr/apbs/src/pmgc

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/apbs/pmgc" TYPE FILE FILES
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/buildAd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/buildBd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/buildGd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/buildPd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/cgd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/gsd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/matvecd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mgcsd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mgdrvd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mgsubd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mikpckd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mlinpckd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mypdec.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/newtond.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/newdrvd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/powerd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/smoothd.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/pmgc/mgfasd.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/lib/libapbs_pmgc.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so"
         OLD_RPATH "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/lib:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_pmgc.so")
    endif()
  endif()
endif()

