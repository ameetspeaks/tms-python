# TMS Tracking API

Vehicle tracking and route processing API for Transportation Management System (TMS).
Integrated with Vite Frontend and Supabase.

## System Architecture

The system follows a hybrid architecture to optimize costs and performance:
1.  **Data Source**: Telenity SIM cards send GPS pings (15-min intervals).
2.  **Storage**: Raw coordinates are stored in Supabase via tracking execution API.
3.  **Frontend**: Vite React application fetches raw data.
4.  **Processing**: Python API (HuggingFace Spaces) handles heavy lifting:
    *   Route simplification (Douglas-Peucker)
    *   Road snapping (OSRM)
    *   Reverse geocoding (Nominatim)
    *   Polyline encoding (Google Maps format)
5.  **Visualization**: Frontend displays the processed route on Google Maps.

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

### Single Reverse Geocode
`POST /api/v1/reverse-geocode`

### Snap to Roads
`POST /api/v1/snap-to-roads`

## Deployment

### HuggingFace Spaces (Python API)
1.  Create a new Space on HuggingFace.
2.  Select **Docker** as the SDK.
3.  Upload the contents of this `python/` directory.
4.  The `Dockerfile` is configured for non-root user (UID 1000) required by Spaces.
5.  Set Environment Variables in Space settings if needed.

### Vercel (Frontend)
1.  The Vite frontend connects to this API.
2.  Ensure `VITE_PYTHON_API_URL` is set to your HuggingFace Space URL in Vercel project settings.

## Development

### Prerequisites
- Python 3.9+
- Docker (optional)

### Local Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the server:
    ```bash
    uvicorn app:app --reload --port 7860
    ```

### Running Tests
Unit tests are included to verify logic and integrations.
```bash
pytest tests/
```

## Database Compatibility
This API is stateless and compatible with the Supabase schema. It accepts JSON data formatted from the `tracking_history` table and returns processed JSON ready for display or storage.
