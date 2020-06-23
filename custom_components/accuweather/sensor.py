"""Support for the AccuWeather service."""
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    CONF_NAME,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_FEET,
    LENGTH_INCHES,
    LENGTH_METERS,
    SPEED_KILOMETERS_PER_HOUR,
    SPEED_MILES_PER_HOUR,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import ATTRIBUTION, COORDINATOR, DOMAIN

ATTR_ICON = "icon"
ATTR_LABEL = "label"
ATTR_UNIT_METRIC = "Metric"
ATTR_UNIT_IMPERIAL = "Imperial"

LENGTH_MILIMETERS = "mm"

SENSOR_TYPES = {
    "RealFeelTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "RealFeelTemperatureShade": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature Shade",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "DewPoint": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Dew Point",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "UVIndex": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-sunny",
        ATTR_LABEL: "UV Index",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "PressureTendency": {
        ATTR_DEVICE_CLASS: "accuweather__pressure_tendency",
        ATTR_ICON: "mdi:gauge",
        ATTR_LABEL: "Pressure Tendency",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "ApparentTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Apparent Temperature",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "WindChillTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Wind Chill Temperature",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "WetBulbTemperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "Wet Bulb Temperature",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "Precipitation": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_LABEL: "Precipitation",
        ATTR_UNIT_METRIC: LENGTH_MILIMETERS,
        ATTR_UNIT_IMPERIAL: LENGTH_INCHES,
    },
    "CloudCover": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-cloudy",
        ATTR_LABEL: "Cloud Cover",
        ATTR_UNIT_METRIC: UNIT_PERCENTAGE,
        ATTR_UNIT_IMPERIAL: UNIT_PERCENTAGE,
    },
    "Ceiling": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-fog",
        ATTR_LABEL: "Cloud Ceiling",
        ATTR_UNIT_METRIC: LENGTH_METERS,
        ATTR_UNIT_IMPERIAL: LENGTH_FEET,
    },
    "WindGust": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_LABEL: "Wind Gust",
        ATTR_UNIT_METRIC: SPEED_KILOMETERS_PER_HOUR,
        ATTR_UNIT_IMPERIAL: SPEED_MILES_PER_HOUR,
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a AccuWeather weather entities from a config_entry."""
    name = config_entry.data[CONF_NAME]

    units = "Metric" if hass.config.units.is_metric else "Imperial"

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(AccuWeatherSensor(name, sensor, coordinator, units))

    async_add_entities(sensors, False)


class AccuWeatherSensor(Entity):
    """Define an AccuWeather entity."""

    def __init__(self, name, kind, coordinator, units):
        """Initialize."""
        self._name = name
        self.kind = kind
        self.coordinator = coordinator
        self._device_class = None
        self._state = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self.units = units

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
            self._state = round(self.coordinator.data[self.kind][self.units]["Value"])
        elif self.kind == "PressureTendency":
            self._state = self.coordinator.data[self.kind]["LocalizedText"].lower()
        elif self.kind == "Precipitation":
            self._state = self.coordinator.data["PrecipitationSummary"][self.kind][
                self.units
            ]["Value"]
        elif self.kind == "WindGust":
            self._state = self.coordinator.data[self.kind]["Speed"][self.units]["Value"]
        else:
            self._state = self.coordinator.data[self.kind][self.units]["Value"]
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
        return SENSOR_TYPES[self.kind][self.units]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.kind == "UVIndex":
            self._attrs["level"] = self.coordinator.data["UVIndexText"]
        if self.kind == "Precipitation":
            self._attrs["precipitation_type"] = self.coordinator.data["PrecipitationType"]
        return self._attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update AccuWeather entity."""
        await self.coordinator.async_request_refresh()
