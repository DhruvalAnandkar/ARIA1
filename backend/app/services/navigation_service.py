import math
import re
import uuid

import requests

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_walking_directions(
    lat: float, lng: float, destination: str
) -> dict:
    """Get walking directions from Google Maps Directions API.

    Returns:
        {
            "route_id": str,
            "steps": [{"instruction": str, "distance": str, "duration": str, "lat": float, "lng": float}],
            "total_distance": str,
            "total_duration": str,
        }
    """
    origin = f"{lat},{lng}"

    r = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json",
        params={
            "origin": origin,
            "destination": destination,
            "mode": "walking",
            "key": settings.google_maps_api_key,
        },
        timeout=10,
    )
    data = r.json()

    if data["status"] != "OK":
        logger.warning("directions_api_error", status=data["status"], destination=destination)
        return {
            "route_id": "",
            "steps": [],
            "total_distance": "",
            "total_duration": "",
            "error": f"Could not find route: {data['status']}",
        }

    leg = data["routes"][0]["legs"][0]
    steps = []

    for step in leg["steps"]:
        clean_instruction = re.sub(r"<[^<]+?>", "", step["html_instructions"])
        steps.append({
            "instruction": f"{clean_instruction} for {step['distance']['text']}",
            "distance": step["distance"]["text"],
            "duration": step["duration"]["text"],
            "lat": step["end_location"]["lat"],
            "lng": step["end_location"]["lng"],
        })

    return {
        "route_id": uuid.uuid4().hex,
        "steps": steps,
        "total_distance": leg["distance"]["text"],
        "total_duration": leg["duration"]["text"],
    }


def calculate_distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two GPS coordinates in meters (Haversine)."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_near_waypoint(
    current_lat: float, current_lng: float, waypoint_lat: float, waypoint_lng: float, threshold_m: float = 20
) -> bool:
    """Check if the user is near a waypoint (within threshold meters)."""
    return calculate_distance_meters(current_lat, current_lng, waypoint_lat, waypoint_lng) <= threshold_m
