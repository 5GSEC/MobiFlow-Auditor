/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_GlobalENB_ID_H_
#define	_GlobalENB_ID_H_


#include "asn_application.h"

/* Including external dependencies */
#include "PLMNIdentity.h"
#include "ENB-ID.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* GlobalENB-ID */
typedef struct GlobalENB_ID {
	PLMNIdentity_t	 pLMNIdentity;
	ENB_ID_t	 eNB_ID;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} GlobalENB_ID_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_GlobalENB_ID;
extern asn_SEQUENCE_specifics_t asn_SPC_GlobalENB_ID_specs_1;
extern asn_TYPE_member_t asn_MBR_GlobalENB_ID_1[2];

#ifdef __cplusplus
}
#endif

#endif	/* _GlobalENB_ID_H_ */
#include "asn_internal.h"
