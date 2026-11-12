/**
 * ASN.1 wrapper for the E2SM-CP service model (MobiFlow control plane
 * telemetry, OID 1.3.6.1.4.1.32473.1.1.2.1). Built from the sources in
 * e2sm_cp/ (asn1_compile_cp.sh) into its own executable, wrapper_cp, so its
 * types never clash with the E2AP / E2SM-KPM ones of wrapper.
 *
 * Usage: wrapper_cp <encode|decode> <structure_name> <payload>
 *
 *   decode E2SM_CP_RANFunctionDefinition <hex>
 *   decode E2SM_CP_IndicationHeader      <hex>
 *   decode E2SM_CP_IndicationMessage     <hex>
 *       print the structure as one JSON object on stdout
 *
 *   encode E2SM_CP_EventTrigger     "<max_batch_size>,<max_batch_delay_ms>"
 *       format 1 (upon event); 0 leaves a limit out (report each event at once)
 *   encode E2SM_CP_ActionDefinition "<ric_style_type>,<include_opaque>,<attribute_ids>"
 *       format 1; include_opaque -1 (absent: E2 node default), 0 or 1;
 *       attribute_ids ";"-separated (empty: all attributes)
 *       print the APER encoding as hex on stdout
 *
 * On failure nothing is printed on stdout, the reason goes to stderr and the
 * exit status is 1.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <stdint.h>

#include "asn_application.h"
#include "E2SM_CP_E2SM-CP-RANFunctionDefinition.h"
#include "E2SM_CP_RIC-EventTriggerStyle-Item.h"
#include "E2SM_CP_RIC-ReportStyle-Item.h"
#include "E2SM_CP_AttributeDefinition.h"
#include "E2SM_CP_E2SM-CP-EventTrigger.h"
#include "E2SM_CP_E2SM-CP-EventTrigger-Format1.h"
#include "E2SM_CP_E2SM-CP-ActionDefinition.h"
#include "E2SM_CP_E2SM-CP-ActionDefinition-Format1.h"
#include "E2SM_CP_E2SM-CP-IndicationHeader.h"
#include "E2SM_CP_E2SM-CP-IndicationHeader-Format1.h"
#include "E2SM_CP_E2SM-CP-IndicationMessage.h"
#include "E2SM_CP_E2SM-CP-IndicationMessage-Format1.h"
#include "E2SM_CP_UEEventGroup.h"
#include "E2SM_CP_UE-Reference.h"
#include "E2SM_CP_Event.h"
#include "E2SM_CP_MessageLayer.h"
#include "E2SM_CP_Attribute.h"
#include "E2SM_CP_MessageID.h"
#include "E2SM_CP_InterfaceMessage-ID.h"
#include "E2SM_CP_RRC-MessageID.h"
#include "E2SM_CP_NAS-MessageID.h"
#include "E2SM_CP_OpaqueMessage-ID.h"
#include "E2SM_CP_CGI.h"
#include "E2SM_CP_NR-CGI.h"
#include "E2SM_CP_EUTRA-CGI.h"

#define BUF_SIZE 65536

static int fail(const char *fmt, const char *arg) {
    fprintf(stderr, "wrapper_cp: ");
    fprintf(stderr, fmt, arg);
    fprintf(stderr, "\n");
    return 1;
}

/* hex string -> bytes; characters other than hex digits (spaces, newlines)
 * are skipped. Returns the byte count, or -1 on an odd number of digits. */
static long hex_to_bin(const char *hex, uint8_t **out) {
    size_t cap = strlen(hex) / 2 + 1, n = 0;
    uint8_t *buf = malloc(cap);
    int hi = -1;
    if (!buf) return -1;
    for (const char *p = hex; *p; ++p) {
        int v;
        if (!isxdigit((unsigned char)*p)) continue;
        v = isdigit((unsigned char)*p) ? *p - '0' : tolower((unsigned char)*p) - 'a' + 10;
        if (hi < 0) {
            hi = v;
        } else {
            buf[n++] = (uint8_t)(hi << 4 | v);
            hi = -1;
        }
    }
    if (hi >= 0) {
        free(buf);
        return -1;
    }
    *out = buf;
    return (long)n;
}

