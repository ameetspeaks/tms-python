from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from cachetools import TTLCache
import asyncio
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(
            user_agent="tms_tracking_api_v1",
            timeout=10
        )
        # Cache for 24 hours, max 10000 entries
        self.cache = TTLCache(maxsize=10000, ttl=86400)
    
    async def reverse_geocode(self, lat: float, lng: float) -> str:
        """
        Reverse geocode a coordinate to place name with caching
        """
        cache_key = f"{lat:.6f},{lng:.6f}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            location = await loop.run_in_executor(
                None,
                lambda: self.geolocator.reverse(f"{lat}, {lng}", language="en")
            )
            
            if location:
                place_name = location.address
                self.cache[cache_key] = place_name
                logger.info(f"Geocoded: {cache_key} -> {place_name}")
                return place_name
            else:
                return "Unknown Location"
                
        except GeocoderTimedOut:
            logger.warning(f"Geocoding timeout for {cache_key}")
            return "Geocoding Timeout"
        except GeocoderServiceError as e:
            logger.error(f"Geocoding service error: {str(e)}")
            return "Geocoding Error"
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {str(e)}")
            return "Unknown Location"
    
    def clear_cache(self):
        """Clear the geocoding cache"""
        self.cache.clear()
        logger.info("Geocoding cache cleared")