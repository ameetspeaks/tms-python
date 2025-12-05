import httpx
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class OSRMClient:
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        """
        OSRM client for routing and map matching
        Using public OSRM instance (replace with your own for production)
        """
        self.base_url = base_url
        self.timeout = 30.0
    
    async def snap_to_roads(self, coordinates: List[Tuple[float, float]]) -> Optional[List[Tuple[float, float]]]:
        """
        Snap GPS coordinates to road network using OSRM match service
        """
        if len(coordinates) < 2:
            return coordinates
        
        try:
            # Format coordinates for OSRM (lng,lat format)
            coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
            url = f"{self.base_url}/match/v1/driving/{coords_str}"
            
            params = {
                "overview": "full",
                "geometries": "geojson",
                "steps": "false"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") == "Ok" and data.get("matchings"):
                    # Extract snapped coordinates
                    geometry = data["matchings"][0]["geometry"]
                    snapped = [(coord[1], coord[0]) for coord in geometry["coordinates"]]
                    logger.info(f"Snapped {len(coordinates)} points to {len(snapped)} road points")
                    return snapped
                else:
                    logger.warning(f"OSRM match failed: {data.get('code')}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("OSRM request timeout")
            return None
        except Exception as e:
            logger.error(f"Error snapping to roads: {str(e)}")
            return None
    
    async def get_route_duration(self, coordinates: List[Tuple[float, float]]) -> Optional[float]:
        """
        Get estimated route duration in minutes using OSRM
        """
        if len(coordinates) < 2:
            return None
        
        try:
            # Use first and last point for duration estimate
            start = coordinates[0]
            end = coordinates[-1]
            
            coords_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
            url = f"{self.base_url}/route/v1/driving/{coords_str}"
            
            params = {
                "overview": "false",
                "steps": "false"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") == "Ok" and data.get("routes"):
                    duration_seconds = data["routes"][0]["duration"]
                    duration_minutes = duration_seconds / 60
                    logger.info(f"Route duration: {duration_minutes:.2f} minutes")
                    return round(duration_minutes, 2)
                else:
                    logger.warning(f"OSRM route failed: {data.get('code')}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting route duration: {str(e)}")
            return None