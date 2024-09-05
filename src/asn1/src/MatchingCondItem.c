/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.03.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "MatchingCondItem.h"

asn_TYPE_member_t asn_MBR_MatchingCondItem_1[] = {
	{ ATF_NOFLAGS, 0, offsetof(struct MatchingCondItem, matchingCondChoice),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		+1,	/* EXPLICIT tag at current level */
		&asn_DEF_MatchingCondItem_Choice,
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
		"matchingCondChoice"
		},
	{ ATF_POINTER, 1, offsetof(struct MatchingCondItem, logicalOR),
		(ASN_TAG_CLASS_CONTEXT | (1 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_LogicalOR,
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
		"logicalOR"
		},
};
static const int asn_MAP_MatchingCondItem_oms_1[] = { 1 };
static const ber_tlv_tag_t asn_DEF_MatchingCondItem_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_MatchingCondItem_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 }, /* matchingCondChoice */
    { (ASN_TAG_CLASS_CONTEXT | (1 << 2)), 1, 0, 0 } /* logicalOR */
};
asn_SEQUENCE_specifics_t asn_SPC_MatchingCondItem_specs_1 = {
	sizeof(struct MatchingCondItem),
	offsetof(struct MatchingCondItem, _asn_ctx),
	asn_MAP_MatchingCondItem_tag2el_1,
	2,	/* Count of tags in the map */
	asn_MAP_MatchingCondItem_oms_1,	/* Optional members */
	1, 0,	/* Root/Additions */
	2,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_MatchingCondItem = {
	"MatchingCondItem",
	"MatchingCondItem",
	&asn_OP_SEQUENCE,
	asn_DEF_MatchingCondItem_tags_1,
	sizeof(asn_DEF_MatchingCondItem_tags_1)
		/sizeof(asn_DEF_MatchingCondItem_tags_1[0]), /* 1 */
	asn_DEF_MatchingCondItem_tags_1,	/* Same as above */
	sizeof(asn_DEF_MatchingCondItem_tags_1)
		/sizeof(asn_DEF_MatchingCondItem_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_MatchingCondItem_1,
	2,	/* Elements count */
	&asn_SPC_MatchingCondItem_specs_1	/* Additional specs */
};

