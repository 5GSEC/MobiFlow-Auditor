/**
    This wrapper code is dedicated for the O-RAN KPM spec
 */ 
#include <stdio.h>
#include "asn_application.h"
#include "E2AP-PDU.h"
#include "E2SM-KPM-IndicationMessage.h"
#include "E2SM-KPM-ActionDefinition.h"
#include "E2SM-KPM-RANfunction-Description.h"
#include "E2SM-KPM-ActionDefinition-Format1.h"
#include "GranularityPeriod.h"
#include "MeasurementInfoList.h"
#include "MeasurementInfoItem.h"
#include "MeasurementType.h"

void decode_data_structure(const char* structure_name, const char* hex_payload) {
     // Convert hex payload to binary
     size_t hex_len = strlen(hex_payload);
     size_t bin_len = hex_len / 2;
     char* binary_payload = (char*)malloc(bin_len + 1);
     for (size_t i = 0; i < bin_len; i++) {
         sscanf(hex_payload + 2 * i, "%2hhx", &binary_payload[i]);
     }
     binary_payload[bin_len] = '\0';

     // Decode the ASN.1 data structure
     // Write decoded data to stdout
     enum asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
     asn_dec_rval_t decode_result;

     // Create a dictionary to map structure names to their corresponding types
     // and definitions
     struct {
         const char *name;
         asn_TYPE_descriptor_t *type;
         size_t size;
     } structure_mapping[] = {
         {"E2AP_PDU", &asn_DEF_E2AP_PDU, sizeof(E2AP_PDU_t)},
         {"E2SM_KPM_IndicationMessage", &asn_DEF_E2SM_KPM_IndicationMessage, sizeof(E2SM_KPM_IndicationMessage_t)},
         {"E2SM_KPM_ActionDefinition", &asn_DEF_E2SM_KPM_ActionDefinition, sizeof(E2SM_KPM_ActionDefinition_t)},
         {"E2SM_KPM_RANfunction_Description", &asn_DEF_E2SM_KPM_RANfunction_Description, sizeof(E2SM_KPM_RANfunction_Description_t)},
     };

     for (int i = 0; i < sizeof(structure_mapping) / sizeof(structure_mapping[0]); i++) {
         if (strcmp(structure_name, structure_mapping[i].name) == 0) {
             // Allocate memory for the structure instance
             void *struct_ins = calloc(1, structure_mapping[i].size);
             if (struct_ins == NULL) {
                 perror("calloc");
                 return;
             }

             // Decode the structure
             decode_result = asn_decode(0, syntax, structure_mapping[i].type, &struct_ins, binary_payload, bin_len);
             if (decode_result.code != RC_OK) {
                 fprintf(stderr, "Failed to decode structure: %s, error code: %d\n", structure_mapping[i].name, decode_result.code);
                 return;
             }

             // Print the decoded structure
             xer_fprint(stdout, structure_mapping[i].type, struct_ins);

             // Free the allocated memory
             // ASN_STRUCT_FREE(*structure_mapping[i].type, struct_ins);
             free(struct_ins);
             return;
         }
     }

     fprintf(stderr, "Unknown structure name: %s\n", structure_name);
 }

