import os
import platform
import psutil
import requests
from typing import Annotated, Any

def register(agent: Any) -> None:
    @agent.tool
    def get_system_info() -> dict[str, Any]:
        """Get information about the current system (OS, CPU, Memory)."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu_count": psutil.cpu_count(),
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        }

    @agent.tool
    def list_directory(
        path: Annotated[str, "The directory path to list"] = "."
    ) -> dict[str, Any]:
        """List files and directories in a given path."""
        try:
            items = os.listdir(path)
            return {"items": items, "path": os.path.abspath(path)}
        except Exception as e:
            return {"error": str(e)}

    @agent.tool
    def get_weather(
        city: Annotated[str, "Name of the city"],
        lat: Annotated[float | None, "Latitude (optional)"] = None,
        lon: Annotated[float | None, "Longitude (optional)"] = None
    ) -> dict[str, Any]:
        """Get current weather for a city using Open-Meteo."""
        # Simple city to lat/lon mapping for common ones if not provided
        # For a real tool, we'd use a geocoding API.
        if lat is None or lon is None:
            # Mock geocoding for some cities
            geodata = {"london": (51.5, -0.1), "paris": (48.8, 2.3), "new york": (40.7, -74.0), "tokyo": (35.7, 139.7)}
            lat, lon = geodata.get(city.lower(), (0.0, 0.0))
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            return {"city": city, "weather": data.get("current_weather", {})}
        except Exception as e:
            return {"error": str(e)}
