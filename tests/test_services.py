import pytest
from utils.helpers import calculate_distance, estimate_speed
from services.route_processor import RouteProcessor
from datetime import datetime, timedelta

# Tests for utils/helpers.py
def test_calculate_distance():
    # Approximate distance between New York and London
    ny = (40.7128, -74.0060)
    london = (51.5074, -0.1278)
    distance = calculate_distance(ny, london)
    assert 5500 < distance < 5600  # Should be around 5570 km

def test_calculate_distance_same_point():
    point = (40.7128, -74.0060)
    assert calculate_distance(point, point) == 0.0

def test_estimate_speed():
    t1 = datetime.now()
    t2 = t1 + timedelta(hours=1)
    
    p1 = {"timestamp": t1}
    p2 = {"timestamp": t2, "distance_from_previous": 100.0}
    
    speed = estimate_speed(p1, p2)
    assert speed == 100.0

def test_estimate_speed_zero_time():
    t1 = datetime.now()
    p1 = {"timestamp": t1}
    p2 = {"timestamp": t1, "distance_from_previous": 100.0}
    assert estimate_speed(p1, p2) == 0.0

# Tests for services/route_processor.py
def test_simplify_route():
    processor = RouteProcessor()
    # A straight line with a point in the middle that should be removed
    points = [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)]
    simplified = processor.simplify_route(points, tolerance=0.1)
    assert len(simplified) == 2
    assert simplified[0] == (0.0, 0.0)
    assert simplified[-1] == (1.0, 1.0)

def test_encode_decode_polyline():
    processor = RouteProcessor()
    points = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    encoded = processor.encode_polyline(points)
    assert isinstance(encoded, str)
    assert len(encoded) > 0
    
    decoded = processor.decode_polyline(encoded)
    # Polyline encoding has some precision loss, so we check if close
    assert len(decoded) == len(points)
    for p1, p2 in zip(points, decoded):
        assert abs(p1[0] - p2[0]) < 0.0001
        assert abs(p1[1] - p2[1]) < 0.0001
