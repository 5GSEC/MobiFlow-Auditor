/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.03.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_MeasurementInfo_Action_List_H_
#define	_MeasurementInfo_Action_List_H_


#include "asn_application.h"

/* Including external dependencies */
#include "asn_SEQUENCE_OF.h"
#include "constr_SEQUENCE_OF.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declarations */
struct MeasurementInfo_Action_Item;

/* MeasurementInfo-Action-List */
typedef struct MeasurementInfo_Action_List {
	A_SEQUENCE_OF(struct MeasurementInfo_Action_Item) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} MeasurementInfo_Action_List_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_MeasurementInfo_Action_List;
extern asn_SET_OF_specifics_t asn_SPC_MeasurementInfo_Action_List_specs_1;
extern asn_TYPE_member_t asn_MBR_MeasurementInfo_Action_List_1[1];
extern asn_per_constraints_t asn_PER_type_MeasurementInfo_Action_List_constr_1;

#ifdef __cplusplus
}
#endif

#endif	/* _MeasurementInfo_Action_List_H_ */
#include "asn_internal.h"
