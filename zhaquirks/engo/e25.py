"""ENGO E25-24 Thermostat."""

from zigpy.quirks.v2.homeassistant import UnitOfTemperature
from zigpy.types import t
from zigpy.zcl.clusters.hvac import Thermostat

from zhaquirks.const import BatterySize
from zhaquirks.tuya.builder import TuyaQuirkBuilder
from zhaquirks.tuya.mcu import DPToAttributeMapping, TuyaAttributesCluster


class Preset(t.enum8):
    """Thermostat preset mode."""

    Manual = 0x00
    Schedule = 0x01
    ScheduleOverride = 0x02
    Frost = 0x03


class ControlAlgorithm(t.enum8):
    """Thermostat control algorithm."""

    TPI_UFH = 0x0
    TPI_RAD = 0x1
    TPI_ELE = 0x2
    HIS_04 = 0x3
    HIS_08 = 0x4
    HIS_12 = 0x5
    HIS_16 = 0x6
    HIS_20 = 0x8
    HIS_30 = 0x9
    HIS_40 = 0x10


class RelayMode(t.enum8):
    """Thermostat Relay Mode."""

    NO = 0x00
    NC = 0x01
    OFF = 0x02


class EngoE25Thermostat(Thermostat, TuyaAttributesCluster):
    """Engo E25 thermostat cluster."""

    _CONSTANT_ATTRIBUTES = {
        Thermostat.AttributeDefs.ctrl_sequence_of_oper.id: Thermostat.ControlSequenceOfOperation.Heating_Only
    }

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.add_unsupported_attribute(
            Thermostat.AttributeDefs.setpoint_change_source.id
        )
        self.add_unsupported_attribute(
            Thermostat.AttributeDefs.setpoint_change_source_timestamp.id
        )
        self.add_unsupported_attribute(Thermostat.AttributeDefs.pi_heating_demand.id)
        self.add_unsupported_attribute(
            Thermostat.AttributeDefs.local_temperature_calibration.id
        )


# Common quirk settings for all E25 thermostat models
def e25_base_quirk(manufacturer: str, model: str):
    return (
        TuyaQuirkBuilder(manufacturer, model)
        .tuya_switch(
            dp_id=1,
            attribute_name="state",
            translation_key="state",
            fallback_name="State",
        )
        .tuya_dp(
            dp_id=2,
            ep_attribute=EngoE25Thermostat.ep_attribute,
            attribute_name=EngoE25Thermostat.AttributeDefs.system_mode.name,
            converter=lambda x: {
                0: Thermostat.SystemMode.Heat,
                1: Thermostat.SystemMode.Cool,
            }[x],
            dp_converter=lambda x: {
                Thermostat.SystemMode.Heat: 0,
                Thermostat.SystemMode.Cool: 1,
            }[x],
        )
        .tuya_dp_multi(
            dp_id=3,
            attribute_mapping=[
                DPToAttributeMapping(
                    ep_attribute=EngoE25Thermostat.ep_attribute,
                    attribute_name=EngoE25Thermostat.AttributeDefs.running_state.name,
                    converter=lambda x: {
                        2: Thermostat.RunningState.Heat_State_On,
                        3: Thermostat.RunningState.Cool_State_On,
                        4: Thermostat.RunningState.Idle,
                        5: Thermostat.RunningState.Idle,
                    }[x],
                ),
                DPToAttributeMapping(
                    ep_attribute=EngoE25Thermostat.ep_attribute,
                    attribute_name=EngoE25Thermostat.AttributeDefs.running_mode.name,
                    converter=lambda x: {
                        2: Thermostat.RunningMode.Heat,
                        3: Thermostat.RunningMode.Cool,
                        4: Thermostat.RunningMode.Off,
                        5: Thermostat.RunningMode.Off,
                    }[x],
                ),
            ],
        )
        .tuya_dp(
            dp_id=16,
            ep_attribute=EngoE25Thermostat.ep_attribute,
            attribute_name=EngoE25Thermostat.AttributeDefs.occupied_heating_setpoint.name,
            converter=lambda x: x * 10,
            dp_converter=lambda x: x // 10,
        )
        .tuya_dp(
            dp_id=19,
            ep_attribute=EngoE25Thermostat.ep_attribute,
            attribute_name=EngoE25Thermostat.AttributeDefs.max_heat_setpoint_limit.name,
            converter=lambda x: x * 10,
            dp_converter=lambda x: x // 10,
        )
        .tuya_dp(
            dp_id=24,
            ep_attribute=EngoE25Thermostat.ep_attribute,
            attribute_name=EngoE25Thermostat.AttributeDefs.local_temperature.name,
            converter=lambda x: x * 10,
        )
        .tuya_dp(
            dp_id=26,
            ep_attribute=EngoE25Thermostat.ep_attribute,
            attribute_name=EngoE25Thermostat.AttributeDefs.min_heat_setpoint_limit.name,
            converter=lambda x: x * 10,
            dp_converter=lambda x: x // 10,
        )
        .tuya_number(
            dp_id=27,
            attribute_name="temperature_calibration",
            translation_key="temperature_calibration",
            fallback_name="Temperature Calibration",
            type=t.int8s,
            unit="°C",
            min_value=-10.0,
            max_value=10.0,
            multiplier=0.1,
            step=0.1,
        )
        .tuya_switch(
            dp_id=40,
            attribute_name="child_lock",
            translation_key="child_lock",
            fallback_name="Child lock",
        )
        .tuya_number(
            dp_id=44,
            attribute_name="backlight_mode",
            translation_key="backlight_mode",
            fallback_name="Backlight mode",
            type=t.uint16_t,
            unit="%",
            min_value=0.0,
            max_value=100.0,
            multiplier=1.0,
            step=10,
        )
        .tuya_enum(
            dp_id=58,
            attribute_name="preset",
            enum_class=Preset,
            translation_key="preset",
            fallback_name="Preset",
        )
        .tuya_enum(
            dp_id=101,
            attribute_name="control_algorithm",
            enum_class=ControlAlgorithm,
            translation_key="control_algorithm",
            fallback_name="Control Algorithm",
        )
        .tuya_switch(
            dp_id=107,
            attribute_name="valve_protection",
            translation_key="valve_protection",
            fallback_name="Valve Protection",
        )
        .tuya_enchantment(True, True)
    )


(
    # 24 Volt mains powered variant
    e25_base_quirk("_TZE204_cmyc8g5i", "TS0601")
    .tuya_enum(
        dp_id=108,
        attribute_name="relay_mode",
        enum_class=RelayMode,
        translation_key="relay_mode",
        fallback_name="Relay Mode",
    )
    .tuya_number(
        dp_id=106,
        attribute_name="frost_protection_setpoint",
        type=t.uint16_t,
        unit=UnitOfTemperature.CELSIUS,
        min_value=5.0,
        max_value=17.0,
        multiplier=0.1,
        step=0.5,
        translation_key="frost_protection_setpoint",
        fallback_name="Frost Protection Setpoint",
    )
    .friendly_name(manufacturer="Engo", model="E25-24 Thermostat")
    .adds(EngoE25Thermostat)
    .skip_configuration()
    # This could also be applied to the 230V variant
    .add_to_registry()
)

(
    # Battery powered variant
    e25_base_quirk("_TZE204_cg8hdnjv", "TS0601")
    .tuya_battery(35, battery_type=BatterySize.AA, battery_qty=2)
    .friendly_name(manufacturer="Engo", model="E25-BAT Thermostat")
    .adds(EngoE25Thermostat)
    .skip_configuration()
    .add_to_registry()
)

