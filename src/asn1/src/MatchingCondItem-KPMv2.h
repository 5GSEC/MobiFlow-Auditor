/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_MatchingCondItem_KPMv2_H_
#define	_MatchingCondItem_KPMv2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "constr_CHOICE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum MatchingCondItem_KPMv2_PR {
	MatchingCondItem_KPMv2_PR_NOTHING,	/* No components present */
	MatchingCondItem_KPMv2_PR_measLabel,
	MatchingCondItem_KPMv2_PR_testCondInfo
	/* Extensions may appear below */
	
} MatchingCondItem_KPMv2_PR;

/* Forward declarations */
struct MeasurementLabel_KPMv2;
struct TestCondInfo_KPMv2;

/* MatchingCondItem-KPMv2 */
typedef struct MatchingCondItem_KPMv2 {
	MatchingCondItem_KPMv2_PR present;
	union MatchingCondItem_KPMv2_u {
		struct MeasurementLabel_KPMv2	*measLabel;
		struct TestCondInfo_KPMv2	*testCondInfo;
		/*
		 * This type is extensible,
		 * possible extensions are below.
		 */
	} choice;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} MatchingCondItem_KPMv2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_MatchingCondItem_KPMv2;
extern asn_CHOICE_specifics_t asn_SPC_MatchingCondItem_KPMv2_specs_1;
extern asn_TYPE_member_t asn_MBR_MatchingCondItem_KPMv2_1[2];
extern asn_per_constraints_t asn_PER_type_MatchingCondItem_KPMv2_constr_1;

#ifdef __cplusplus
}
#endif

#endif	/* _MatchingCondItem_KPMv2_H_ */
#include "asn_internal.h"
