/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_NRCGI_KPMv2_H_
#define	_NRCGI_KPMv2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "PLMN-Identity-KPMv2.h"
#include "NRCellIdentity-KPMv2.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* NRCGI-KPMv2 */
typedef struct NRCGI_KPMv2 {
	PLMN_Identity_KPMv2_t	 pLMN_Identity;
	NRCellIdentity_KPMv2_t	 nRCellIdentity;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} NRCGI_KPMv2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_NRCGI_KPMv2;
extern asn_SEQUENCE_specifics_t asn_SPC_NRCGI_KPMv2_specs_1;
extern asn_TYPE_member_t asn_MBR_NRCGI_KPMv2_1[2];

#ifdef __cplusplus
}
#endif

#endif	/* _NRCGI_KPMv2_H_ */
#include "asn_internal.h"
