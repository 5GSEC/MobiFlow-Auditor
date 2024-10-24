/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_GNB_ID_Choice_KPMv2_H_
#define	_GNB_ID_Choice_KPMv2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "BIT_STRING.h"
#include "constr_CHOICE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum GNB_ID_Choice_KPMv2_PR {
	GNB_ID_Choice_KPMv2_PR_NOTHING,	/* No components present */
	GNB_ID_Choice_KPMv2_PR_gnb_ID
	/* Extensions may appear below */
	
} GNB_ID_Choice_KPMv2_PR;

/* GNB-ID-Choice-KPMv2 */
typedef struct GNB_ID_Choice_KPMv2 {
	GNB_ID_Choice_KPMv2_PR present;
	union GNB_ID_Choice_KPMv2_u {
		BIT_STRING_t	 gnb_ID;
		/*
		 * This type is extensible,
		 * possible extensions are below.
		 */
	} choice;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} GNB_ID_Choice_KPMv2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_GNB_ID_Choice_KPMv2;
extern asn_CHOICE_specifics_t asn_SPC_GNB_ID_Choice_KPMv2_specs_1;
extern asn_TYPE_member_t asn_MBR_GNB_ID_Choice_KPMv2_1[1];
extern asn_per_constraints_t asn_PER_type_GNB_ID_Choice_KPMv2_constr_1;

#ifdef __cplusplus
}
#endif

#endif	/* _GNB_ID_Choice_KPMv2_H_ */
#include "asn_internal.h"