static void print_hex(const uint8_t *buf, size_t len) {
    for (size_t i = 0; i < len; ++i) printf("%02X", buf[i]);
    printf("\n");
}

/* ------------------------------------------------------------------ */
/* JSON output (minimal, ASCII-safe)                                   */
/* ------------------------------------------------------------------ */

static void json_str(const uint8_t *buf, size_t len) {
    putchar('"');
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = buf[i];
        if (c == '"' || c == '\\') printf("\\%c", c);
        else if (c < 0x20 || c > 0x7e) printf("\\u%04x", c);
        else putchar(c);
    }
    putchar('"');
}

static void json_hex(const uint8_t *buf, size_t len) {
    putchar('"');
    for (size_t i = 0; i < len; ++i) printf("%02x", buf[i]);
    putchar('"');
}

#define JSON_OS(os) json_str((os).buf, (os).size)

static void print_cgi(const E2SM_CP_CGI_t *c) {
    uint64_t id = 0;
    const BIT_STRING_t *bits;
    if (c->present == E2SM_CP_CGI_PR_nR_CGI) {
        printf("{\"plmn\":");
        json_hex(c->choice.nR_CGI->pLMNIdentity.buf, c->choice.nR_CGI->pLMNIdentity.size);
        bits = &c->choice.nR_CGI->nRCellIdentity;
        printf(",\"nr_cell_id\":");
    } else if (c->present == E2SM_CP_CGI_PR_eUTRA_CGI) {
        printf("{\"plmn\":");
        json_hex(c->choice.eUTRA_CGI->pLMNIdentity.buf, c->choice.eUTRA_CGI->pLMNIdentity.size);
        bits = &c->choice.eUTRA_CGI->eUTRACellIdentity;
        printf(",\"eutra_cell_id\":");
    } else {
        printf("null");
        return;
    }
    for (size_t i = 0; i < bits->size; ++i)
        id = id << 8 | bits->buf[i];
    printf("%llu}", (unsigned long long)(id >> bits->bits_unused));
}

static void print_message_id(const E2SM_CP_MessageID_t *m) {
    switch (m->present) {
    case E2SM_CP_MessageID_PR_interfaceMessage:
        printf("{\"interface\":%ld,\"procedure\":%ld,\"outcome\":%ld}",
               m->choice.interfaceMessage->interfaceType,
               m->choice.interfaceMessage->messageID.interfaceProcedureID,
               m->choice.interfaceMessage->messageID.messageType);
        break;
    case E2SM_CP_MessageID_PR_rrcMessage: {
        const E2SM_CP_RRC_MessageID_t *r = m->choice.rrcMessage;
        if (r->rrcType.present == E2SM_CP_RRC_MessageID__rrcType_PR_nR)
            printf("{\"rrc_nr_class\":%ld,\"rrc_msg\":%ld}", r->rrcType.choice.nR, r->messageID);
        else
            printf("{\"rrc_lte_class\":%ld,\"rrc_msg\":%ld}", r->rrcType.choice.lTE, r->messageID);
        break;
    }
    case E2SM_CP_MessageID_PR_nasMessage:
        printf("{\"nas_epd\":%ld,\"nas_msg\":%ld}", m->choice.nasMessage->protocolDiscriminator,
               m->choice.nasMessage->messageType);
        break;
    case E2SM_CP_MessageID_PR_opaqueMessage: {
        const E2SM_CP_OpaqueMessage_ID_t *o = m->choice.opaqueMessage;
        printf("{\"opaque_protocol\":%ld,\"reason\":%ld", o->protocol, o->reason);
        if (o->rrcClass) printf(",\"rrc_nr_class\":%ld", *o->rrcClass);
        printf("}");
        break;
    }
    default:
        printf("null");
    }
}

