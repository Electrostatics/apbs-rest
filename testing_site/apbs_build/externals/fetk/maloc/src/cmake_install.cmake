# Install script for directory: /home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/maloc" TYPE FILE FILES
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/base/maloc/maloc.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/base/maloc/maloc_base.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/psh/maloc/psh.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/psh/maloc/vcom.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/psh/maloc/vmp.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/psh/maloc/vmpi.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsh/maloc/vsh.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vio.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vmem.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vnm.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vset.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vsys.h"
    "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/src/vsys/maloc/vpred.h"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/eoffor/apbs-pdb2pqr/apbs/externals/fetk/maloc/lib/libmaloc.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libmaloc.so")
    endif()
  endif()
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/externals/fetk/maloc/src/base/cmake_install.cmake")
  include("/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/externals/fetk/maloc/src/psh/cmake_install.cmake")
  include("/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/externals/fetk/maloc/src/vsh/cmake_install.cmake")
  include("/home/eoffor/react_flask_pdb2pqr/testing_site/apbs_build/externals/fetk/maloc/src/vsys/cmake_install.cmake")

endif()

