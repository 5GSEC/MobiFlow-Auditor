/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2AP-IEs"
 * 	found in "asn1/e2ap_v2.asn1"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_RICcallProcessID_H_
#define	_RICcallProcessID_H_


#include "asn_application.h"

/* Including external dependencies */
#include "OCTET_STRING.h"

#ifdef __cplusplus
extern "C" {
#endif

/* RICcallProcessID */
typedef OCTET_STRING_t	 RICcallProcessID_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_RICcallProcessID;
asn_struct_free_f RICcallProcessID_free;
asn_struct_print_f RICcallProcessID_print;
asn_constr_check_f RICcallProcessID_constraint;
xer_type_decoder_f RICcallProcessID_decode_xer;
xer_type_encoder_f RICcallProcessID_encode_xer;
per_type_decoder_f RICcallProcessID_decode_uper;
per_type_encoder_f RICcallProcessID_encode_uper;
per_type_decoder_f RICcallProcessID_decode_aper;
per_type_encoder_f RICcallProcessID_encode_aper;

#ifdef __cplusplus
}
#endif

#endif	/* _RICcallProcessID_H_ */
#include "asn_internal.h"