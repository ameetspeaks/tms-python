---
title: TMS Tracking API
emoji: 🚛
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# TMS Tracking API

Vehicle tracking and route processing API for Transportation Management System (TMS).
Integrated with Vite Frontend and Supabase.

## 🚀 Live API
- **API Base URL**: https://ameetspeaks-tms.hf.space
- **API Documentation**: https://ameetspeaks-tms.hf.space/docs
- **Health Check**: https://ameetspeaks-tms.hf.space/health

## System Architecture

The system follows a hybrid architecture to optimize costs and performance:
1. **Data Source**: Telenity SIM cards send GPS pings (15-min intervals).
2. **Storage**: Raw coordinates are stored in Supabase via tracking execution API.
3. **Frontend**: Vite React application fetches raw data.
4. **Processing**: Python API (HuggingFace Spaces) handles heavy lifting:
   * Route simplification (Douglas-Peucker)
   * Road snapping (OSRM)
   * Reverse geocoding (Nominatim)
   * Polyline encoding (Google Maps format)
5. **Visualization**: Frontend displays the processed route on Google Maps.

## Features

- 🗺️ **Route Optimization**: Reduces point count while maintaining path accuracy.
- 📍 **Cost-Effective Geocoding**: Uses OpenStreetMap Nominatim instead of Google APIs.
- 🛣️ **Smart Snapping**: Aligns GPS points to actual road networks using OSRM.
- 📏 **Analytics**: Calculates distance, speed, and estimated duration.
- 🎯 **Compatibility**: Outputs Google Maps compatible polylines.
- ⚡ **High Performance**: Implements caching and async processing.
- 🔒 **Secure**: CORS enabled for Vercel production and local development.

## API Endpoints

### Process Route
`POST /api/v1/process-route`

Process GPS coordinates from Telenity SIM tracking.

**Request:**
```json
{
  "coordinates": [
    {
      "lat": 28.6139,
      "lng": 77.2090,
      "timestamp": "2024-01-01T10:00:00Z",
      "vehicle_id": "TRK001"
    }
  ],
  "simplify": true,
  "snap_to_roads": true,
  "reverse_geocode": true
}
```

**Response:**
```json
{
  "original_points": 20,
  "processed_points": 15,
  "route": [...],
  "encoded_polyline": "_p~iF~ps|U_ulLnnqC_mqNvxq`@",
  "total_distance_km": 45.3,
  "estimated_duration_minutes": 65.5
}
```

### Batch Geocoding
`POST /api/v1/geocode`

Reverse geocode multiple coordinates at once.

### Health Check
`GET /health`

Check API status and service availability.

## Integration with Frontend
```javascript
const API_URL = 'https://ameetspeaks-tms.hf.space';

async function processVehicleRoute(coordinates) {
  const response = await fetch(`${API_URL}/api/v1/process-route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      coordinates: coordinates,
      simplify: true,
      snap_to_roads: true,
      reverse_geocode: true
    })
  });
  
  return await response.json();
}
```

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload --port 7860
```

### Running Tests
```bash
pytest tests/ -v
```

## Environment Variables

- `OSRM_API_URL`: Custom OSRM server URL (default: public OSRM)
- `LOG_LEVEL`: Logging level (default: INFO)

## Performance & Rate Limits

- Geocoding results cached for 24 hours
- Processes 100+ coordinates in <2 seconds
- Nominatim rate limit: 1 request/second (respected via caching)
- OSRM public instance used (consider self-hosting for production)

## Notes

- Using public OSRM instance - consider self-hosting for production use
- Nominatim has rate limits - aggressive caching implemented
- All timestamps should be in ISO 8601 format
- Coordinates use standard lat/lng format (not lng/lat)
```

## 2. **Create proper project structure**

Create a file named `.dockerignore`:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
*.egg-info
dist
build
*.md
!README.md
.DS_Store
.vscode
.idea