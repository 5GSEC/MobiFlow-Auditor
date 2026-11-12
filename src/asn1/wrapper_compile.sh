#!/bin/bash
set -e
cd "$(dirname "$0")"
# E2AP + E2SM-KPM
gcc -o wrapper -Isrc/ -DPDU src/*.c wrapper.c -lm
# E2SM-CP (own executable: separate asn1c sources, see asn1_compile_cp.sh)
gcc -O2 -o wrapper_cp -Ie2sm_cp/ e2sm_cp/*.c wrapper_cp.c -lm
