/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "E2AP-Containers"
 * 	found in "asn1/e2ap_v2.asn1"
 * 	`asn1c -gen-APER -gen-UPER -no-gen-JER -no-gen-BER -no-gen-OER -fcompound-names -no-gen-example -findirect-choice -fno-include-deps -fincludes-quoted -D src`
 */

#ifndef	_ProtocolIE_Container_H_
#define	_ProtocolIE_Container_H_


#include "asn_application.h"

/* Including external dependencies */
#include "asn_SEQUENCE_OF.h"
#include "constr_SEQUENCE_OF.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declarations */
struct RICsubscriptionRequest_IEs;
struct RICsubscriptionResponse_IEs;
struct RICsubscriptionFailure_IEs;
struct RICsubscriptionDeleteRequest_IEs;
struct RICsubscriptionDeleteResponse_IEs;
struct RICsubscriptionDeleteFailure_IEs;
struct RICsubscriptionDeleteRequired_IEs;
struct RICindication_IEs;
struct RICcontrolRequest_IEs;
struct RICcontrolAcknowledge_IEs;
struct RICcontrolFailure_IEs;
struct ErrorIndication_IEs;
struct E2setupRequestIEs;
struct E2setupResponseIEs;
struct E2setupFailureIEs;
struct E2connectionUpdate_IEs;
struct E2connectionUpdateAck_IEs;
struct E2connectionUpdateFailure_IEs;
struct E2nodeConfigurationUpdate_IEs;
struct E2nodeConfigurationUpdateAcknowledge_IEs;
struct E2nodeConfigurationUpdateFailure_IEs;
struct ResetRequestIEs;
struct ResetResponseIEs;
struct RICserviceUpdate_IEs;
struct RICserviceUpdateAcknowledge_IEs;
struct RICserviceUpdateFailure_IEs;
struct RICserviceQuery_IEs;

