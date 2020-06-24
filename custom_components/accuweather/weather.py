"""Support for the AccuWeather service."""
from homeassistant.components.weather import (  # ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    WeatherEntity,
)
from homeassistant.const import CONF_NAME, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.util.dt import utc_from_timestamp

from .const import ATTRIBUTION, CONDITION_CLASSES, COORDINATOR, DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a AccuWeather weather entity from a config_entry."""
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    async_add_entities([AccuWeatherEntity(name, coordinator)], False)


class AccuWeatherEntity(WeatherEntity):
    """Define an AccuWeather entity."""

    def __init__(self, name, coordinator):
        """Initialize."""
        self._name = name
        self.coordinator = coordinator
        self._attrs = {}

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return self.coordinator.location_key

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def condition(self):
        """Return the current condition."""
        try:
            return [
                k
                for k, v in CONDITION_CLASSES.items()
                if self.coordinator.data["WeatherIcon"] in v
            ][0]
        except IndexError:
            return STATE_UNKNOWN

    @property
    def temperature(self):
        """Return the temperature."""
        return self.coordinator.data["Temperature"]["Metric"]["Value"]

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        return self.coordinator.data["Pressure"]["Metric"]["Value"]

    @property
    def humidity(self):
        """Return the humidity."""
        return self.coordinator.data["RelativeHumidity"]

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self.coordinator.data["Wind"]["Speed"]["Metric"]["Value"]

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.coordinator.data["Wind"]["Direction"]["Degrees"]

    @property
    def visibility(self):
        """Return the visibility."""
        return self.coordinator.data["Visibility"]["Metric"]["Value"]

    @property
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def forecast(self):
        """Return the forecast array."""
        if self.coordinator.forecast:
            return [
                {
                    ATTR_FORECAST_TIME: utc_from_timestamp(
                        item["EpochDate"]
                    ).isoformat(),
                    ATTR_FORECAST_TEMP: item["Temperature"]["Maximum"]["Value"],
                    ATTR_FORECAST_TEMP_LOW: item["Temperature"]["Minimum"]["Value"],
                    ATTR_FORECAST_WIND_SPEED: item["Day"]["Wind"]["Speed"]["Value"],
                    ATTR_FORECAST_WIND_BEARING: item["Day"]["Wind"]["Direction"][
                        "Degrees"
                    ],
                    ATTR_FORECAST_CONDITION: [
                        k
                        for k, v in CONDITION_CLASSES.items()
                        if item["Day"]["Icon"] in v
                    ][0],
                }
                for item in self.coordinator.data["DailyForecasts"]
            ]

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update AccuWeather entity."""
        await self.coordinator.async_request_refresh()
