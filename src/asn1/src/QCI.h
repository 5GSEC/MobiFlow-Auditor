/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_QCI_H_
#define	_QCI_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeInteger.h"

#ifdef __cplusplus
extern "C" {
#endif

/* QCI */
typedef long	 QCI_t;

/* Implementation */
extern asn_per_constraints_t asn_PER_type_QCI_constr_1;
extern asn_TYPE_descriptor_t asn_DEF_QCI;
asn_struct_free_f QCI_free;
asn_struct_print_f QCI_print;
asn_constr_check_f QCI_constraint;
xer_type_decoder_f QCI_decode_xer;
xer_type_encoder_f QCI_encode_xer;
per_type_decoder_f QCI_decode_uper;
per_type_encoder_f QCI_encode_uper;
per_type_decoder_f QCI_decode_aper;
per_type_encoder_f QCI_encode_aper;

#ifdef __cplusplus
}
#endif

#endif	/* _QCI_H_ */
#include "asn_internal.h"
