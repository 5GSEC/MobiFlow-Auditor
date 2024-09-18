/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-COMMON-IEs"
 * 	found in "asn1/e2sm_v3.00.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "UEID-ENB.h"

#include "E2SM-COMMON-IEs_GlobalENB-ID.h"
#include "Cell-RNTI.h"
asn_TYPE_member_t asn_MBR_UEID_ENB_1[] = {
	{ ATF_NOFLAGS, 0, offsetof(struct UEID_ENB, mME_UE_S1AP_ID),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_MME_UE_S1AP_ID,
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
		"mME-UE-S1AP-ID"
		},
	{ ATF_NOFLAGS, 0, offsetof(struct UEID_ENB, gUMMEI),
		(ASN_TAG_CLASS_CONTEXT | (1 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_GUMMEI,
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
		"gUMMEI"
		},
	{ ATF_POINTER, 4, offsetof(struct UEID_ENB, m_eNB_UE_X2AP_ID),
		(ASN_TAG_CLASS_CONTEXT | (2 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_ENB_UE_X2AP_ID,
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
		"m-eNB-UE-X2AP-ID"
		},
	{ ATF_POINTER, 3, offsetof(struct UEID_ENB, m_eNB_UE_X2AP_ID_Extension),
		(ASN_TAG_CLASS_CONTEXT | (3 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_ENB_UE_X2AP_ID_Extension,
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
		"m-eNB-UE-X2AP-ID-Extension"
		},
	{ ATF_POINTER, 2, offsetof(struct UEID_ENB, globalENB_ID),
		(ASN_TAG_CLASS_CONTEXT | (4 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_E2SM_COMMON_IEs_GlobalENB_ID,
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
		"globalENB-ID"
		},
	{ ATF_POINTER, 1, offsetof(struct UEID_ENB, cell_RNTI),
		(ASN_TAG_CLASS_CONTEXT | (5 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_Cell_RNTI,
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
		"cell-RNTI"
		},
};
static const int asn_MAP_UEID_ENB_oms_1[] = { 2, 3, 4, 5 };
static const ber_tlv_tag_t asn_DEF_UEID_ENB_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_UEID_ENB_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 }, /* mME-UE-S1AP-ID */
    { (ASN_TAG_CLASS_CONTEXT | (1 << 2)), 1, 0, 0 }, /* gUMMEI */
    { (ASN_TAG_CLASS_CONTEXT | (2 << 2)), 2, 0, 0 }, /* m-eNB-UE-X2AP-ID */
    { (ASN_TAG_CLASS_CONTEXT | (3 << 2)), 3, 0, 0 }, /* m-eNB-UE-X2AP-ID-Extension */
    { (ASN_TAG_CLASS_CONTEXT | (4 << 2)), 4, 0, 0 }, /* globalENB-ID */
    { (ASN_TAG_CLASS_CONTEXT | (5 << 2)), 5, 0, 0 } /* cell-RNTI */
};
asn_SEQUENCE_specifics_t asn_SPC_UEID_ENB_specs_1 = {
	sizeof(struct UEID_ENB),
	offsetof(struct UEID_ENB, _asn_ctx),
	asn_MAP_UEID_ENB_tag2el_1,
	6,	/* Count of tags in the map */
	asn_MAP_UEID_ENB_oms_1,	/* Optional members */
	3, 1,	/* Root/Additions */
	5,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_UEID_ENB = {
	"UEID-ENB",
	"UEID-ENB",
	&asn_OP_SEQUENCE,
	asn_DEF_UEID_ENB_tags_1,
	sizeof(asn_DEF_UEID_ENB_tags_1)
		/sizeof(asn_DEF_UEID_ENB_tags_1[0]), /* 1 */
	asn_DEF_UEID_ENB_tags_1,	/* Same as above */
	sizeof(asn_DEF_UEID_ENB_tags_1)
		/sizeof(asn_DEF_UEID_ENB_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_UEID_ENB_1,
	6,	/* Elements count */
	&asn_SPC_UEID_ENB_specs_1	/* Additional specs */
};
