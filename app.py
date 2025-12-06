from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import os
import sys
import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.geocoding import GeocodingService
from services.route_processor import RouteProcessor
from services.osrm_client import OSRMClient
from utils.helpers import calculate_distance, estimate_speed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
VERCEL_API_URL = os.getenv("VERCEL_API_URL", "https://tms-navy-one.vercel.app")
CRON_SECRET = os.getenv("CRON_SECRET", "")
ENABLE_CRON = os.getenv("ENABLE_CRON", "false").lower() == "true"
OSRM_BASE_URL = os.getenv("OSRM_API_URL", "http://router.project-osrm.org")

# Initialize FastAPI app
app = FastAPI(
    title="TMS Tracking API",
    description="Vehicle tracking and route processing API for TMS (HuggingFace Spaces)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger.info("Initializing services...")
geocoding_service = GeocodingService()
route_processor = RouteProcessor()
osrm_client = OSRMClient(base_url=OSRM_BASE_URL)
logger.info(f"Services initialized. OSRM URL: {OSRM_BASE_URL}")

# HTTP client for cron jobs
http_client = httpx.AsyncClient(timeout=60.0)

# Scheduler for cron jobs
scheduler = AsyncIOScheduler()

# Pydantic models
class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of GPS ping")
    vehicle_id: Optional[str] = Field(None, description="Vehicle identifier")

class RouteRequest(BaseModel):
    coordinates: List[Coordinate] = Field(..., min_length=2, description="List of GPS coordinates (minimum 2)")
    simplify: bool = Field(default=True, description="Apply Douglas-Peucker simplification")
    snap_to_roads: bool = Field(default=True, description="Snap coordinates to actual roads")
    reverse_geocode: bool = Field(default=True, description="Get place names for coordinates")

class ProcessedPoint(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[datetime] = None
    place_name: Optional[str] = None
    speed: Optional[float] = None
    distance_from_previous: Optional[float] = None

class RouteResponse(BaseModel):
    original_points: int
    processed_points: int
    route: List[ProcessedPoint]
    encoded_polyline: str
    total_distance_km: float
    estimated_duration_minutes: Optional[float] = None

class GeocodingRequest(BaseModel):
    coordinates: List[Coordinate]

class GeocodingResponse(BaseModel):
    results: List[Dict[str, Any]]

# Cron job functions
async def location_poll_job():
    """Poll location data from Telenity every 15 minutes"""
    try:
        logger.info("🔄 Starting location poll job...")
        
        response = await http_client.post(
            f"{VERCEL_API_URL}/api/cron/location-poll",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CRON_SECRET}"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Location poll successful: {response.json()}")
        else:
            logger.error(f"❌ Location poll failed: {response.status_code} - {response.text}")
            
    except httpx.TimeoutException:
        logger.error("❌ Location poll timeout")
    except Exception as e:
        logger.error(f"❌ Location poll error: {str(e)}", exc_info=True)

async def consent_poll_job():
    """Poll consent data from Telenity every 60 minutes"""
    try:
        logger.info("🔄 Starting consent poll job...")
        
        response = await http_client.post(
            f"{VERCEL_API_URL}/api/telenity/consent/poll",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CRON_SECRET}"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Consent poll successful: {response.json()}")
        else:
            logger.error(f"❌ Consent poll failed: {response.status_code} - {response.text}")
            
    except httpx.TimeoutException:
        logger.error("❌ Consent poll timeout")
    except Exception as e:
        logger.error(f"❌ Consent poll error: {str(e)}", exc_info=True)

async def auth_token_refresh_job():
    """Refresh authentication token every 6 hours"""
    try:
        logger.info("🔄 Starting authentication token refresh job...")
        
        response = await http_client.post(
            f"{VERCEL_API_URL}/api/telenity/auth/refresh",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CRON_SECRET}"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Auth token refresh successful: {response.json()}")
        else:
            logger.error(f"❌ Auth token refresh failed: {response.status_code} - {response.text}")
            
    except httpx.TimeoutException:
        logger.error("❌ Auth token refresh timeout")
    except Exception as e:
        logger.error(f"❌ Auth token refresh error: {str(e)}", exc_info=True)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info("🚀 TMS Tracking API started successfully")
    logger.info(f"📍 API Documentation: /docs")
    logger.info(f"❤️  Health Check: /health")
    logger.info(f"🌐 OSRM URL: {OSRM_BASE_URL}")
    logger.info(f"🔗 Vercel API: {VERCEL_API_URL}")
    
    # Start cron jobs if enabled
    if ENABLE_CRON:
        logger.info("⏰ Starting cron jobs...")
        
        # Location poll - every 15 minutes
        scheduler.add_job(
            location_poll_job,
            'cron',
            minute='*/15',
            id='location_poll',
            replace_existing=True,
            max_instances=1
        )
        logger.info("  ✓ Location poll: every 15 minutes")
        
        # Consent poll - every 60 minutes
        scheduler.add_job(
            consent_poll_job,
            'cron',
            minute='*/60',
            id='consent_poll',
            replace_existing=True,
            max_instances=1
        )
        logger.info("  ✓ Consent poll: every 60 minutes")
        
        # Auth token refresh - every 6 hours
        scheduler.add_job(
            auth_token_refresh_job,
            'cron',
            hour='*/6',
            minute='0',
            id='auth_token_refresh',
            replace_existing=True,
            max_instances=1
        )
        logger.info("  ✓ Auth token refresh: every 6 hours")
        
        scheduler.start()
        logger.info("✅ Cron jobs started successfully")
    else:
        logger.info("⚠️  Cron jobs disabled (set ENABLE_CRON=true to enable)")
    
    logger.info("=" * 70)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 TMS Tracking API shutting down...")
    
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped")
    
    await http_client.aclose()
    logger.info("✅ HTTP client closed")

