/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.03.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_E2SM_KPM_IndicationHeader_Format1_H_
#define	_E2SM_KPM_IndicationHeader_Format1_H_


#include "asn_application.h"

/* Including external dependencies */
#include "TimeStamp.h"
#include "PrintableString.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* E2SM-KPM-IndicationHeader-Format1 */
typedef struct E2SM_KPM_IndicationHeader_Format1 {
	TimeStamp_t	 colletStartTime;
	PrintableString_t	*fileFormatversion;	/* OPTIONAL */
	PrintableString_t	*senderName;	/* OPTIONAL */
	PrintableString_t	*senderType;	/* OPTIONAL */
	PrintableString_t	*vendorName;	/* OPTIONAL */
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} E2SM_KPM_IndicationHeader_Format1_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_E2SM_KPM_IndicationHeader_Format1;
extern asn_SEQUENCE_specifics_t asn_SPC_E2SM_KPM_IndicationHeader_Format1_specs_1;
extern asn_TYPE_member_t asn_MBR_E2SM_KPM_IndicationHeader_Format1_1[5];

#ifdef __cplusplus
}
#endif

#endif	/* _E2SM_KPM_IndicationHeader_Format1_H_ */
#include "asn_internal.h"