/* ProtocolIE-Container */
typedef struct ProtocolIE_Container_1909P0 {
	A_SEQUENCE_OF(struct RICsubscriptionRequest_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P0_t;
typedef struct ProtocolIE_Container_1909P1 {
	A_SEQUENCE_OF(struct RICsubscriptionResponse_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P1_t;
typedef struct ProtocolIE_Container_1909P2 {
	A_SEQUENCE_OF(struct RICsubscriptionFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P2_t;
typedef struct ProtocolIE_Container_1909P3 {
	A_SEQUENCE_OF(struct RICsubscriptionDeleteRequest_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P3_t;
typedef struct ProtocolIE_Container_1909P4 {
	A_SEQUENCE_OF(struct RICsubscriptionDeleteResponse_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P4_t;
typedef struct ProtocolIE_Container_1909P5 {
	A_SEQUENCE_OF(struct RICsubscriptionDeleteFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P5_t;
typedef struct ProtocolIE_Container_1909P6 {
	A_SEQUENCE_OF(struct RICsubscriptionDeleteRequired_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P6_t;
typedef struct ProtocolIE_Container_1909P7 {
	A_SEQUENCE_OF(struct RICindication_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P7_t;
typedef struct ProtocolIE_Container_1909P8 {
	A_SEQUENCE_OF(struct RICcontrolRequest_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P8_t;
typedef struct ProtocolIE_Container_1909P9 {
	A_SEQUENCE_OF(struct RICcontrolAcknowledge_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P9_t;
typedef struct ProtocolIE_Container_1909P10 {
	A_SEQUENCE_OF(struct RICcontrolFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P10_t;
typedef struct ProtocolIE_Container_1909P11 {
	A_SEQUENCE_OF(struct ErrorIndication_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P11_t;
typedef struct ProtocolIE_Container_1909P12 {
	A_SEQUENCE_OF(struct E2setupRequestIEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P12_t;
typedef struct ProtocolIE_Container_1909P13 {
	A_SEQUENCE_OF(struct E2setupResponseIEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P13_t;
typedef struct ProtocolIE_Container_1909P14 {
	A_SEQUENCE_OF(struct E2setupFailureIEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P14_t;
typedef struct ProtocolIE_Container_1909P15 {
	A_SEQUENCE_OF(struct E2connectionUpdate_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P15_t;
typedef struct ProtocolIE_Container_1909P16 {
	A_SEQUENCE_OF(struct E2connectionUpdateAck_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P16_t;
typedef struct ProtocolIE_Container_1909P17 {
	A_SEQUENCE_OF(struct E2connectionUpdateFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P17_t;
typedef struct ProtocolIE_Container_1909P18 {
	A_SEQUENCE_OF(struct E2nodeConfigurationUpdate_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P18_t;
typedef struct ProtocolIE_Container_1909P19 {
	A_SEQUENCE_OF(struct E2nodeConfigurationUpdateAcknowledge_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P19_t;
typedef struct ProtocolIE_Container_1909P20 {
	A_SEQUENCE_OF(struct E2nodeConfigurationUpdateFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P20_t;
typedef struct ProtocolIE_Container_1909P21 {
	A_SEQUENCE_OF(struct ResetRequestIEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P21_t;
typedef struct ProtocolIE_Container_1909P22 {
	A_SEQUENCE_OF(struct ResetResponseIEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P22_t;
typedef struct ProtocolIE_Container_1909P23 {
	A_SEQUENCE_OF(struct RICserviceUpdate_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P23_t;
typedef struct ProtocolIE_Container_1909P24 {
	A_SEQUENCE_OF(struct RICserviceUpdateAcknowledge_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P24_t;
typedef struct ProtocolIE_Container_1909P25 {
	A_SEQUENCE_OF(struct RICserviceUpdateFailure_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P25_t;
typedef struct ProtocolIE_Container_1909P26 {
	A_SEQUENCE_OF(struct RICserviceQuery_IEs) list;
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} ProtocolIE_Container_1909P26_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P0;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P0_specs_1;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P0_1[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P0_constr_1;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P1;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P1_specs_3;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P1_3[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P1_constr_3;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P2;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P2_specs_5;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P2_5[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P2_constr_5;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P3;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P3_specs_7;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P3_7[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P3_constr_7;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P4;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P4_specs_9;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P4_9[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P4_constr_9;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P5;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P5_specs_11;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P5_11[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P5_constr_11;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P6;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P6_specs_13;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P6_13[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P6_constr_13;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P7;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P7_specs_15;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P7_15[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P7_constr_15;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P8;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P8_specs_17;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P8_17[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P8_constr_17;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P9;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P9_specs_19;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P9_19[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P9_constr_19;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P10;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P10_specs_21;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P10_21[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P10_constr_21;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P11;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P11_specs_23;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P11_23[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P11_constr_23;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P12;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P12_specs_25;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P12_25[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P12_constr_25;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P13;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P13_specs_27;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P13_27[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P13_constr_27;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P14;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P14_specs_29;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P14_29[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P14_constr_29;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P15;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P15_specs_31;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P15_31[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P15_constr_31;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P16;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P16_specs_33;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P16_33[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P16_constr_33;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P17;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P17_specs_35;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P17_35[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P17_constr_35;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P18;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P18_specs_37;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P18_37[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P18_constr_37;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P19;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P19_specs_39;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P19_39[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P19_constr_39;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P20;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P20_specs_41;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P20_41[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P20_constr_41;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P21;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P21_specs_43;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P21_43[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P21_constr_43;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P22;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P22_specs_45;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P22_45[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P22_constr_45;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P23;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P23_specs_47;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P23_47[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P23_constr_47;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P24;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P24_specs_49;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P24_49[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P24_constr_49;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P25;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P25_specs_51;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P25_51[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P25_constr_51;
extern asn_TYPE_descriptor_t asn_DEF_ProtocolIE_Container_1909P26;
extern asn_SET_OF_specifics_t asn_SPC_ProtocolIE_Container_1909P26_specs_53;
extern asn_TYPE_member_t asn_MBR_ProtocolIE_Container_1909P26_53[1];
extern asn_per_constraints_t asn_PER_type_ProtocolIE_Container_1909P26_constr_53;

#ifdef __cplusplus
}
#endif

#endif	/* _ProtocolIE_Container_H_ */
#include "asn_internal.h"
