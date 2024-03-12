/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_TestCond_Type_KPMv2_H_
#define	_TestCond_Type_KPMv2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeEnumerated.h"
#include "constr_CHOICE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum TestCond_Type_KPMv2_PR {
	TestCond_Type_KPMv2_PR_NOTHING,	/* No components present */
	TestCond_Type_KPMv2_PR_gBR,
	TestCond_Type_KPMv2_PR_aMBR,
	TestCond_Type_KPMv2_PR_isStat,
	TestCond_Type_KPMv2_PR_isCatM,
	TestCond_Type_KPMv2_PR_rSRP,
	TestCond_Type_KPMv2_PR_rSRQ
	/* Extensions may appear below */
	
} TestCond_Type_KPMv2_PR;
typedef enum TestCond_Type_KPMv2__gBR {
	TestCond_Type_KPMv2__gBR_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__gBR;
typedef enum TestCond_Type_KPMv2__aMBR {
	TestCond_Type_KPMv2__aMBR_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__aMBR;
typedef enum TestCond_Type_KPMv2__isStat {
	TestCond_Type_KPMv2__isStat_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__isStat;
typedef enum TestCond_Type_KPMv2__isCatM {
	TestCond_Type_KPMv2__isCatM_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__isCatM;
typedef enum TestCond_Type_KPMv2__rSRP {
	TestCond_Type_KPMv2__rSRP_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__rSRP;
typedef enum TestCond_Type_KPMv2__rSRQ {
	TestCond_Type_KPMv2__rSRQ_true	= 0
	/*
	 * Enumeration is extensible
	 */
} e_TestCond_Type_KPMv2__rSRQ;

/* TestCond-Type-KPMv2 */
typedef struct TestCond_Type_KPMv2 {
	TestCond_Type_KPMv2_PR present;
	union TestCond_Type_KPMv2_u {
		long	 gBR;
		long	 aMBR;
		long	 isStat;
		long	 isCatM;
		long	 rSRP;
		long	 rSRQ;
		/*
		 * This type is extensible,
		 * possible extensions are below.
		 */
	} choice;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} TestCond_Type_KPMv2_t;

/* Implementation */
/* extern asn_TYPE_descriptor_t asn_DEF_gBR_2;	// (Use -fall-defs-global to expose) */
/* extern asn_TYPE_descriptor_t asn_DEF_aMBR_5;	// (Use -fall-defs-global to expose) */
/* extern asn_TYPE_descriptor_t asn_DEF_isStat_8;	// (Use -fall-defs-global to expose) */
/* extern asn_TYPE_descriptor_t asn_DEF_isCatM_11;	// (Use -fall-defs-global to expose) */
/* extern asn_TYPE_descriptor_t asn_DEF_rSRP_14;	// (Use -fall-defs-global to expose) */
/* extern asn_TYPE_descriptor_t asn_DEF_rSRQ_17;	// (Use -fall-defs-global to expose) */
extern asn_TYPE_descriptor_t asn_DEF_TestCond_Type_KPMv2;
extern asn_CHOICE_specifics_t asn_SPC_TestCond_Type_KPMv2_specs_1;
extern asn_TYPE_member_t asn_MBR_TestCond_Type_KPMv2_1[6];
extern asn_per_constraints_t asn_PER_type_TestCond_Type_KPMv2_constr_1;

#ifdef __cplusplus
}
#endif

#endif	/* _TestCond_Type_KPMv2_H_ */
#include "asn_internal.h"
