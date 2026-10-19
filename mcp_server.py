"""Provided weather APIs, automatic fallback, and a cache. No API keys needed."""
import json
import logging
import math
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

app = FastMCP("Workspace Weather")
# Try in this order. Students do not need to change the provided adapter.
API_LIST = ["met_no", "open_meteo"]
API_URLS = {
    "met_no": "https://api.met.no/weatherapi/locationforecast/2.0/compact",
    "open_meteo": "https://api.open-meteo.com/v1/forecast",
}
USER_AGENT = "GenUI-Mini-Project/1.0 (https://github.com/jinghan-yu/genui-mini-project1)"
CACHE_FILE = Path(__file__).with_name(".weather-cache.json")
CITIES = {
    "Shanghai": (31.2304, 121.4737), "Beijing": (39.9042, 116.4074),
    "London": (51.5074, -0.1278), "New York": (40.7128, -74.0060),
}


def read_cache():
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def fetch_weather(provider, city):
    cache = read_cache()
    key = f"{provider}:{city}"
    previous = cache.get(key, {})
    if not isinstance(previous, dict):
        previous = {}
    if previous.get("expires", 0) > time.time():
        return previous["weather"]
    latitude, longitude = CITIES[city]
    headers = {"User-Agent": USER_AGENT}
    if provider == "met_no":
        params = {"lat": latitude, "lon": longitude}
        if previous.get("last_modified"):
            headers["If-Modified-Since"] = previous["last_modified"]
    else:
        params = {"latitude": latitude, "longitude": longitude, "timezone": "UTC",
                  "forecast_days": 1, "wind_speed_unit": "ms",
                  "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"}
    response = httpx.get(API_URLS[provider], params=params, headers=headers,
                         timeout=6, follow_redirects=True)
    if response.status_code == 304:
        weather = previous["weather"]
    else:
        response.raise_for_status()
        data = response.json()
        if provider == "met_no":
            forecast = data["properties"]["timeseries"][0]
            details = forecast["data"]["instant"]["details"]
            period = forecast["data"].get("next_1_hours", forecast["data"].get("next_6_hours", {}))
            weather = {"city": city, "temperature": details["air_temperature"],
                       "humidity": details["relative_humidity"], "wind_speed": details["wind_speed"],
                       "condition": period.get("summary", {}).get("symbol_code", "forecast"),
                       "time": forecast["time"], "source": "MET Norway",
                       "source_url": "https://api.met.no/", "kind": "Latest forecast"}
        else:
            current = data["current"]
            weather = {"city": city, "temperature": current["temperature_2m"],
                       "humidity": current["relative_humidity_2m"], "wind_speed": current["wind_speed_10m"],
                       "weather_code": current["weather_code"], "time": current["time"] + "Z",
                       "source": "Open-Meteo", "source_url": "https://open-meteo.com/",
                       "kind": "Current weather estimate"}
        if not all(isinstance(weather[field], (int, float)) and math.isfinite(weather[field])
                   for field in ["temperature", "humidity", "wind_speed"]):
            raise ValueError("The API returned invalid weather values.")
        if not isinstance(weather["time"], str) or not isinstance(weather.get("condition", ""), str):
            raise ValueError("The API returned invalid weather text.")
    try:
        expires = time.time() + 600
        if provider == "met_no":
            expires = parsedate_to_datetime(response.headers["Expires"]).timestamp()
    except (KeyError, TypeError, ValueError, OverflowError):
        expires = time.time() + 600
    cache[key] = {"weather": weather, "expires": expires,
                  "last_modified": response.headers.get("Last-Modified", previous.get("last_modified", ""))}
    temporary = CACHE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(cache), encoding="utf-8")
    temporary.replace(CACHE_FILE)
    return weather


@app.tool()
def get_weather(city: str = "Shanghai") -> dict[str, Any]:
    """Get weather for Shanghai, Beijing, London, or New York, trying available APIs."""
    if city not in CITIES:
        raise ValueError("Choose Shanghai, Beijing, London, or New York.")
    for provider in API_LIST:
        try:
            return fetch_weather(provider, city)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            logging.warning("Weather provider %s failed: %s", provider, error)
    raise RuntimeError("All weather APIs are unavailable. Try again later.")


if __name__ == "__main__":
    app.run(transport="stdio")
