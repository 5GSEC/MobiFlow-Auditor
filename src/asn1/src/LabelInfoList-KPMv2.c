/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "LabelInfoList-KPMv2.h"

#include "LabelInfoItem-KPMv2.h"
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
asn_per_constraints_t asn_PER_type_LabelInfoList_KPMv2_constr_1 CC_NOTUSED = {
	{ APC_UNCONSTRAINED,	-1, -1,  0,  0 },
	{ APC_CONSTRAINED,	 31, -1,  1,  2147483647 }	/* (SIZE(1..2147483647)) */,
	0, 0	/* No PER value map */
};
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
asn_TYPE_member_t asn_MBR_LabelInfoList_KPMv2_1[] = {
	{ ATF_POINTER, 0, 0,
		(ASN_TAG_CLASS_UNIVERSAL | (16 << 2)),
		0,
		&asn_DEF_LabelInfoItem_KPMv2,
		0,
		{
#if !defined(ASN_DISABLE_OER_SUPPORT)
			0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
			0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
			0
		},
		0, 0, /* No default value */
		""
		},
};
static const ber_tlv_tag_t asn_DEF_LabelInfoList_KPMv2_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
asn_SET_OF_specifics_t asn_SPC_LabelInfoList_KPMv2_specs_1 = {
	sizeof(struct LabelInfoList_KPMv2),
	offsetof(struct LabelInfoList_KPMv2, _asn_ctx),
	0,	/* XER encoding is XMLDelimitedItemList */
};
asn_TYPE_descriptor_t asn_DEF_LabelInfoList_KPMv2 = {
	"LabelInfoList-KPMv2",
	"LabelInfoList-KPMv2",
	&asn_OP_SEQUENCE_OF,
	asn_DEF_LabelInfoList_KPMv2_tags_1,
	sizeof(asn_DEF_LabelInfoList_KPMv2_tags_1)
		/sizeof(asn_DEF_LabelInfoList_KPMv2_tags_1[0]), /* 1 */
	asn_DEF_LabelInfoList_KPMv2_tags_1,	/* Same as above */
	sizeof(asn_DEF_LabelInfoList_KPMv2_tags_1)
		/sizeof(asn_DEF_LabelInfoList_KPMv2_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		&asn_PER_type_LabelInfoList_KPMv2_constr_1,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_OF_constraint
	},
	asn_MBR_LabelInfoList_KPMv2_1,
	1,	/* Single element */
	&asn_SPC_LabelInfoList_KPMv2_specs_1	/* Additional specs */
};

