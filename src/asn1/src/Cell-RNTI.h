/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_Cell_RNTI_H_
#define	_Cell_RNTI_H_


#include "asn_application.h"

/* Including external dependencies */
#include "RNTI-Value.h"
#include "CGI.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Cell-RNTI */
typedef struct Cell_RNTI {
	RNTI_Value_t	 c_RNTI;
	CGI_t	 cell_Global_ID;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} Cell_RNTI_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_Cell_RNTI;
extern asn_SEQUENCE_specifics_t asn_SPC_Cell_RNTI_specs_1;
extern asn_TYPE_member_t asn_MBR_Cell_RNTI_1[2];

#ifdef __cplusplus
}
#endif

#endif	/* _Cell_RNTI_H_ */
#include "asn_internal.h"
