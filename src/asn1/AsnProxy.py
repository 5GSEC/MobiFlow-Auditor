import subprocess
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

# Generic ASN proxy for decoding / encoding ASN data structures
class AsnProxy(ABC):

    def __init__(self, path_wrapper_c_exec):
        self.wrapper_path = path_wrapper_c_exec

    def encode_asn_struct(self, structure_name: str, hex_str: str) -> str:
        # Call the C program with the specified operation, structure name, and payload
        # operation = "encode"
        # result = subprocess.run([self.wrapper_path, operation, structure_name, hex_str], capture_output=True, text=True)
        # # Return the result
        raise NotImplementedError

    def decode_asn_struct(self, structure_name: str, hex_str: str) -> dict:
        # Call the C program with the specified operation, structure name, and payload
        operation = "decode"
        result = subprocess.run([self.wrapper_path, operation, structure_name, hex_str], capture_output=True, text=True)
        # Return the result
        xml_str = result.stdout.strip()
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

    def element_to_dict(self, element) -> dict:
        # Initialize the dictionary to store the element's tag, text, and children
        result = {
            element.tag: element.text.strip() if element.text is not None and element.text.strip() != "" else [
                self. element_to_dict(child) for child in element],
        }

        return result
