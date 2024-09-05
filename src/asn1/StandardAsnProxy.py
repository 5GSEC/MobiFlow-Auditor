from .AsnProxy import AsnProxy

# ASN proxy for decoding / encoding O-RAN compliant related ASN data structures
class StandardAsnProxy(AsnProxy):

    def __init__(self, path_wrapper_c_exec):
        super().__init__(path_wrapper_c_exec)

    def decode_e2ap_pdu(self, hex_payload: str):
        return self.decode_asn_struct("E2AP_PDU", hex_payload)

    def encode_e2ap_pdu(self, hex_payload: str):
        return self.encode_asn_struct("E2AP_PDU", hex_payload)

    def decode_e2sm_kpm_indication_message(self, hex_payload: str):
        return self.decode_asn_struct("E2SM_KPM_IndicationMessage", hex_payload)

    def encode_e2sm_kpm_indication_message(self, hex_payload: str):
        return self.encode_asn_struct("E2SM_KPM_IndicationMessage", hex_payload)

    def decode_e2sm_kpm_action_definition(self, hex_payload: str):
        return self.decode_asn_struct("E2SM_KPM_ActionDefinition", hex_payload)

    def encode_e2sm_kpm_action_definition(self, hex_payload: str):
        return self.encode_asn_struct("E2SM_KPM_ActionDefinition", hex_payload)

    def decode_e2sm_kpm_ran_function_definition(self, hex_payload: str):
        return self.decode_asn_struct("E2SM_KPM_RANfunction_Description", hex_payload)

    def encode_e2sm_kpm_ran_function_definition(self, hex_payload: str):
        return self.encode_asn_struct("E2SM_KPM_RANfunction_Description", hex_payload)
