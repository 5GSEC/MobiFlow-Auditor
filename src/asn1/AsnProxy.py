import os
import json
import subprocess
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

# Generic ASN proxy for decoding / encoding ASN data structures
class AsnProxy(ABC):

    def __init__(self, path_wrapper_c_exec, path_cp_wrapper_c_exec=None):
        self.wrapper_path = path_wrapper_c_exec
        # E2SM-CP has its own executable (wrapper_cp.c), next to wrapper by default
        if path_cp_wrapper_c_exec is None:
            path_cp_wrapper_c_exec = os.path.join(os.path.dirname(path_wrapper_c_exec), "wrapper_cp")
        self.cp_wrapper_path = path_cp_wrapper_c_exec
        self.last_error = ""  # stderr of the last failed E2SM-CP wrapper call

    def encode_asn_struct(self, structure_name: str, hex_str: str) -> str:
        # Call the C program with the specified operation, structure name, and payload
        operation = "encode"
        result = subprocess.run([self.wrapper_path, operation, structure_name, hex_str], capture_output=True, text=True)
        return str(result.stdout.strip())

    def decode_asn_struct(self, structure_name: str, hex_str: str) -> dict:
        # Call the C program with the specified operation, structure name, and payload
        operation = "decode"
        result = subprocess.run([self.wrapper_path, operation, structure_name, hex_str], capture_output=True, text=True)
        # Return the result
        xml_str = result.stdout.strip()
        if len(xml_str.strip()) == 0:
            return None
        return self.element_to_dict(ET.fromstring(xml_str))

    @abstractmethod
    def decode_e2ap_pdu(self, hex_payload: str):
        pass

    @abstractmethod
    def encode_e2ap_pdu(self, hex_payload: str):
        pass

    @abstractmethod
    def decode_e2sm_kpm_indication_message(self, hex_payload: str):
        pass

    @abstractmethod
    def encode_e2sm_kpm_indication_message(self, hex_payload: str):
        pass

    @abstractmethod
    def decode_e2sm_kpm_action_definition(self, hex_payload: str):
        pass

    @abstractmethod
    def encode_e2sm_kpm_action_definition(self, hex_payload: str):
        pass

    @abstractmethod
    def decode_e2sm_kpm_ran_function_definition(self, hex_payload: str):
        pass

    @abstractmethod
    def encode_e2sm_kpm_ran_function_definition(self, hex_payload: str):
        pass

    # ------------------------------------------------------------------
    # E2SM-CP (MobiFlow control plane telemetry). The encoding does not
    # depend on the RIC platform, so these are common to every proxy.
    # Decoders return a dict (see wrapper_cp.c for the layout) or None,
    # encoders a hex string or None; on failure, last_error says why.
    # ------------------------------------------------------------------

    def _run_cp_wrapper(self, operation: str, structure_name: str, payload: str):
        try:
            result = subprocess.run([self.cp_wrapper_path, operation, structure_name, payload],
                                    capture_output=True, text=True)
        except OSError as e:
            self.last_error = f"{self.cp_wrapper_path}: {e}"
            return None
        if result.returncode != 0 or not result.stdout.strip():
            self.last_error = result.stderr.strip() or f"{structure_name}: no output"
            return None
        return result.stdout.strip()

    def _decode_cp_struct(self, structure_name: str, hex_payload: str):
        out = self._run_cp_wrapper("decode", structure_name, hex_payload)
        if out is None:
            return None
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            self.last_error = f"{structure_name}: invalid wrapper output: {e}"
            return None

    def decode_e2sm_cp_ran_function_definition(self, hex_payload: str):
        return self._decode_cp_struct("E2SM_CP_RANFunctionDefinition", hex_payload)

    def decode_e2sm_cp_indication_header(self, hex_payload: str):
        return self._decode_cp_struct("E2SM_CP_IndicationHeader", hex_payload)

    def decode_e2sm_cp_indication_message(self, hex_payload: str):
        return self._decode_cp_struct("E2SM_CP_IndicationMessage", hex_payload)

    def encode_e2sm_cp_event_trigger(self, max_batch_size: int = 0, max_batch_delay_ms: int = 0):
        """Event trigger format 1 (upon event); a limit of 0 is left out."""
        return self._run_cp_wrapper("encode", "E2SM_CP_EventTrigger",
                                    f"{int(max_batch_size)},{int(max_batch_delay_ms)}")

    def encode_e2sm_cp_action_definition(self, ric_style_type: int, attribute_ids=None, include_opaque=None):
        """Action definition format 1. attribute_ids: the attributes to report
        (None or empty: all); include_opaque: None leaves the E2 node default."""
        opaque = -1 if include_opaque is None else int(bool(include_opaque))
        attrs = ";".join(str(int(a)) for a in (attribute_ids or []))
        return self._run_cp_wrapper("encode", "E2SM_CP_ActionDefinition",
                                    f"{int(ric_style_type)},{opaque},{attrs}")

    def element_to_dict(self, element) -> dict:
        result = None
        try:
            # Initialize the dictionary to store the element's tag, text, and children
            result = {
                element.tag: element.text.strip() if element.text is not None and element.text.strip() != "" else [
                    self. element_to_dict(child) for child in element],
            }
        except ET.ParseError as e:
            return None

        return result

