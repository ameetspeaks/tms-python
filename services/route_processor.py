import polyline
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class RouteProcessor:
    def __init__(self):
        pass
    
    def simplify_route(self, coordinates: List[Tuple[float, float]], tolerance: float = 0.0001) -> List[Tuple[float, float]]:
        """
        Apply Douglas-Peucker algorithm to simplify route
        Reduces number of points while maintaining route shape
        """
        if len(coordinates) < 3:
            return coordinates
        
        try:
            simplified = self._douglas_peucker(coordinates, tolerance)
            logger.info(f"Simplified from {len(coordinates)} to {len(simplified)} points")
            return simplified
        except Exception as e:
            logger.error(f"Error simplifying route: {str(e)}")
            return coordinates
    
    def _douglas_peucker(self, points: List[Tuple[float, float]], tolerance: float) -> List[Tuple[float, float]]:
        """
        Douglas-Peucker algorithm implementation
        """
        if len(points) < 3:
            return points
        
        # Find point with maximum distance
        dmax = 0
        index = 0
        end = len(points) - 1
        
        for i in range(1, end):
            d = self._perpendicular_distance(points[i], points[0], points[end])
            if d > dmax:
                index = i
                dmax = d
        
        # If max distance is greater than tolerance, recursively simplify
        if dmax > tolerance:
            # Recursive call
            rec_results1 = self._douglas_peucker(points[:index+1], tolerance)
            rec_results2 = self._douglas_peucker(points[index:], tolerance)
            
            # Build result list
            result = rec_results1[:-1] + rec_results2
        else:
            result = [points[0], points[end]]
        
        return result
    
    def _perpendicular_distance(self, point: Tuple[float, float], 
                                line_start: Tuple[float, float], 
                                line_end: Tuple[float, float]) -> float:
        """
        Calculate perpendicular distance from point to line
        """
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return np.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        
        # Calculate perpendicular distance
        nom = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1)
        denom = np.sqrt(dy**2 + dx**2)
        
        return nom / denom
    
    def encode_polyline(self, coordinates: List[Tuple[float, float]]) -> str:
        """
        Encode coordinates to Google Maps polyline format
        """
        try:
            encoded = polyline.encode(coordinates, 5)
            logger.debug(f"Encoded {len(coordinates)} points to polyline")
            return encoded
        except Exception as e:
            logger.error(f"Error encoding polyline: {str(e)}")
            return ""
    
    def decode_polyline(self, encoded: str) -> List[Tuple[float, float]]:
        """
        Decode Google Maps polyline to coordinates
        """
        try:
            decoded = polyline.decode(encoded)
            return decoded
        except Exception as e:
            logger.error(f"Error decoding polyline: {str(e)}")
            return []