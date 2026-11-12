#!/bin/bash
# Generate the E2SM-CP (MobiFlow control plane telemetry) ASN.1 sources into
# e2sm_cp/. The spec is maintained in 5GSEC/5G-eBPF (e2sm/e2sm-cp/spec); copy
# asn1/e2sm_cp_v1.00.asn from there when it changes and re-run this script.
#
# Every generated type is prefixed with E2SM_CP_ so it can never clash with the
# E2AP / E2SM-KPM sources in src/; the CP sources are built into their own
# executable (wrapper_cp, see wrapper_compile.sh).

ASN1C="${ASN1C:-/opt/asn1c/bin/asn1c}"
ASN_FILES="asn1/e2sm_v3.00.asn asn1/e2sm_cp_v1.00.asn" # E2SM common IEs + E2SM-CP
OUTPUT_DIR="e2sm_cp"

cd "$(dirname "$0")"
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

ASN1C_PREFIX="E2SM_CP_" $ASN1C -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names \
    -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted $ASN_FILES -D $OUTPUT_DIR