static void print_attribute_value(const E2SM_CP_AttributeValue_t *v) {
    switch (v->present) {
    case E2SM_CP_AttributeValue_PR_valueBoolean:
        printf(v->choice.valueBoolean ? "true" : "false");
        break;
    case E2SM_CP_AttributeValue_PR_valueInt:
        printf("%ld", v->choice.valueInt);
        break;
    case E2SM_CP_AttributeValue_PR_valueReal:
        if (isfinite(v->choice.valueReal)) printf("%.17g", v->choice.valueReal);
        else printf("null");
        break;
    case E2SM_CP_AttributeValue_PR_valuePrintableString:
        JSON_OS(v->choice.valuePrintableString);
        break;
    case E2SM_CP_AttributeValue_PR_valueOctS:
        json_hex(v->choice.valueOctS.buf, v->choice.valueOctS.size);
        break;
    case E2SM_CP_AttributeValue_PR_valueBitS:
        json_hex(v->choice.valueBitS.buf, v->choice.valueBitS.size);
        break;
    default:
        printf("null");
    }
}

/* ------------------------------------------------------------------ */
/* decode                                                              */
/* ------------------------------------------------------------------ */

static void print_ran_function_definition(const E2SM_CP_E2SM_CP_RANFunctionDefinition_t *d) {
    printf("{\"short_name\":");
    JSON_OS(d->ranFunction_Name.ranFunction_ShortName);
    printf(",\"oid\":");
    JSON_OS(d->ranFunction_Name.ranFunction_E2SM_OID);
    printf(",\"description\":");
    JSON_OS(d->ranFunction_Name.ranFunction_Description);
    if (d->ranFunction_Name.ranFunction_Instance)
        printf(",\"instance\":%ld", *d->ranFunction_Name.ranFunction_Instance);
    printf(",\"schema_version\":");
    JSON_OS(d->schemaVersion);

    printf(",\"event_trigger_styles\":[");
    for (int i = 0; i < d->ric_EventTriggerStyle_List.list.count; ++i) {
        const E2SM_CP_RIC_EventTriggerStyle_Item_t *s = d->ric_EventTriggerStyle_List.list.array[i];
        printf("%s{\"type\":%ld,\"name\":", i ? "," : "", s->ric_EventTriggerStyle_Type);
        JSON_OS(s->ric_EventTriggerStyle_Name);
        printf(",\"format\":%ld}", s->ric_EventTriggerFormat_Type);
    }

    printf("],\"report_styles\":[");
    for (int i = 0; i < d->ric_ReportStyle_List.list.count; ++i) {
        const E2SM_CP_RIC_ReportStyle_Item_t *s = d->ric_ReportStyle_List.list.array[i];
        printf("%s{\"type\":%ld,\"name\":", i ? "," : "", s->ric_ReportStyle_Type);
        JSON_OS(s->ric_ReportStyle_Name);
        printf(",\"event_trigger_styles\":[");
        for (int j = 0; j < s->ric_SupportedEventTriggerStyle_List.list.count; ++j)
            printf("%s%ld", j ? "," : "", *s->ric_SupportedEventTriggerStyle_List.list.array[j]);
        printf("],\"action_format\":%ld,\"header_format\":%ld,\"message_format\":%ld}",
               s->ric_ActionFormat_Type, s->ric_IndicationHeaderFormat_Type,
               s->ric_IndicationMessageFormat_Type);
    }

    printf("],\"attributes\":[");
    for (int i = 0; i < d->attributeDefinition_List.list.count; ++i) {
        const E2SM_CP_AttributeDefinition_t *a = d->attributeDefinition_List.list.array[i];
        printf("%s{\"id\":%ld,\"name\":", i ? "," : "", a->attributeID);
        JSON_OS(a->attributeName);
        printf(",\"type\":%ld,\"stability\":%ld", a->valueType, a->stability);
        if (a->unit) {
            printf(",\"unit\":");
            JSON_OS(*a->unit);
        }
        if (a->description) {
            printf(",\"description\":");
            JSON_OS(*a->description);
        }
        printf("}");
    }
    printf("]");

    if (d->supportedMessage_List) {
        printf(",\"supported_messages\":[");
        for (int i = 0; i < d->supportedMessage_List->list.count; ++i) {
            if (i) printf(",");
            print_message_id(d->supportedMessage_List->list.array[i]);
        }
        printf("]");
    }
    printf("}\n");
}

