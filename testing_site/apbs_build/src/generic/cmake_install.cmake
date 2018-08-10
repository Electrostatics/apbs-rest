# Install script for directory: /home/eoffor/apbs-pdb2pqr/apbs/src/generic

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/apbs/generic" TYPE FILE FILES
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/nosh.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/mgparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/femparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/pbamparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/pbsamparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/pbeparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/bemparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/geoflowparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/apolparm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vacc.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/valist.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vatom.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vpbe.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vcap.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vclist.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vstring.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vparam.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vgreen.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vmatrix.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vhal.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/src/generic/vunit.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/lib/libapbs_generic.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so"
         OLD_RPATH "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/lib:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libapbs_generic.so")
    endif()
  endif()
endif()