// Function to convert binary data to hex string
char* binary_to_hex_string(const uint8_t* binary_data, size_t data_len) {
    // Allocate memory for the hex string
    char *hex_string = (char*)malloc(data_len * 2 + 1); // Two hex characters per byte, plus one for null terminator
    if (hex_string == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    // Convert each byte to hex
    for (size_t i = 0; i < data_len; i++) {
        sprintf(&hex_string[i * 2], "%02X", binary_data[i]);
    }
    hex_string[data_len * 2] = '\0'; // Null-terminate the string

    return hex_string;
}

// Function to encode action definition
void encode_action_definition(int format, long ricStyleType, long granularityPeriod, char* measList) {
    E2SM_KPM_ActionDefinition_t *actionDef = (E2SM_KPM_ActionDefinition_t *) calloc(1, sizeof(E2SM_KPM_ActionDefinition_t));
    E2SM_KPM_ActionDefinition_Format1_t *actionDefFormat1;

    if (!actionDef) {
        fprintf(stderr, "alloc RIC ActionDefinition failed\n");
        return;
    }

    // ric style
    actionDef->ric_Style_Type = ricStyleType;

    // currently only support format 1
    if (format == 1) {
        actionDefFormat1 = (E2SM_KPM_ActionDefinition_Format1_t *)calloc(1, sizeof(E2SM_KPM_ActionDefinition_Format1_t));

        // granularity period
        actionDefFormat1->granulPeriod = granularityPeriod;

        // measurement items
        MeasurementInfoItem_t* actionDefMeasInfoItem;
        int measItemSize = 0;
        const char *delimiter = ";"; // assume the delimiter is ";"
        char *token = strtok(measList, delimiter);
        while(token != NULL) {
            actionDefMeasInfoItem = (MeasurementInfoItem_t *)calloc(1, sizeof(MeasurementInfoItem_t));
            actionDefMeasInfoItem->measType.present = MeasurementType_PR_measName;
            actionDefMeasInfoItem->measType.choice.measName.buf = (uint8_t *)strdup(token);
            actionDefMeasInfoItem->measType.choice.measName.size = strlen(token);
            ASN_SEQUENCE_ADD(&actionDefFormat1->measInfoList, actionDefMeasInfoItem);
            ++measItemSize;
            token = strtok(NULL, delimiter);
        }
        actionDefFormat1->measInfoList.list.count = measItemSize;

        actionDef->actionDefinition_formats.present = E2SM_KPM_ActionDefinition__actionDefinition_formats_PR_actionDefinition_Format1;
        actionDef->actionDefinition_formats.choice.actionDefinition_Format1 = actionDefFormat1;
    }

    // encode
    uint8_t e2smbuffer[8192];
    size_t e2smbuffer_size = 8192;
    asn_enc_rval_t er = asn_encode_to_buffer(NULL, ATS_ALIGNED_BASIC_PER, &asn_DEF_E2SM_KPM_ActionDefinition,
            actionDef, e2smbuffer, e2smbuffer_size);

    if (er.encoded < 0) {
        fprintf(stderr, "Encode failure for E2SM_KPM_ActionDefinition, name=%s, tag=%s\n", er.failed_type->name, er.failed_type->xml_tag);
    }
    else {
        fprintf(stderr, "Encode successful for E2SM_KPM_ActionDefinition, encoded bytes=%ld\n", er.encoded);
        char *hex_string = binary_to_hex_string(e2smbuffer, er.encoded);
        printf("%s\n", hex_string);
        // xer_fprint(stdout, &asn_DEF_E2SM_KPM_ActionDefinition, actionDef);
    }

    free(actionDefFormat1);
    free(actionDef);
}

// Function to encode ASN.1 data structure
void encode_data_structure(const char* structure_name, const char* payload) {
    // Encode the ASN.1 data structure
    // Write encoded data to stdout
    char *copiedPayload = strdup(payload);
    if (strcmp(structure_name, "E2SM_KPM_ActionDefinition") == 0) {
        const char *delimiter = ","; // this need to be consistent with the python part...
        int index = 0;
        int format;
        long ricStyleType, granularityPeriod;
        char *measList;
        char *token = strtok(copiedPayload, delimiter);
        while(token != NULL) {
            switch (index) {
                case 0:
                    format = atoi(token);
                    break;
                case 1:
                    ricStyleType = atol(token);
                    break;
                case 2:
                    granularityPeriod = atol(token);
                    break;
                case 3:
                    measList = strdup(token);
                    break;
                default:
                    break;
            }
            ++index;
            token = strtok(NULL, delimiter);
        }
        if (index != 4) {
            fprintf(stderr, "Incorrect arg num for encoding E2SM_KPM_ActionDefinition: %d\n", index);
            return;
        }
        encode_action_definition(format, ricStyleType, granularityPeriod, measList);
    }

    free(copiedPayload);
}


int main(int argc, char *argv[]) {

    if (argc < 4) {
        printf("Usage: %s <encode|decode> <structure_name> <payload>\n", argv[0]);
        return 1;
    }

    const char* operation = argv[1];
    const char* structure_name = argv[2];
    const char* payload = argv[3];

    if (strcmp(operation, "encode") == 0) {
        encode_data_structure(structure_name, payload);
    } else if (strcmp(operation, "decode") == 0) {
        decode_data_structure(structure_name, payload);
    } else {
        printf("Invalid operation\n");
        return 1;
    }

    return 0;
}



