#!/usr/bin/env python3
"""
Test script to verify Hugging Face Space cron job functionality.
This script tests the TMS Tracking API endpoints to ensure cron jobs are working.
"""

import requests
import json
import time
from datetime import datetime

def test_space_endpoints():
    """Test the Hugging Face Space endpoints."""
    base_url = "https://ameetspeaks-tms.hf.space"
    cron_secret = "AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"
    
    print(f"🚀 Testing TMS Tracking API - {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Cron enabled: {health_data.get('cron_jobs', {}).get('enabled')}")
            print(f"   Scheduler running: {health_data.get('cron_jobs', {}).get('scheduler_running')}")
            print(f"   Active jobs: {health_data.get('cron_jobs', {}).get('jobs', [])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    print()
    
    # Test 2: Cron Status
    print("2. Testing cron status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/cron/status", timeout=10)
        if response.status_code == 200:
            cron_data = response.json()
            print(f"✅ Cron status retrieved")
            print(f"   Enabled: {cron_data.get('enabled')}")
            print(f"   Running: {cron_data.get('running')}")
            if cron_data.get('jobs'):
                for job in cron_data['jobs']:
                    print(f"   Job: {job.get('id')} - {job.get('name')}")
                    print(f"     Next run: {job.get('next_run')}")
                    print(f"     Trigger: {job.get('trigger')}")
        else:
            print(f"❌ Cron status failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Cron status error: {str(e)}")
    
    print()
    
    # Test 3: Manual Location Poll Trigger
    print("3. Testing manual location poll trigger...")
    try:
        headers = {
            "Authorization": f"Bearer {cron_secret}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{base_url}/api/trigger/location-poll", 
            headers=headers, 
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Location poll triggered successfully")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Timestamp: {result.get('timestamp')}")
        else:
            print(f"❌ Location poll trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Location poll trigger error: {str(e)}")
    
    print()
    
    # Test 4: Manual Consent Poll Trigger
    print("4. Testing manual consent poll trigger...")
    try:
        headers = {
            "Authorization": f"Bearer {cron_secret}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{base_url}/api/trigger/consent-poll", 
            headers=headers, 
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consent poll triggered successfully")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Timestamp: {result.get('timestamp')}")
        else:
            print(f"❌ Consent poll trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Consent poll trigger error: {str(e)}")
    
    print()
    print("=" * 60)
    print("✅ Testing completed!")
    print("\nIf all tests passed, your cron job automation is working correctly.")
    print("The system will automatically:")
    print("- Poll location data every minute")
    print("- Poll consent data every hour")
    print("- Call your Vercel API endpoints")
    print("- Keep your tracking data synchronized")

def test_vercel_endpoints():
    """Test the Vercel API endpoints that the cron jobs call."""
    vercel_url = "https://tms-navy-one.vercel.app"
    cron_secret = "AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"
    
    print("\n🔍 Testing Vercel API Endpoints")
    print("=" * 40)
    
    # Test location poll endpoint
    print("Testing Vercel location poll endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {cron_secret}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{vercel_url}/api/cron/location-poll", 
            headers=headers, 
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Vercel location poll working")
            print(f"   Message: {result.get('message')}")
            print(f"   Processed: {result.get('processed')}")
            print(f"   Errors: {result.get('errors')}")
        else:
            print(f"❌ Vercel location poll failed")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Vercel location poll error: {str(e)}")

if __name__ == "__main__":
    test_space_endpoints()
    test_vercel_endpoints()