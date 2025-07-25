/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "UEID-GNB-CU-UP.h"

asn_TYPE_member_t asn_MBR_UEID_GNB_CU_UP_1[] = {
	{ ATF_NOFLAGS, 0, offsetof(struct UEID_GNB_CU_UP, gNB_CU_CP_UE_E1AP_ID),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_GNB_CU_CP_UE_E1AP_ID,
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
		"gNB-CU-CP-UE-E1AP-ID"
		},
	{ ATF_POINTER, 1, offsetof(struct UEID_GNB_CU_UP, ran_UEID),
		(ASN_TAG_CLASS_CONTEXT | (1 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_RANUEID,
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
		"ran-UEID"
		},
};
static const int asn_MAP_UEID_GNB_CU_UP_oms_1[] = { 1 };
static const ber_tlv_tag_t asn_DEF_UEID_GNB_CU_UP_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_UEID_GNB_CU_UP_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 }, /* gNB-CU-CP-UE-E1AP-ID */
    { (ASN_TAG_CLASS_CONTEXT | (1 << 2)), 1, 0, 0 } /* ran-UEID */
};
asn_SEQUENCE_specifics_t asn_SPC_UEID_GNB_CU_UP_specs_1 = {
	sizeof(struct UEID_GNB_CU_UP),
	offsetof(struct UEID_GNB_CU_UP, _asn_ctx),
	asn_MAP_UEID_GNB_CU_UP_tag2el_1,
	2,	/* Count of tags in the map */
	asn_MAP_UEID_GNB_CU_UP_oms_1,	/* Optional members */
	1, 0,	/* Root/Additions */
	2,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_UEID_GNB_CU_UP = {
	"UEID-GNB-CU-UP",
	"UEID-GNB-CU-UP",
	&asn_OP_SEQUENCE,
	asn_DEF_UEID_GNB_CU_UP_tags_1,
	sizeof(asn_DEF_UEID_GNB_CU_UP_tags_1)
		/sizeof(asn_DEF_UEID_GNB_CU_UP_tags_1[0]), /* 1 */
	asn_DEF_UEID_GNB_CU_UP_tags_1,	/* Same as above */
	sizeof(asn_DEF_UEID_GNB_CU_UP_tags_1)
		/sizeof(asn_DEF_UEID_GNB_CU_UP_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_UEID_GNB_CU_UP_1,
	2,	/* Elements count */
	&asn_SPC_UEID_GNB_CU_UP_specs_1	/* Additional specs */
};

