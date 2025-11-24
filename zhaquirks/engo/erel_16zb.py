from zigpy.device import zha
from zhaquirks.tuya.builder import TuyaQuirkBuilder


(
    TuyaQuirkBuilder("_TZ3218_sfjr4fnz", "TS0002")
    .replaces_endpoint(1, device_type=zha.DeviceType.ON_OFF_SWITCH)
    .add_to_registry()
)
