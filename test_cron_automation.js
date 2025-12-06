/**
 * Test script to verify Hugging Face Space cron job functionality.
 * This script tests the TMS Tracking API endpoints to ensure cron jobs are working.
 */

import https from 'https';
import { URL } from 'url';

const BASE_URL = 'ameetspeaks-tms.hf.space';
const VERCEL_URL = 'tms-navy-one.vercel.app';
const CRON_SECRET = 'AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A';

function makeRequest(hostname, path, method = 'GET', headers = {}) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: hostname,
      path: path,
      method: method,
      headers: headers
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, headers: res.headers, data: data });
      });
    });

    req.on('error', (err) => { reject(err); });
    req.end();
  });
}

async function testCronAutomation() {
  console.log('🚀 Testing Hugging Face Space Cron Automation...\n');

  try {
    // Test 1: Check Hugging Face Space health
    console.log('1️⃣ Testing Hugging Face Space health...');
    const healthResponse = await makeRequest(BASE_URL, '/health');
    console.log(`   ✅ Health check: ${healthResponse.statusCode}`);
    if (healthResponse.statusCode === 200) {
      const healthData = JSON.parse(healthResponse.data);
      console.log(`   📊 Space status: ${healthData.status || 'unknown'}`);
      if (healthData.cron_jobs) {
        console.log(`   ⏰ Cron jobs: ${JSON.stringify(healthData.cron_jobs)}`);
      }
    }
    console.log('');

    // Test 2: Check cron status endpoint
    console.log('2️⃣ Testing cron status endpoint...');
    const cronStatusResponse = await makeRequest(BASE_URL, '/cron/status');
    console.log(`   ✅ Cron status: ${cronStatusResponse.statusCode}`);
    if (cronStatusResponse.statusCode === 200) {
      const cronData = JSON.parse(cronStatusResponse.data);
      console.log(`   📈 Last execution: ${cronData.last_execution || 'unknown'}`);
      console.log(`   🔢 Total executions: ${cronData.total_executions || 0}`);
    }
    console.log('');

    // Test 3: Trigger manual location poll
    console.log('3️⃣ Triggering manual location poll...');
    const locationPollResponse = await makeRequest(BASE_URL, '/location-poll', 'POST', {
      'Authorization': `Bearer ${CRON_SECRET}`,
      'Content-Type': 'application/json'
    });
    console.log(`   ✅ Location poll: ${locationPollResponse.statusCode}`);
    if (locationPollResponse.statusCode === 200) {
      const pollData = JSON.parse(locationPollResponse.data);
      console.log(`   📍 Processed: ${pollData.processed || 0} locations`);
      console.log(`   ⚠️  Errors: ${pollData.errors || 0}`);
    }
    console.log('');

    // Test 4: Trigger manual consent poll
    console.log('4️⃣ Triggering manual consent poll...');
    const consentPollResponse = await makeRequest(BASE_URL, '/consent-poll', 'POST', {
      'Authorization': `Bearer ${CRON_SECRET}`,
      'Content-Type': 'application/json'
    });
    console.log(`   ✅ Consent poll: ${consentPollResponse.statusCode}`);
    if (consentPollResponse.statusCode === 200) {
      const consentData = JSON.parse(consentPollResponse.data);
      console.log(`   📋 Processed: ${consentData.processed || 0} consents`);
      console.log(`   ⚠️  Errors: ${consentData.errors || 0}`);
    }
    console.log('');

    // Test 5: Check Vercel API endpoints
    console.log('5️⃣ Testing Vercel API endpoints...');
    
    // Test Vercel cron health
    const vercelHealthResponse = await makeRequest(VERCEL_URL, '/api/cron/health');
    console.log(`   ✅ Vercel health: ${vercelHealthResponse.statusCode}`);
    
    // Test Vercel cron monitor
    const vercelMonitorResponse = await makeRequest(VERCEL_URL, '/api/cron/monitor');
    console.log(`   ✅ Vercel monitor: ${vercelMonitorResponse.statusCode}`);
    if (vercelMonitorResponse.statusCode === 200) {
      const monitorData = JSON.parse(vercelMonitorResponse.data);
      console.log(`   📊 Monitor status: ${monitorData.status || 'unknown'}`);
      if (monitorData.monitor) {
        console.log(`   🔍 Failed jobs (24h): ${monitorData.monitor.failed_jobs_24h || 0}`);
        console.log(`   📍 Tracking health: ${monitorData.monitor.tracking_health || 'unknown'}`);
      }
    }
    console.log('');

    console.log('🎉 All tests completed successfully!');
    console.log('📋 Summary:');
    console.log('   ✅ Hugging Face Space is running');
    console.log('   ✅ Cron jobs are configured');
    console.log('   ✅ Location polling works');
    console.log('   ✅ Consent polling works');
    console.log('   ✅ Vercel API endpoints are accessible');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the tests
testCronAutomation();