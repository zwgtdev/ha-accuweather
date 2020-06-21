"""Support for the AccuWeather service."""
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    CONF_NAME,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_METERS,
    TEMP_CELSIUS,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import ATTRIBUTION, DOMAIN

ATTR_ICON = "icon"
ATTR_LABEL = "label"
ATTR_UNIT = "unit"

LENGTH_MILIMETERS = "mm"

SENSOR_TYPES = {
    "RealFeelTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "ReelFeel Temperature",
        ATTR_UNIT: TEMP_CELSIUS,
    },
    "DewPoint": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Dew Point",
        ATTR_UNIT: TEMP_CELSIUS,
    },
    "UVIndex": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-sunny",
        ATTR_LABEL: "UV Index",
        ATTR_UNIT: None,
    },
    "PressureTendency": {
        ATTR_DEVICE_CLASS: "accuweather__pressure_tendency",
        ATTR_ICON: "mdi:gauge",
        ATTR_LABEL: "Pressure Tendency",
        ATTR_UNIT: None,
    },
    "ApparentTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Apparent Temperature",
        ATTR_UNIT: TEMP_CELSIUS,
    },
    "WindChillTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Wind Chill Temperature",
        ATTR_UNIT: TEMP_CELSIUS,
    },
    "WetBulbTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Wet Bulb Temperature",
        ATTR_UNIT: TEMP_CELSIUS,
    },
    "Precipitation": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_LABEL: "Precipitation",
        ATTR_UNIT: LENGTH_MILIMETERS,
    },
    "CloudCover": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-cloudy",
        ATTR_LABEL: "Cloud Cover",
        ATTR_UNIT: UNIT_PERCENTAGE,
    },
    "Ceiling": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-fog",
        ATTR_LABEL: "Cloud Ceiling",
        ATTR_UNIT: LENGTH_METERS,
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a AccuWeather weather entities from a config_entry."""
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(AccuWeatherSensor(name, sensor, coordinator))

    async_add_entities(sensors, False)


class AccuWeatherSensor(Entity):
    """Define an AccuWeather entity."""

    def __init__(self, name, kind, coordinator):
        """Initialize."""
        self._name = name
        self.kind = kind
        self.coordinator = coordinator
        self._device_class = None
        self._state = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def name(self):
        """Return the name."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.coordinator.location_key}-{self.kind}"

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the state."""
        if self.kind in ["UVIndex", "CloudCover"]:
            self._state = self.coordinator.data[self.kind]
        elif self.kind == "Ceiling":
            self._state = round(self.coordinator.data[self.kind]["Metric"]["Value"])
        elif self.kind == "PressureTendency":
            self._state = self.coordinator.data[self.kind]["LocalizedText"].lower()
        elif self.kind == "Precipitation":
            self._state = self.coordinator.data["PrecipitationSummary"][self.kind]["Metric"]["Value"]
        else:
            self._state = self.coordinator.data[self.kind]["Metric"]["Value"]
        return self._state

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def device_class(self):
        """Return the device_class."""
        return SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return SENSOR_TYPES[self.kind][ATTR_UNIT]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.kind == "UVIndex":
            self._attrs["level"] = self.coordinator.data["UVIndexText"]
        return self._attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update AccuWeather entity."""
        await self.coordinator.async_request_refresh()
