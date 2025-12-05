import asyncio
import httpx
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERCEL_API_URL = os.getenv("VERCEL_API_URL", "https://tms-navy-one.vercel.app")
CRON_SECRET = os.getenv("CRON_SECRET", "")

class CronJobRunner:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def location_poll(self):
        """Poll location data from Telenity every minute"""
        try:
            logger.info("🔄 Starting location poll...")
            
            response = await self.client.post(
                f"{VERCEL_API_URL}/api/cron/location-poll",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {CRON_SECRET}"
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Location poll successful: {response.json()}")
            else:
                logger.error(f"❌ Location poll failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Location poll error: {str(e)}")
    
    async def consent_poll(self):
        """Poll consent data from Telenity every hour"""
        try:
            logger.info("🔄 Starting consent poll...")
            
            response = await self.client.post(
                f"{VERCEL_API_URL}/api/telenity/consent/poll",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {CRON_SECRET}"
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Consent poll successful: {response.json()}")
            else:
                logger.error(f"❌ Consent poll failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Consent poll error: {str(e)}")
    
    async def close(self):
        await self.client.aclose()

# Singleton instance
cron_runner = CronJobRunner()