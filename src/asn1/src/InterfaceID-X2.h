/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_InterfaceID_X2_H_
#define	_InterfaceID_X2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "constr_CHOICE.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum InterfaceID_X2__nodeType_PR {
	InterfaceID_X2__nodeType_PR_NOTHING,	/* No components present */
	InterfaceID_X2__nodeType_PR_global_eNB_ID,
	InterfaceID_X2__nodeType_PR_global_en_gNB_ID
	/* Extensions may appear below */
	
} InterfaceID_X2__nodeType_PR;

/* Forward declarations */
struct GlobalENB_ID;
struct GlobalenGNB_ID;

/* InterfaceID-X2 */
typedef struct InterfaceID_X2 {
	struct InterfaceID_X2__nodeType {
		InterfaceID_X2__nodeType_PR present;
		union InterfaceID_X2__nodeType_u {
			struct GlobalENB_ID	*global_eNB_ID;
			struct GlobalenGNB_ID	*global_en_gNB_ID;
			/*
			 * This type is extensible,
			 * possible extensions are below.
			 */
		} choice;
		
		/* Context for parsing across buffer boundaries */
		asn_struct_ctx_t _asn_ctx;
	} nodeType;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} InterfaceID_X2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_InterfaceID_X2;
extern asn_SEQUENCE_specifics_t asn_SPC_InterfaceID_X2_specs_1;
extern asn_TYPE_member_t asn_MBR_InterfaceID_X2_1[1];

#ifdef __cplusplus
}
#endif

#endif	/* _InterfaceID_X2_H_ */
#include "asn_internal.h"
