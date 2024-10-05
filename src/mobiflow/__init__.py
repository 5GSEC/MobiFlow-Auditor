from .encoding import decode_rrc_msg, decode_nas_msg
from .constant import *

mobiflow_ver = "v2" # TODO populate this field to config

if mobiflow_ver == "v1":
    from .mobiflow import UE, BS, UEMobiFlow, BSMobiFlow
    from .factbase import FactBase
elif mobiflow_ver == "v2":
    from .mobiflow_v2 import UE, BS, UEMobiFlow, BSMobiFlow, parse_measurement_into_mobiflow
    from .factbase_v2 import FactBase
