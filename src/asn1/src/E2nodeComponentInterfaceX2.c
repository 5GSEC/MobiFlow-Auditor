/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2AP-IEs"
 * 	found in "asn1/e2ap_v2.asn1"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "E2nodeComponentInterfaceX2.h"

#include "E2AP-IEs_GlobalENB-ID.h"
#include "E2AP-IEs_GlobalenGNB-ID.h"
asn_TYPE_member_t asn_MBR_E2nodeComponentInterfaceX2_1[] = {
	{ ATF_POINTER, 2, offsetof(struct E2nodeComponentInterfaceX2, global_eNB_ID),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_E2AP_IEs_GlobalENB_ID,
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
		"global-eNB-ID"
		},
	{ ATF_POINTER, 1, offsetof(struct E2nodeComponentInterfaceX2, global_en_gNB_ID),
		(ASN_TAG_CLASS_CONTEXT | (1 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_E2AP_IEs_GlobalenGNB_ID,
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
		"global-en-gNB-ID"
		},
};
static const int asn_MAP_E2nodeComponentInterfaceX2_oms_1[] = { 0, 1 };
static const ber_tlv_tag_t asn_DEF_E2nodeComponentInterfaceX2_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_E2nodeComponentInterfaceX2_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 }, /* global-eNB-ID */
    { (ASN_TAG_CLASS_CONTEXT | (1 << 2)), 1, 0, 0 } /* global-en-gNB-ID */
};
asn_SEQUENCE_specifics_t asn_SPC_E2nodeComponentInterfaceX2_specs_1 = {
	sizeof(struct E2nodeComponentInterfaceX2),
	offsetof(struct E2nodeComponentInterfaceX2, _asn_ctx),
	asn_MAP_E2nodeComponentInterfaceX2_tag2el_1,
	2,	/* Count of tags in the map */
	asn_MAP_E2nodeComponentInterfaceX2_oms_1,	/* Optional members */
	2, 0,	/* Root/Additions */
	2,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_E2nodeComponentInterfaceX2 = {
	"E2nodeComponentInterfaceX2",
	"E2nodeComponentInterfaceX2",
	&asn_OP_SEQUENCE,
	asn_DEF_E2nodeComponentInterfaceX2_tags_1,
	sizeof(asn_DEF_E2nodeComponentInterfaceX2_tags_1)
		/sizeof(asn_DEF_E2nodeComponentInterfaceX2_tags_1[0]), /* 1 */
	asn_DEF_E2nodeComponentInterfaceX2_tags_1,	/* Same as above */
	sizeof(asn_DEF_E2nodeComponentInterfaceX2_tags_1)
		/sizeof(asn_DEF_E2nodeComponentInterfaceX2_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_E2nodeComponentInterfaceX2_1,
	2,	/* Elements count */
	&asn_SPC_E2nodeComponentInterfaceX2_specs_1	/* Additional specs */
};

