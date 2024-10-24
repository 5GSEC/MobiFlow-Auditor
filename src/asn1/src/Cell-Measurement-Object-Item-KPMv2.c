/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2SM-KPM-IEs"
 * 	found in "asn1/e2sm_kpm_v2.0.3-changed.asn"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#include "Cell-Measurement-Object-Item-KPMv2.h"

asn_TYPE_member_t asn_MBR_Cell_Measurement_Object_Item_KPMv2_1[] = {
	{ ATF_NOFLAGS, 0, offsetof(struct Cell_Measurement_Object_Item_KPMv2, cell_object_ID),
		(ASN_TAG_CLASS_CONTEXT | (0 << 2)),
		-1,	/* IMPLICIT tag at current level */
		&asn_DEF_CellObjectID_KPMv2,
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
		"cell-object-ID"
		},
	{ ATF_NOFLAGS, 0, offsetof(struct Cell_Measurement_Object_Item_KPMv2, cell_global_ID),
		(ASN_TAG_CLASS_CONTEXT | (1 << 2)),
		+1,	/* EXPLICIT tag at current level */
		&asn_DEF_CellGlobalID_KPMv2,
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
		"cell-global-ID"
		},
};
static const ber_tlv_tag_t asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1[] = {
	(ASN_TAG_CLASS_UNIVERSAL | (16 << 2))
};
static const asn_TYPE_tag2member_t asn_MAP_Cell_Measurement_Object_Item_KPMv2_tag2el_1[] = {
    { (ASN_TAG_CLASS_CONTEXT | (0 << 2)), 0, 0, 0 }, /* cell-object-ID */
    { (ASN_TAG_CLASS_CONTEXT | (1 << 2)), 1, 0, 0 } /* cell-global-ID */
};
asn_SEQUENCE_specifics_t asn_SPC_Cell_Measurement_Object_Item_KPMv2_specs_1 = {
	sizeof(struct Cell_Measurement_Object_Item_KPMv2),
	offsetof(struct Cell_Measurement_Object_Item_KPMv2, _asn_ctx),
	asn_MAP_Cell_Measurement_Object_Item_KPMv2_tag2el_1,
	2,	/* Count of tags in the map */
	0, 0, 0,	/* Optional elements (not needed) */
	2,	/* First extension addition */
};
asn_TYPE_descriptor_t asn_DEF_Cell_Measurement_Object_Item_KPMv2 = {
	"Cell-Measurement-Object-Item-KPMv2",
	"Cell-Measurement-Object-Item-KPMv2",
	&asn_OP_SEQUENCE,
	asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1,
	sizeof(asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1)
		/sizeof(asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1[0]), /* 1 */
	asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1,	/* Same as above */
	sizeof(asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1)
		/sizeof(asn_DEF_Cell_Measurement_Object_Item_KPMv2_tags_1[0]), /* 1 */
	{
#if !defined(ASN_DISABLE_OER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_OER_SUPPORT) */
#if !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT)
		0,
#endif  /* !defined(ASN_DISABLE_UPER_SUPPORT) || !defined(ASN_DISABLE_APER_SUPPORT) */
		SEQUENCE_constraint
	},
	asn_MBR_Cell_Measurement_Object_Item_KPMv2_1,
	2,	/* Elements count */
	&asn_SPC_Cell_Measurement_Object_Item_KPMv2_specs_1	/* Additional specs */
};
