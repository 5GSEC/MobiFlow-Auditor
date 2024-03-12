#include <stdio.h>
#include "asn_application.h"
#include "E2AP-PDU.h"
#include "E2SM-KPMv2-IndicationMessage.h"
#include "E2SM-KPMv2-ActionDefinition.h"
#include "E2SM-KPMv2-RANfunction-Description.h"

// Function to encode ASN.1 data structure
void encode_data_structure(const char* structure_name, const char* binary_payload, size_t len) {
    // Encode the ASN.1 data structure
    // Write encoded data to stdout
    printf("Encoded data\n");
}

void decode_data_structure(const char* structure_name, const char* binary_payload, size_t len) {
    // Decode the ASN.1 data structure
    // Write decoded data to stdout
    enum asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
    asn_dec_rval_t decode_result;

    if (strcmp(structure_name, "E2AP_PDU") == 0) {
        E2AP_PDU_t * struct_ins = (E2AP_PDU_t * )calloc(1,sizeof(E2AP_PDU_t));
        decode_result = asn_decode(0, syntax, &asn_DEF_E2AP_PDU, (void **)&struct_ins, binary_payload, len);
        xer_fprint(stdout, &asn_DEF_E2AP_PDU, struct_ins);
    }
    else if (strcmp(structure_name, "E2SM_KPMv2_IndicationMessage") == 0) {
        E2SM_KPMv2_IndicationMessage_t * struct_ins = (E2SM_KPMv2_IndicationMessage_t * )calloc(1,sizeof(E2SM_KPMv2_IndicationMessage_t));
        decode_result = asn_decode(0, syntax, &asn_DEF_E2SM_KPMv2_IndicationMessage, (void **)&struct_ins, binary_payload, len);
        xer_fprint(stdout, &asn_DEF_E2SM_KPMv2_IndicationMessage, struct_ins);
    }
    else if (strcmp(structure_name, "E2SM_KPMv2_ActionDefinition") == 0) {
        E2SM_KPMv2_ActionDefinition_t * struct_ins = (E2SM_KPMv2_ActionDefinition_t * )calloc(1,sizeof(E2SM_KPMv2_ActionDefinition_t));
        decode_result = asn_decode(0, syntax, &asn_DEF_E2SM_KPMv2_ActionDefinition, (void **)&struct_ins, binary_payload, len);
        xer_fprint(stdout, &asn_DEF_E2SM_KPMv2_ActionDefinition, struct_ins);
    }
    else if (strcmp(structure_name, "E2SM_KPMv2_RANfunction_Description") == 0) {
        E2SM_KPMv2_RANfunction_Description_t * struct_ins = (E2SM_KPMv2_RANfunction_Description_t * )calloc(1,sizeof(E2SM_KPMv2_RANfunction_Description_t));
        decode_result = asn_decode(0, syntax, &asn_DEF_E2SM_KPMv2_RANfunction_Description, (void **)&struct_ins, binary_payload, len);
        xer_fprint(stdout, &asn_DEF_E2SM_KPMv2_RANfunction_Description, struct_ins);
    }
    else {
        fprintf(stderr, "Unknown structure name: %s\n", structure_name);
    }

    fprintf(stderr, "Decoded data %d\n", decode_result.code);
}

// Decode ASN.1 data structure
// void decode_data_structure(const char* structure_name, const char* binary_payload, size_t len) {
//     // Decode the ASN.1 data structure
//     // Write decoded data to stdout
//     enum asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
//     asn_dec_rval_t decode_result;

//     // Create a dictionary to map structure names to their corresponding types
//     // and definitions
//     struct {
//         const char *name;
//         asn_TYPE_descriptor_t *type;
//     } structure_mapping[] = {
//         {"E2SM_KPMv2_IndicationMessage", &asn_DEF_E2SM_KPMv2_IndicationMessage},
//         {"E2SM_KPMv2_ActionDefinition", &asn_DEF_E2SM_KPMv2_ActionDefinition},
//         {"E2SM_KPMv2_RANfunction_Description", &asn_DEF_E2SM_KPMv2_RANfunction_Description},
//     };

//     for (int i = 0; i < sizeof(structure_mapping) / sizeof(structure_mapping[0]); i++) {
//         if (strcmp(structure_name, structure_mapping[i].name) == 0) {
//             // Allocate memory for the structure instance
//             void *struct_ins = calloc(1, sizeof(structure_mapping[i].type));
//             if (struct_ins == NULL) {
//                 perror("calloc");
//                 return;
//             }

//             // Decode the structure
//             decode_result = asn_decode(0, syntax, structure_mapping[i].type, &struct_ins, binary_payload, len);
//             if (decode_result.code != RC_OK) {
//                 fprintf(stderr, "Failed to decode structure: %s, error code: %d\n", structure_mapping[i].name, decode_result.code);
//                 return;
//             }

//             // Print the decoded structure
//             xer_fprint(stdout, structure_mapping[i].type, struct_ins);

//             // Free the allocated memory
//             // ASN_STRUCT_FREE(*structure_mapping[i].type, struct_ins);
//             free(struct_ins);
//             return;
//         }
//     }

//     fprintf(stderr, "Unknown structure name: %s\n", structure_name);
// }

int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("Usage: %s <encode|decode> <structure_name> <binary_payload>\n", argv[0]);
        return 1;
    }

    const char* operation = argv[1];
    const char* structure_name = argv[2];
    const char* hex_payload = argv[3];

    // Convert hex payload to binary
    size_t hex_len = strlen(hex_payload);
    size_t bin_len = hex_len / 2;
    char* binary_payload = (char*)malloc(bin_len + 1);
    for (size_t i = 0; i < bin_len; i++) {
        sscanf(hex_payload + 2 * i, "%2hhx", &binary_payload[i]);
    }
    binary_payload[bin_len] = '\0';

    if (strcmp(operation, "encode") == 0) {
        encode_data_structure(structure_name, binary_payload, bin_len);
    } else if (strcmp(operation, "decode") == 0) {
        decode_data_structure(structure_name, binary_payload, bin_len);
    } else {
        printf("Invalid operation\n");
        return 1;
    }

    return 0;
}

