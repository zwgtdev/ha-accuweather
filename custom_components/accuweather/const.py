"""Constants for AccuWeather integration."""
ATTRIBUTION = "Data provided by AccuWeather"
CONF_FORECAST = "forecast"
COORDINATOR = "coordinator"
DOMAIN = "accuweather"
UNDO_UPDATE_LISTENER = "undo_update_listener"

CONDITION_CLASSES = {
    "cloudy": [7, 8, 38],
    "fog": [11],
    "hail": [25],
    "lightning": [],
    "lightning-rainy": [15, 16, 17, 41, 42],
    "partlycloudy": [4, 6, 35, 36],
    "pouring": [18],
    "rainy": [12, 13, 14, 26, 39, 40],
    "snowy": [19, 20, 21, 22, 23, 43, 44],
    "snowy-rainy": [29],
    "sunny": [1, 2, 3, 5, 33, 34, 37],
    "windy": [32],
    "windy-variant": [],
    "exceptional": [24, 30, 31],
}
OPTIONAL_SENSORS = (
    "DewPoint",
    "WetBulbTemperature",
    "WindChillTemperature",
    "ApparentTemperature",
    "RealFeelTemperatureShade",
)