static int print_indication_header(const E2SM_CP_E2SM_CP_IndicationHeader_t *h) {
    const E2SM_CP_E2SM_CP_IndicationHeader_Format1_t *f;
    if (h->ric_indicationHeader_formats.present !=
            E2SM_CP_E2SM_CP_IndicationHeader__ric_indicationHeader_formats_PR_indicationHeader_Format1)
        return fail("unsupported %s format", "E2SM_CP_IndicationHeader");
    f = h->ric_indicationHeader_formats.choice.indicationHeader_Format1;
    printf("{\"format\":1,\"collection_start_time\":");
    json_hex(f->collectionStartTime.buf, f->collectionStartTime.size);
    printf(",\"schema_version\":");
    JSON_OS(f->schemaVersion);
    printf(",\"first_seq\":%lu,\"dropped\":%lu", f->firstSequenceNumber, f->droppedEventCount);
    if (f->cell_List) {
        printf(",\"cells\":[");
        for (int i = 0; i < f->cell_List->list.count; ++i) {
            if (i) printf(",");
            print_cgi(f->cell_List->list.array[i]);
        }
        printf("]");
    }
    printf("}\n");
    return 0;
}

static void print_ue_reference(const E2SM_CP_UE_Reference_t *u) {
    printf("{\"ran_ue_id\":");
    json_hex(u->ranUEID.buf, u->ranUEID.size);
    if (u->gNB_DU_ID) {
        uint64_t v = 0;
        asn_INTEGER2uint64(u->gNB_DU_ID, &v);
        printf(",\"gnb_du_id\":%llu", (unsigned long long)v);
    }
    if (u->gNB_DU_UE_F1AP_ID) printf(",\"gnb_du_ue_f1ap_id\":%lu", *u->gNB_DU_UE_F1AP_ID);
    if (u->gNB_CU_UE_F1AP_ID) printf(",\"gnb_cu_ue_f1ap_id\":%lu", *u->gNB_CU_UE_F1AP_ID);
    if (u->c_RNTI) printf(",\"c_rnti\":%ld", *u->c_RNTI);
    printf("}");
}

static int print_indication_message(const E2SM_CP_E2SM_CP_IndicationMessage_t *m) {
    const E2SM_CP_E2SM_CP_IndicationMessage_Format1_t *f;
    if (m->ric_indicationMessage_formats.present !=
            E2SM_CP_E2SM_CP_IndicationMessage__ric_indicationMessage_formats_PR_indicationMessage_Format1)
        return fail("unsupported %s format", "E2SM_CP_IndicationMessage");
    f = m->ric_indicationMessage_formats.choice.indicationMessage_Format1;
    printf("{\"format\":1,\"groups\":[");
    for (int g = 0; g < f->ueEventGroup_List.list.count; ++g) {
        const E2SM_CP_UEEventGroup_t *ug = f->ueEventGroup_List.list.array[g];
        printf("%s{", g ? "," : "");
        if (ug->ueReference) {
            printf("\"ue\":");
            print_ue_reference(ug->ueReference);
            printf(",");
        }
        if (ug->cellGlobalID) {
            printf("\"cell\":");
            print_cgi(ug->cellGlobalID);
            printf(",");
        }
        printf("\"events\":[");
        for (int e = 0; e < ug->event_List.list.count; ++e) {
            const E2SM_CP_Event_t *ev = ug->event_List.list.array[e];
            printf("%s{\"seq\":%lu,\"time_offset_us\":%lu,\"direction\":%ld,\"layers\":[",
                   e ? "," : "", ev->sequenceNumber, ev->timeOffset, ev->direction);
            for (int l = 0; l < ev->messageLayer_List.list.count; ++l) {
                const E2SM_CP_MessageLayer_t *ml = ev->messageLayer_List.list.array[l];
                printf("%s{\"msg\":", l ? "," : "");
                print_message_id(&ml->messageID);
                if (ml->protection) printf(",\"protection\":%ld", *ml->protection);
                if (ml->attribute_List) {
                    printf(",\"attrs\":{");
                    for (int k = 0; k < ml->attribute_List->list.count; ++k) {
                        const E2SM_CP_Attribute_t *a = ml->attribute_List->list.array[k];
                        printf("%s\"%ld\":", k ? "," : "", a->attributeID);
                        print_attribute_value(&a->attributeValue);
                    }
                    printf("}");
                }
                printf("}");
            }
            printf("]}");
        }
        printf("]}");
    }
    printf("]}\n");
    return 0;
}

