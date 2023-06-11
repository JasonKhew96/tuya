"""Support for Tuya select."""
from __future__ import annotations

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantTuyaData
from .base import TuyaEntity
from .const import DOMAIN, TUYA_DISCOVERY_NEW, DPCode, DPType

# Commonly used, that are re-used in the select down below.
LANGUAGE_SELECT: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key=DPCode.LANGUAGE,
        name="Language",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:translate",
        entity_registry_enabled_default=False,
        translation_key="language",
    ),
)


# All descriptions can be found here. Mostly the Enum data types in the
# default instructions set of each category end up being a select.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
SELECTS: dict[str, tuple[SelectEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        SelectEntityDescription(
            key=DPCode.ALARM_VOLUME,
            name="Volume",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Coffee maker
    # https://developer.tuya.com/en/docs/iot/categorykfj?id=Kaiuz2p12pc7f
    "kfj": (
        SelectEntityDescription(
            key=DPCode.CUP_NUMBER,
            name="Cups",
            icon="mdi:numeric",
        ),
        SelectEntityDescription(
            key=DPCode.CONCENTRATION_SET,
            name="Concentration",
            icon="mdi:altimeter",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.MATERIAL,
            name="Material",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            icon="mdi:coffee",
        ),
    ),
    # Switch
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "kg": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            entity_category=EntityCategory.CONFIG,
            translation_key="relay_status",
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="light_mode",
        ),
    ),
    # Smart Lock
    # https://developer.tuya.com/en/docs/iot/f?id=Kb0o2vbzuzl81
    "ms": (
        SelectEntityDescription(
            key=DPCode.ALARM_VOLUME,
            name="Alert volume",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:volume-high",
            translation_key="lock_alarm_volume",
        ),
        SelectEntityDescription(
            key=DPCode.BASIC_NIGHTVISION,
            name="Infrared (IR) night vision",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:weather-night",
            translation_key="lock_basic_nightvision",
        ),
        SelectEntityDescription(
            key=DPCode.BEEP_VOLUME,
            name="Local voice volume",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:volume-high",
            translation_key="lock_doorbell_volume",
        ),
        SelectEntityDescription(
            key=DPCode.DOOR_UNCLOSED_TRIGGER,
            name="Trigger time of unclosed",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="lock_door_unclosed_trigger",
        ),
        SelectEntityDescription(
            key=DPCode.DOORBELL_SONG,
            name="Doorbell ringtone",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:music-box-multiple-outline",
            translation_key="lock_doorbell_song",
        ),
        SelectEntityDescription(
            key=DPCode.DOORBELL_VOLUME,
            name="Doorbell volume",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:volume-high",
            translation_key="lock_doorbell_volume",
        ),
        SelectEntityDescription(
            key=DPCode.KEY_TONE,
            name="Volume on keypress",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:music-box-multiple-outline",
            translation_key="lock_doorbell_volume",
        ),
        SelectEntityDescription(
            key=DPCode.LOCK_MOTOR_DIRECTION,
            name="Rotation direction of motor",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:swap-horizontal",
            translation_key="lock_motor_direction",
        ),
        SelectEntityDescription(
            key=DPCode.LOW_POWER_THRESHOLD,
            name="Low battery alert",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:battery-alert-variant-outline",
            translation_key="lock_low_power_threshold",
        ),
        SelectEntityDescription(
            key=DPCode.MOTOR_TORQUE,
            name="Torque force of motor",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:hexagon-multiple-outline",
            translation_key="lock_motor_torque",
        ),
        SelectEntityDescription(
            key=DPCode.OPEN_SPEED_STATE,
            name="Unlocking speed",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:speedometer",
            translation_key="lock_open_speed_state",
        ),
        SelectEntityDescription(
            key=DPCode.PHOTO_MODE,
            name="Photo mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:image-multiple-outline",
            translation_key="lock_photo_mode",
        ),
        SelectEntityDescription(
            key=DPCode.RINGTONE,
            name="Local ringtone",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:music-box-multiple-outline",
            translation_key="lock_ringtone",
        ),
        SelectEntityDescription(
            key=DPCode.SOUND_MODE,
            name="Sound mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:music-box-multiple-outline",
            translation_key="lock_sound_mode",
        ),
        SelectEntityDescription(
            key=DPCode.STAY_ALARM_MODE,
            name="Loitering alert mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:star-box-multiple-outline",
            translation_key="lock_stay_alarm_mode",
        ),
        SelectEntityDescription(
            key=DPCode.STAY_CAPTURE_MODE,
            name="Loitering photo capture mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:image-multiple-outline",
            translation_key="lock_stay_capture_mode",
        ),
        SelectEntityDescription(
            key=DPCode.STAY_TRIGGER_DISTANCE,
            name="Loitering sensing range",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:signal-distance-variant",
            translation_key="lock_stay_trigger_distance",
        ),
        SelectEntityDescription(
            key=DPCode.UNLOCK_SWITCH,
            name="Unlock mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:shield-lock-open-outline",
            translation_key="lock_unlock_switch",
        ),
        *LANGUAGE_SELECT,
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryqn?id=Kaiuz18kih0sm
    "qn": (
        SelectEntityDescription(
            key=DPCode.LEVEL,
            name="Temperature level",
            icon="mdi:thermometer-lines",
        ),
    ),
    # Siren Alarm
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sgbj": (
        SelectEntityDescription(
            key=DPCode.ALARM_VOLUME,
            name="Volume",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.BRIGHT_STATE,
            name="Brightness",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        SelectEntityDescription(
            key=DPCode.IPC_WORK_MODE,
            name="IPC mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="ipc_work_mode",
        ),
        SelectEntityDescription(
            key=DPCode.DECIBEL_SENSITIVITY,
            name="Sound detection densitivity",
            icon="mdi:volume-vibrate",
            entity_category=EntityCategory.CONFIG,
            translation_key="decibel_sensitivity",
        ),
        SelectEntityDescription(
            key=DPCode.RECORD_MODE,
            name="Record mode",
            icon="mdi:record-rec",
            entity_category=EntityCategory.CONFIG,
            translation_key="record_mode",
        ),
        SelectEntityDescription(
            key=DPCode.BASIC_NIGHTVISION,
            name="Night vision",
            icon="mdi:theme-light-dark",
            entity_category=EntityCategory.CONFIG,
            translation_key="basic_nightvision",
        ),
        SelectEntityDescription(
            key=DPCode.BASIC_ANTI_FLICKER,
            name="Anti-flicker",
            icon="mdi:image-outline",
            entity_category=EntityCategory.CONFIG,
            translation_key="basic_anti_flicker",
        ),
        SelectEntityDescription(
            key=DPCode.MOTION_SENSITIVITY,
            name="Motion detection sensitivity",
            icon="mdi:motion-sensor",
            entity_category=EntityCategory.CONFIG,
            translation_key="motion_sensitivity",
        ),
    ),
    # IoT Switch?
    # Note: Undocumented
    "tdq": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            entity_category=EntityCategory.CONFIG,
            translation_key="relay_status",
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="light_mode",
        ),
    ),
    # Dimmer Switch
    # https://developer.tuya.com/en/docs/iot/categorytgkg?id=Kaiuz0ktx7m0o
    "tgkg": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            entity_category=EntityCategory.CONFIG,
            translation_key="relay_status",
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="light_mode",
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_1,
            name="Light source type",
            entity_category=EntityCategory.CONFIG,
            translation_key="led_type",
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_2,
            name="Light 2 source type",
            entity_category=EntityCategory.CONFIG,
            translation_key="led_type",
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_3,
            name="Light 3 source type",
            entity_category=EntityCategory.CONFIG,
            translation_key="led_type",
        ),
    ),
    # Dimmer
    # https://developer.tuya.com/en/docs/iot/tgq?id=Kaof8ke9il4k4
    "tgq": (
        SelectEntityDescription(
            key=DPCode.LED_TYPE_1,
            name="Light source type",
            entity_category=EntityCategory.CONFIG,
            translation_key="led_type",
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_2,
            name="Light 2 source type",
            entity_category=EntityCategory.CONFIG,
            translation_key="led_type",
        ),
    ),
    # Fingerbot
    "szjqr": (
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="fingerbot_mode",
        ),
    ),
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        SelectEntityDescription(
            key=DPCode.CISTERN,
            name="Water tank adjustment",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:water-opacity",
            translation_key="vacuum_cistern",
        ),
        SelectEntityDescription(
            key=DPCode.COLLECTION_MODE,
            name="Dust collection mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:air-filter",
            translation_key="vacuum_collection",
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:layers-outline",
            translation_key="vacuum_mode",
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf45vs7vkge
    "fs": (
        SelectEntityDescription(
            key=DPCode.FAN_VERTICAL,
            name="Vertical swing flap angle",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:format-vertical-align-center",
            translation_key="fan_angle",
        ),
        SelectEntityDescription(
            key=DPCode.FAN_HORIZONTAL,
            name="Horizontal swing flap angle",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:format-horizontal-align-center",
            translation_key="fan_angle",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
    ),
    # Curtain
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46o5mtfyc
    "cl": (
        SelectEntityDescription(
            key=DPCode.CONTROL_BACK_MODE,
            name="Motor mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:swap-horizontal",
            translation_key="curtain_motor_mode",
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            entity_category=EntityCategory.CONFIG,
            translation_key="curtain_mode",
        ),
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": (
        SelectEntityDescription(
            key=DPCode.SPRAY_MODE,
            name="Spray mode",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:spray",
            translation_key="humidifier_spray_mode",
        ),
        SelectEntityDescription(
            key=DPCode.LEVEL,
            name="Spraying level",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:spray",
            translation_key="humidifier_level",
        ),
        SelectEntityDescription(
            key=DPCode.MOODLIGHTING,
            name="Moodlighting",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:lightbulb-multiple",
            translation_key="humidifier_moodlighting",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
    ),
    # Air Purifier
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46h2s6dzm
    "kj": (
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
    ),
    # Dehumidifier
    # https://developer.tuya.com/en/docs/iot/categorycs?id=Kaiuz1vcz4dha
    "cs": (
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
            translation_key="countdown",
        ),
        SelectEntityDescription(
            key=DPCode.DEHUMIDITY_SET_ENUM,
            name="Target humidity",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:water-percent",
        ),
    ),
}

# Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SELECTS["cz"] = SELECTS["kg"]

# Power Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SELECTS["pc"] = SELECTS["kg"]

# Lock (duplicate of 'ms')
# https://developer.tuya.com/en/docs/iot/f?id=Kb0o2vbzuzl81
SELECTS["bxx"] = SELECTS["ms"]
SELECTS["gyms"] = SELECTS["ms"]
SELECTS["jtmspro"] = SELECTS["ms"]
SELECTS["hotelms"] = SELECTS["ms"]
SELECTS["ms_category"] = SELECTS["ms"]
SELECTS["jtmsbh"] = SELECTS["ms"]
SELECTS["mk"] = SELECTS["ms"]
SELECTS["videolock"] = SELECTS["ms"]
SELECTS["photolock"] = SELECTS["ms"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya select dynamically through Tuya discovery."""
    hass_data: HomeAssistantTuyaData = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_discover_device(device_ids: list[str]) -> None:
        """Discover and add a discovered Tuya select."""
        entities: list[TuyaSelectEntity] = []
        for device_id in device_ids:
            device = hass_data.device_manager.device_map[device_id]
            if descriptions := SELECTS.get(device.category):
                for description in descriptions:
                    if description.key in device.status:
                        entities.append(
                            TuyaSelectEntity(
                                device, hass_data.device_manager, description
                            )
                        )

        async_add_entities(entities)

    async_discover_device([*hass_data.device_manager.device_map])

    entry.async_on_unload(
        async_dispatcher_connect(hass, TUYA_DISCOVERY_NEW, async_discover_device)
    )


class TuyaSelectEntity(TuyaEntity, SelectEntity):
    """Tuya Select Entity."""

    def __init__(
        self,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: SelectEntityDescription,
    ) -> None:
        """Init Tuya sensor."""
        super().__init__(device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"

        self._attr_options: list[str] = []
        if enum_type := self.find_dpcode(
            description.key, dptype=DPType.ENUM, prefer_function=True
        ):
            self._attr_options = enum_type.range

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        # Raw value
        value = self.device.status.get(self.entity_description.key)
        if value is None or value not in self._attr_options:
            return None

        return value

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self._send_command(
            [
                {
                    "code": self.entity_description.key,
                    "value": option,
                }
            ]
        )
