#!/bin/bash
cd output
go run ../../pdb2pqr/pdb2pqr-cli.go --with-ph=7.0 --ph-calc-method=propka --apbs-input --ff=parse --verbose ../samples/1a1p.pdb 1a1p_out.pqr
# go run ../../pdb2pqr/pdb2pqr-cli.go --with-ph=7.0 --ph-calc-method=pdb2pka --apbs-input --ff=parse --verbose ../samples/1a1p.pdb 1a1p_out.pqr

cd ..