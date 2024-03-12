/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_E2SM_KPMv2_IndicationMessage_Format2_H_
#define	_E2SM_KPMv2_IndicationMessage_Format2_H_


#include "asn_application.h"

/* Including external dependencies */
#include "SubscriptionID-KPMv2.h"
#include "CellObjectID-KPMv2.h"
#include "GranularityPeriod-KPMv2.h"
#include "MeasurementCondUEidList-KPMv2.h"
#include "MeasurementData-KPMv2.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* E2SM-KPMv2-IndicationMessage-Format2 */
typedef struct E2SM_KPMv2_IndicationMessage_Format2 {
	SubscriptionID_KPMv2_t	 subscriptID;
	CellObjectID_KPMv2_t	*cellObjID;	/* OPTIONAL */
	GranularityPeriod_KPMv2_t	*granulPeriod;	/* OPTIONAL */
	MeasurementCondUEidList_KPMv2_t	 measCondUEidList;
	MeasurementData_KPMv2_t	 measData;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} E2SM_KPMv2_IndicationMessage_Format2_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_E2SM_KPMv2_IndicationMessage_Format2;
extern asn_SEQUENCE_specifics_t asn_SPC_E2SM_KPMv2_IndicationMessage_Format2_specs_1;
extern asn_TYPE_member_t asn_MBR_E2SM_KPMv2_IndicationMessage_Format2_1[5];

#ifdef __cplusplus
}
#endif

#endif	/* _E2SM_KPMv2_IndicationMessage_Format2_H_ */
#include "asn_internal.h"