static int decode_data_structure(const char *structure_name, const char *hex_payload) {
    static const struct {
        const char *name;
        asn_TYPE_descriptor_t *type;
    } types[] = {
        {"E2SM_CP_RANFunctionDefinition", &asn_DEF_E2SM_CP_E2SM_CP_RANFunctionDefinition},
        {"E2SM_CP_IndicationHeader", &asn_DEF_E2SM_CP_E2SM_CP_IndicationHeader},
        {"E2SM_CP_IndicationMessage", &asn_DEF_E2SM_CP_E2SM_CP_IndicationMessage},
    };
    asn_TYPE_descriptor_t *td = NULL;
    uint8_t *bin = NULL;
    void *s = NULL;
    asn_dec_rval_t rv;
    long len;
    int rc = 0;

    for (size_t i = 0; i < sizeof(types) / sizeof(types[0]); ++i)
        if (strcmp(structure_name, types[i].name) == 0)
            td = types[i].type;
    if (!td)
        return fail("unknown structure name: %s", structure_name);
    if ((len = hex_to_bin(hex_payload, &bin)) < 0)
        return fail("invalid hex payload for %s", structure_name);

    rv = aper_decode_complete(NULL, td, &s, bin, (size_t)len);
    if (rv.code != RC_OK) {
        rc = fail("failed to decode %s", structure_name);
    } else if (td == &asn_DEF_E2SM_CP_E2SM_CP_RANFunctionDefinition) {
        print_ran_function_definition(s);
    } else if (td == &asn_DEF_E2SM_CP_E2SM_CP_IndicationHeader) {
        rc = print_indication_header(s);
    } else {
        rc = print_indication_message(s);
    }
    ASN_STRUCT_FREE(*td, s);
    free(bin);
    return rc;
}

/* ------------------------------------------------------------------ */
/* encode                                                              */
/* ------------------------------------------------------------------ */

static int encode_and_print(asn_TYPE_descriptor_t *td, void *s) {
    static uint8_t buf[BUF_SIZE];
    char errbuf[256];
    size_t errlen = sizeof(errbuf);
    asn_enc_rval_t er;

    if (asn_check_constraints(td, s, errbuf, &errlen) != 0) {
        fprintf(stderr, "wrapper_cp: %s constraint violation: %s\n", td->name, errbuf);
        return 1;
    }
    er = asn_encode_to_buffer(NULL, ATS_ALIGNED_BASIC_PER, td, s, buf, sizeof(buf));
    if (er.encoded < 0 || (size_t)er.encoded > sizeof(buf))
        return fail("failed to encode %s", td->name);
    print_hex(buf, (size_t)er.encoded);
    return 0;
}

/* split "a,b,c" into at most n fields (empty fields kept) */
static int split_fields(char *s, char **fields, int n) {
    int count = 0;
    while (count < n) {
        fields[count++] = s;
        s = strchr(s, ',');
        if (!s) break;
        *s++ = '\0';
    }
    return s ? -1 : count;
}

