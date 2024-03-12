#!/bin/bash

# Defeind ASN.1 executable
ASN1C="/opt/asn1c/bin/asn1c"

# Define input ASN.1 files
ASN_FILES="asn1/e2sm_kpm_v2.0.3-changed.asn asn1/e2ap_v2.asn1"

# Define output directory
OUTPUT_DIR="src"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# ASN.1 compilation flags
FLAGs="-gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted"

# Compile ASN.1 files
$ASN1C -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted $ASN_FILES -D $OUTPUT_DIR
