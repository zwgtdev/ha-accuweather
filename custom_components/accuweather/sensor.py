"""Support for the AccuWeather service."""
import logging

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
    TIME_HOURS,
    UNIT_PERCENTAGE,
    UV_INDEX,
)
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_UNIT_IMPERIAL,
    ATTR_UNIT_METRIC,
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    OPTIONAL_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

ATTR_ICON = "icon"
ATTR_LABEL = "label"

LENGTH_MILIMETERS = "mm"

FORECAST_DAYS = [0, 1, 2, 3, 4]

FORECAST_SENSOR_TYPES = {
    "RealFeelTemperatureShadeMax": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature Shade Max",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "RealFeelTemperatureShadeMin": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature Shade Min",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "RealFeelTemperatureMax": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature Max",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "RealFeelTemperatureMin": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "RealFeel Temperature Min",
        ATTR_UNIT_METRIC: TEMP_CELSIUS,
        ATTR_UNIT_IMPERIAL: TEMP_FAHRENHEIT,
    },
    "PrecipitationProbabilityDay": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "weather-snowy-rainy",
        ATTR_LABEL: "Precipitation Probability Day",
        ATTR_UNIT_METRIC: UNIT_PERCENTAGE,
        ATTR_UNIT_IMPERIAL: UNIT_PERCENTAGE,
    },
    "PrecipitationProbabilityNight": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "weather-snowy-rainy",
        ATTR_LABEL: "Precipitation Probability Night",
        ATTR_UNIT_METRIC: UNIT_PERCENTAGE,
        ATTR_UNIT_IMPERIAL: UNIT_PERCENTAGE,
    },
    "ThunderstormProbabilityDay": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "weather-lightning",
        ATTR_LABEL: "Thunderstorm Probability Day",
        ATTR_UNIT_METRIC: UNIT_PERCENTAGE,
        ATTR_UNIT_IMPERIAL: UNIT_PERCENTAGE,
    },
    "ThunderstormProbabilityNight": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "weather-lightning",
        ATTR_LABEL: "Thunderstorm Probability Night",
        ATTR_UNIT_METRIC: UNIT_PERCENTAGE,
        ATTR_UNIT_IMPERIAL: UNIT_PERCENTAGE,
    },
    "HoursOfSun": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-lightning",
        ATTR_LABEL: "Hours Of Sun",
        ATTR_UNIT_METRIC: TIME_HOURS,
        ATTR_UNIT_IMPERIAL: TIME_HOURS,
    },
    "UVIndex": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-sunny",
        ATTR_LABEL: "UV Index",
        ATTR_UNIT_METRIC: UV_INDEX,
        ATTR_UNIT_IMPERIAL: UV_INDEX,
    },
}

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
        ATTR_UNIT_METRIC: UV_INDEX,
        ATTR_UNIT_IMPERIAL: UV_INDEX,
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

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(AccuWeatherSensor(name, sensor, coordinator))

    if coordinator.forecast:
        for sensor in FORECAST_SENSOR_TYPES:
            for day in FORECAST_DAYS:
                sensors.append(
                    AccuWeatherSensor(name, sensor, coordinator, forecast_day=day)
                )

    async_add_entities(sensors, False)


class AccuWeatherSensor(Entity):
    """Define an AccuWeather entity."""

    def __init__(self, name, kind, coordinator, forecast_day=None):
        """Initialize."""
        self._name = name
        self.kind = kind
        self.coordinator = coordinator
        self._device_class = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self.units = (
            ATTR_UNIT_METRIC if self.coordinator.is_metric else ATTR_UNIT_IMPERIAL
        )
        self.forecast_day = forecast_day

    @property
    def name(self):
        """Return the name."""
        if self.forecast_day is not None:
            return f"{self._name} {FORECAST_SENSOR_TYPES[self.kind][ATTR_LABEL]} {self.forecast_day}d"
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        if self.forecast_day is not None:
            return f"{self.coordinator.location_key}-{self.kind}-{self.forecast_day}".lower()
        return f"{self.coordinator.location_key}-{self.kind}".lower()

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
        if self.forecast_day is not None:
            if self.kind in [
                "RealFeelTemperatureMax",
                "RealFeelTemperatureMin",
                "RealFeelTemperatureShadeMax",
                "RealFeelTemperatureShadeMin",
                "UVIndex",
            ]:
                return self.coordinator.data["DailyForecasts"][self.forecast_day][
                    self.kind
                ]["Value"]
            return self.coordinator.data["DailyForecasts"][self.forecast_day][self.kind]
        if self.kind in ["UVIndex", "CloudCover"]:
            return self.coordinator.data[self.kind]
        if self.kind == "Ceiling":
            return round(self.coordinator.data[self.kind][self.units]["Value"])
        if self.kind == "PressureTendency":
            return self.coordinator.data[self.kind]["LocalizedText"].lower()
        if self.kind == "Precipitation":
            return self.coordinator.data["PrecipitationSummary"][self.kind][self.units][
                "Value"
            ]
        if self.kind == "WindGust":
            return self.coordinator.data[self.kind]["Speed"][self.units]["Value"]
        return self.coordinator.data[self.kind][self.units]["Value"]

    @property
    def icon(self):
        """Return the icon."""
        if self.forecast_day is not None:
            return FORECAST_SENSOR_TYPES[self.kind][ATTR_ICON]
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def device_class(self):
        """Return the device_class."""
        if self.forecast_day is not None:
            return FORECAST_SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]
        return SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        if self.forecast_day is not None:
            return FORECAST_SENSOR_TYPES[self.kind][self.units]
        return SENSOR_TYPES[self.kind][self.units]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.forecast_day is not None:
            if self.kind == "PrecipitationProbabilityDay":
                self._attrs["type"] = self.coordinator.data["DailyForecasts"][
                    self.forecast_day
                ].get("PrecipitationTypeDay")
                self._attrs["intensity"] = self.coordinator.data["DailyForecasts"][
                    self.forecast_day
                ].get("PrecipitationIntensityDay")
                self._attrs["rain_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["RainProbabilityDay"]
                self._attrs["snow_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["SnowProbabilityDay"]
                self._attrs["ice_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["IceProbabilityDay"]
            if self.kind == "PrecipitationProbabilityNight":
                self._attrs["type"] = self.coordinator.data["DailyForecasts"][
                    self.forecast_day
                ].get("PrecipitationTypeNight")
                self._attrs["intensity"] = self.coordinator.data["DailyForecasts"][
                    self.forecast_day
                ].get("PrecipitationIntensityNight")
                self._attrs["rain_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["RainProbabilityNight"]
                self._attrs["snow_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["SnowProbabilityNight"]
                self._attrs["ice_probability"] = self.coordinator.data[
                    "DailyForecasts"
                ][self.forecast_day]["IceProbabilityNight"]
            if self.kind == "UVIndex":
                self._attrs["level"] = self.coordinator.data["DailyForecasts"][
                    self.forecast_day
                ][self.kind]["Category"]
            return self._attrs
        if self.kind == "UVIndex":
            self._attrs["level"] = self.coordinator.data["UVIndexText"]
        if self.kind == "Precipitation":
            self._attrs["precipitation_type"] = self.coordinator.data[
                "PrecipitationType"
            ]
        return self._attrs

    @property
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added to the entity registry."""
        return bool(self.kind not in OPTIONAL_SENSORS)

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update AccuWeather entity."""
        await self.coordinator.async_request_refresh()