# API endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TMS Tracking API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "process_route": "/api/v1/process-route",
            "geocode": "/api/v1/geocode",
            "trigger_location_poll": "/api/trigger/location-poll",
            "trigger_consent_poll": "/api/trigger/consent-poll"
        },
        "cron_enabled": ENABLE_CRON
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "geocoding": "operational",
            "routing": "operational",
            "osrm": OSRM_BASE_URL,
            "vercel": VERCEL_API_URL
        },
        "cron_jobs": {
            "enabled": ENABLE_CRON,
            "scheduler_running": scheduler.running if ENABLE_CRON else False,
            "jobs": [job.id for job in scheduler.get_jobs()] if ENABLE_CRON and scheduler.running else []
        },
        "version": "1.0.0"
    }

@app.post("/api/v1/process-route", response_model=RouteResponse)
async def process_route(request: RouteRequest):
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
            raise HTTPException(
                status_code=400, 
                detail="At least 2 coordinates required for route processing"
            )
        
        logger.info(f"Processing route with {len(request.coordinates)} points")
        
        # Convert to list of tuples
        coords = [(c.lat, c.lng) for c in request.coordinates]
        
        # Step 1: Simplify route if requested
        if request.simplify and len(coords) > 2:
            coords = route_processor.simplify_route(coords, tolerance=0.0001)
            logger.info(f"Simplified to {len(coords)} points")
        
        # Step 2: Snap to roads if requested
        if request.snap_to_roads:
            try:
                snapped_coords = await osrm_client.snap_to_roads(coords)
                if snapped_coords:
                    coords = snapped_coords
                    logger.info(f"Snapped to roads: {len(coords)} points")
            except Exception as e:
                logger.warning(f"Road snapping failed, using original coords: {e}")
        
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
            
            # Reverse geocode if requested (only start and end to respect rate limits)
            if request.reverse_geocode and (i == 0 or i == len(coords) - 1):
                try:
                    place_name = await geocoding_service.reverse_geocode(lat, lng)
                    point_data["place_name"] = place_name
                except Exception as e:
                    logger.warning(f"Geocoding failed for point {i}: {e}")
                    point_data["place_name"] = "Unknown Location"
            
            processed_points.append(ProcessedPoint(**point_data))
        
        # Step 4: Generate encoded polyline
        encoded_polyline = route_processor.encode_polyline(coords)
        
        # Step 5: Estimate duration using OSRM
        duration_minutes = None
        if len(coords) >= 2:
            try:
                duration_minutes = await osrm_client.get_route_duration(coords)
            except Exception as e:
                logger.warning(f"Duration estimation failed: {e}")
        
        logger.info(f"✅ Route processed successfully: {len(processed_points)} points, {total_distance:.2f} km")
        
        return RouteResponse(
            original_points=len(request.coordinates),
            processed_points=len(processed_points),
            route=processed_points,
            encoded_polyline=encoded_polyline,
            total_distance_km=round(total_distance, 3),
            estimated_duration_minutes=duration_minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing route: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/v1/geocode", response_model=GeocodingResponse)
async def geocode_batch(request: GeocodingRequest):
    """
    Batch reverse geocoding for multiple coordinates
    """
    try:
        results = []
        for coord in request.coordinates:
            try:
                place_name = await geocoding_service.reverse_geocode(coord.lat, coord.lng)
            except Exception as e:
                logger.warning(f"Geocoding failed for {coord.lat},{coord.lng}: {e}")
                place_name = "Unknown Location"
            
            results.append({
                "lat": coord.lat,
                "lng": coord.lng,
                "place_name": place_name,
                "timestamp": coord.timestamp
            })
        
        return GeocodingResponse(results=results)
        
    except Exception as e:
        logger.error(f"Error in batch geocoding: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Manual trigger endpoints for cron jobs
@app.post("/api/trigger/location-poll")
async def trigger_location_poll():
    """Manually trigger location poll job"""
    try:
        await location_poll_job()
        return {
            "status": "success",
            "message": "Location poll triggered successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Manual location poll trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trigger/consent-poll")
async def trigger_consent_poll():
    """Manually trigger consent poll job"""
    try:
        await consent_poll_job()
        return {
            "status": "success",
            "message": "Consent poll triggered successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Manual consent poll trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cron/status")
async def cron_status():
    """Get status of all cron jobs"""
    if not ENABLE_CRON or not scheduler.running:
        return {
            "enabled": ENABLE_CRON,
            "running": False,
            "jobs": []
        }
    
    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "enabled": ENABLE_CRON,
        "running": scheduler.running,
        "jobs": jobs_info
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7860,
        log_level="info"
    )