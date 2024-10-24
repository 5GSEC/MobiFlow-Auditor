/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_RIC_EventTriggerStyle_Item_KPMv2_H_
#define	_RIC_EventTriggerStyle_Item_KPMv2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "RIC-Style-Type-KPMv2.h"
#include "RIC-Style-Name-KPMv2.h"
#include "RIC-Format-Type-KPMv2.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* RIC-EventTriggerStyle-Item-KPMv2 */
typedef struct RIC_EventTriggerStyle_Item_KPMv2 {
	RIC_Style_Type_KPMv2_t	 ric_EventTriggerStyle_Type;
	RIC_Style_Name_KPMv2_t	 ric_EventTriggerStyle_Name;
	RIC_Format_Type_KPMv2_t	 ric_EventTriggerFormat_Type;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} RIC_EventTriggerStyle_Item_KPMv2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_RIC_EventTriggerStyle_Item_KPMv2;
extern asn_SEQUENCE_specifics_t asn_SPC_RIC_EventTriggerStyle_Item_KPMv2_specs_1;
extern asn_TYPE_member_t asn_MBR_RIC_EventTriggerStyle_Item_KPMv2_1[3];

#ifdef __cplusplus
}
#endif

#endif	/* _RIC_EventTriggerStyle_Item_KPMv2_H_ */
#include "asn_internal.h"
