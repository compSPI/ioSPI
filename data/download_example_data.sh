#!/bin/bash

URLlist=""
# RCSB PDB X-ray crystallography example: 4PIR
URLlist="${URLlist} https://files.rcsb.org/download/4PIR.pdb.gz" 
URLlist="${URLlist} https://files.rcsb.org/download/4PIR.cif.gz"
URLlist="${URLlist} https://edmaps.rcsb.org/coefficients/4pir.mtz"
# RCSB PDB cryoEM example: 6Y1Z
URLlist="${URLlist} https://files.rcsb.org/download/6Y1Z.pdb.gz"
URLlist="${URLlist} https://files.rcsb.org/download/6Y1Z.cif.gz"
URLlist="${URLlist} https://files.rcsb.org/pub/emdb/structures/EMD-10673/map/emd_10673.map.gz"

for url in $URLlist; do
  echo "> wget $url"
  wget $url
done
