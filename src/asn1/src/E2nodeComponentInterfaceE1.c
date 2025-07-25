/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2AP-IEs"
 * 	found in "asn1/e2ap_v2.asn1"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "E2nodeComponentInterfaceE1.h"

asn_TYPE_member_t asn_MBR_E2nodeComponentInterfaceE1_1[] = {
	{ ATF_NOFLAGS, 0, offsetof(struct E2nodeComponentInterfaceE1, gNB_CU_CP_ID),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_E2AP_IEs_GNB_CU_UP_ID,
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
		"gNB-CU-CP-ID"
		},
};
static const ber_tlv_tag_t asn_DEF_E2nodeComponentInterfaceE1_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_E2nodeComponentInterfaceE1_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 } /* gNB-CU-CP-ID */
};
asn_SEQUENCE_specifics_t asn_SPC_E2nodeComponentInterfaceE1_specs_1 = {
	sizeof(struct E2nodeComponentInterfaceE1),
	offsetof(struct E2nodeComponentInterfaceE1, _asn_ctx),
	asn_MAP_E2nodeComponentInterfaceE1_tag2el_1,
	1,	/* Count of tags in the map */
	0, 0, 0,	/* Optional elements (not needed) */
	1,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_E2nodeComponentInterfaceE1 = {
	"E2nodeComponentInterfaceE1",
	"E2nodeComponentInterfaceE1",
	&asn_OP_SEQUENCE,
	asn_DEF_E2nodeComponentInterfaceE1_tags_1,
	sizeof(asn_DEF_E2nodeComponentInterfaceE1_tags_1)
		/sizeof(asn_DEF_E2nodeComponentInterfaceE1_tags_1[0]), /* 1 */
	asn_DEF_E2nodeComponentInterfaceE1_tags_1,	/* Same as above */
	sizeof(asn_DEF_E2nodeComponentInterfaceE1_tags_1)
		/sizeof(asn_DEF_E2nodeComponentInterfaceE1_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_E2nodeComponentInterfaceE1_1,
	1,	/* Elements count */
	&asn_SPC_E2nodeComponentInterfaceE1_specs_1	/* Additional specs */
};

