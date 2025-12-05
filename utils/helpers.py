import math
from typing import Tuple, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 3)

def estimate_speed(point1: Dict, point2: Dict) -> float:
    """
    Estimate speed between two points with timestamps
    Returns speed in km/h
    """
    try:
        if not point1.get("timestamp") or not point2.get("timestamp"):
            return 0.0
        
        # Calculate distance
        distance_km = point2.get("distance_from_previous", 0.0)
        
        # Calculate time difference in hours
        time_diff = point2["timestamp"] - point1["timestamp"]
        hours = time_diff.total_seconds() / 3600
        
        if hours == 0:
            return 0.0
        
        speed = distance_km / hours
        return round(speed, 2)
        
    except Exception as e:
        logger.error(f"Error calculating speed: {str(e)}")
        return 0.0

def format_timestamp(dt: datetime) -> str:
    """Format datetime for API responses"""
    return dt.isoformat() if dt else None