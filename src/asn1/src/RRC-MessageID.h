/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_RRC_MessageID_H_
#define	_RRC_MessageID_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeInteger.h"
#include "RRCclass-LTE.h"
#include "RRCclass-NR.h"
#include "constr_CHOICE.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum RRC_MessageID__rrcType_PR {
	RRC_MessageID__rrcType_PR_NOTHING,	/* No components present */
	RRC_MessageID__rrcType_PR_lTE,
	RRC_MessageID__rrcType_PR_nR
	/* Extensions may appear below */
	
} RRC_MessageID__rrcType_PR;

/* RRC-MessageID */
typedef struct RRC_MessageID {
	struct RRC_MessageID__rrcType {
		RRC_MessageID__rrcType_PR present;
		union RRC_MessageID__rrcType_u {
			RRCclass_LTE_t	 lTE;
			RRCclass_NR_t	 nR;
			/*
			 * This type is extensible,
			 * possible extensions are below.
			 */
		} choice;
		
		/* Context for parsing across buffer boundaries */
		asn_struct_ctx_t _asn_ctx;
	} rrcType;
	long	 messageID;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} RRC_MessageID_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_RRC_MessageID;

#ifdef __cplusplus
}
#endif

#endif	/* _RRC_MessageID_H_ */
#include "asn_internal.h"