static int encode_event_trigger(char *payload) {
    char *f[2];
    E2SM_CP_E2SM_CP_EventTrigger_t *et;
    E2SM_CP_E2SM_CP_EventTrigger_Format1_t *f1;
    long batch_size, batch_delay;
    int rc;

    if (split_fields(payload, f, 2) != 2)
        return fail("expected \"<max_batch_size>,<max_batch_delay_ms>\" for %s", "E2SM_CP_EventTrigger");
    batch_size = atol(f[0]);
    batch_delay = atol(f[1]);

    et = calloc(1, sizeof(*et));
    f1 = calloc(1, sizeof(*f1));
    et->ric_eventTrigger_formats.present = E2SM_CP_E2SM_CP_EventTrigger__ric_eventTrigger_formats_PR_eventTrigger_Format1;
    et->ric_eventTrigger_formats.choice.eventTrigger_Format1 = f1;
    if (batch_size > 0) {
        f1->maxBatchSize = calloc(1, sizeof(*f1->maxBatchSize));
        *f1->maxBatchSize = batch_size;
    }
    if (batch_delay > 0) {
        f1->maxBatchDelay = calloc(1, sizeof(*f1->maxBatchDelay));
        *f1->maxBatchDelay = (unsigned long)batch_delay;
    }
    rc = encode_and_print(&asn_DEF_E2SM_CP_E2SM_CP_EventTrigger, et);
    ASN_STRUCT_FREE(asn_DEF_E2SM_CP_E2SM_CP_EventTrigger, et);
    return rc;
}

static int encode_action_definition(char *payload) {
    char *f[3];
    E2SM_CP_E2SM_CP_ActionDefinition_t *ad;
    E2SM_CP_E2SM_CP_ActionDefinition_Format1_t *f1;
    int opaque, rc;

    if (split_fields(payload, f, 3) != 3)
        return fail("expected \"<ric_style_type>,<include_opaque>,<attribute_ids>\" for %s",
                    "E2SM_CP_ActionDefinition");
    opaque = atoi(f[1]);

    ad = calloc(1, sizeof(*ad));
    f1 = calloc(1, sizeof(*f1));
    ad->ric_Style_Type = atol(f[0]);
    ad->ric_actionDefinition_formats.present =
        E2SM_CP_E2SM_CP_ActionDefinition__ric_actionDefinition_formats_PR_actionDefinition_Format1;
    ad->ric_actionDefinition_formats.choice.actionDefinition_Format1 = f1;
    for (char *tok = strtok(f[2], ";"); tok; tok = strtok(NULL, ";")) {
        E2SM_CP_AttributeID_t *id;
        if (!f1->attributeID_List)
            f1->attributeID_List = calloc(1, sizeof(*f1->attributeID_List));
        id = calloc(1, sizeof(*id));
        ASN_SEQUENCE_ADD(&f1->attributeID_List->list, id);
        *id = atol(tok);
    }
    if (opaque >= 0) {
        f1->includeOpaqueMessages = calloc(1, sizeof(*f1->includeOpaqueMessages));
        *f1->includeOpaqueMessages = opaque ? 1 : 0;
    }
    rc = encode_and_print(&asn_DEF_E2SM_CP_E2SM_CP_ActionDefinition, ad);
    ASN_STRUCT_FREE(asn_DEF_E2SM_CP_E2SM_CP_ActionDefinition, ad);
    return rc;
}

static int encode_data_structure(const char *structure_name, const char *payload) {
    char *copy = strdup(payload);
    int rc;
    if (strcmp(structure_name, "E2SM_CP_EventTrigger") == 0)
        rc = encode_event_trigger(copy);
    else if (strcmp(structure_name, "E2SM_CP_ActionDefinition") == 0)
        rc = encode_action_definition(copy);
    else
        rc = fail("unknown structure name: %s", structure_name);
    free(copy);
    return rc;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <encode|decode> <structure_name> <payload>\n", argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "encode") == 0)
        return encode_data_structure(argv[2], argv[3]);
    if (strcmp(argv[1], "decode") == 0)
        return decode_data_structure(argv[2], argv[3]);
    fprintf(stderr, "Invalid operation: %s\n", argv[1]);
    return 1;
}
