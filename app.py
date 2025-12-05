from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os

from services.geocoding import GeocodingService
from services.route_processor import RouteProcessor
from services.osrm_client import OSRMClient
from utils.helpers import calculate_distance, estimate_speed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TMS Tracking API",
    description="Vehicle tracking and route processing API for TMS (HuggingFace Spaces)",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://tms-navy-one.vercel.app",
    "https://ameetspeaks-tms.hf.space"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
geocoding_service = GeocodingService()
route_processor = RouteProcessor()
osrm_client = OSRMClient(base_url=os.getenv("OSRM_API_URL", "http://router.project-osrm.org"))

# Pydantic models
class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    timestamp: Optional[datetime] = None
    vehicle_id: Optional[str] = None

class RouteRequest(BaseModel):
    coordinates: List[Coordinate]
    simplify: bool = Field(default=True, description="Apply Douglas-Peucker simplification")
    snap_to_roads: bool = Field(default=True, description="Snap coordinates to actual roads")
    reverse_geocode: bool = Field(default=True, description="Get place names for coordinates")

class ProcessedPoint(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[datetime]
    place_name: Optional[str]
    speed: Optional[float]
    distance_from_previous: Optional[float]

class RouteResponse(BaseModel):
    original_points: int
    processed_points: int
    route: List[ProcessedPoint]
    encoded_polyline: str
    total_distance_km: float
    estimated_duration_minutes: Optional[float]

class GeocodingRequest(BaseModel):
    coordinates: List[Coordinate]

class GeocodingResponse(BaseModel):
    results: List[Dict[str, Any]]

class ReverseGeocodeRequest(BaseModel):
    lat: float
    lng: float

@app.get("/")
async def root():
    return {
        "message": "TMS Tracking API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "health": "/health",
            "process_route": "/api/v1/process-route",
            "geocode": "/api/v1/geocode",
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "geocoding": "operational",
            "routing": "operational"
        }
    }

@app.post("/api/v1/process-route", response_model=RouteResponse)
async def process_route(request: RouteRequest, background_tasks: BackgroundTasks):
    """
    Process GPS coordinates from Telenity SIM tracking:
    - Simplify route (remove redundant points)
    - Snap to roads using OSRM
    - Reverse geocode locations
    - Calculate distances and speeds
    - Generate encoded polyline for Google Maps
    """
    try:
        if len(request.coordinates) < 2:
            raise HTTPException(status_code=400, detail="At least 2 coordinates required")
        
        logger.info(f"Processing route with {len(request.coordinates)} points")
        
        # Convert to list of tuples
        coords = [(c.lat, c.lng) for c in request.coordinates]
        
        # Step 1: Simplify route if requested
        if request.simplify and len(coords) > 2:
            coords = route_processor.simplify_route(coords, tolerance=0.0001)
            logger.info(f"Simplified to {len(coords)} points")
        
        # Step 2: Snap to roads if requested
        if request.snap_to_roads:
            snapped_coords = await osrm_client.snap_to_roads(coords)
            if snapped_coords:
                coords = snapped_coords
                logger.info(f"Snapped to roads: {len(coords)} points")
        
        # Step 3: Process each point
        processed_points = []
        total_distance = 0.0
        
        for i, (lat, lng) in enumerate(coords):
            point_data = {
                "lat": lat,
                "lng": lng,
                "timestamp": request.coordinates[i].timestamp if i < len(request.coordinates) else None
            }
            
            # Calculate distance from previous point
            if i > 0:
                distance = calculate_distance(coords[i-1], (lat, lng))
                point_data["distance_from_previous"] = distance
                total_distance += distance
                
                # Calculate speed if timestamps available
                if (point_data["timestamp"] and 
                    len(processed_points) > 0 and 
                    processed_points[-1].timestamp):
                    speed = estimate_speed(
                        processed_points[-1].model_dump(),
                        point_data
                    )
                    point_data["speed"] = speed
            
            # Reverse geocode if requested
            if request.reverse_geocode:
                # Only geocode start and end to save rate limits if many points, or check logic
                # For now, geocode all simplified points but with cache
                place_name = await geocoding_service.reverse_geocode(lat, lng)
                point_data["place_name"] = place_name
            
            processed_points.append(ProcessedPoint(**point_data))
        
        # Step 4: Generate encoded polyline
        encoded_polyline = route_processor.encode_polyline(coords)
        
        # Step 5: Estimate duration using OSRM
        duration_minutes = None
        if len(coords) >= 2:
            duration_minutes = await osrm_client.get_route_duration(coords)
        
        return RouteResponse(
            original_points=len(request.coordinates),
            processed_points=len(processed_points),
            route=processed_points,
            encoded_polyline=encoded_polyline,
            total_distance_km=round(total_distance, 3),
            estimated_duration_minutes=duration_minutes
        )
        
    except Exception as e:
        logger.error(f"Error processing route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/geocode", response_model=GeocodingResponse)
async def geocode_batch(request: GeocodingRequest):
    """
    Batch reverse geocoding for multiple coordinates
    """
    try:
        results = []
        for coord in request.coordinates:
            place_name = await geocoding_service.reverse_geocode(coord.lat, coord.lng)
            results.append({
                "lat": coord.lat,
                "lng": coord.lng,
                "place_name": place_name,
                "timestamp": coord.timestamp
            })
        return GeocodingResponse(results=results)
    except Exception as e:
        logger.error(f"Error in batch geocoding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
