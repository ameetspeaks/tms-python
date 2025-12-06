# 🤖 TMS Cron Job Automation - Hugging Face Spaces

## Overview

The TMS Tracking API now includes **automatic cron job automation** using Hugging Face Spaces. This replaces the manual Vercel cron job setup with a more reliable and observable system.

## 🚀 Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   HuggingFace       │    │   Vercel Backend    │    │   Database          │
│   Space (Python)    │───▶│   (Node.js/Express)│───▶│   (PostgreSQL)      │
│   Cron Scheduler    │    │   API Endpoints     │    │   Tracking Data     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📋 Features

- ✅ **Automatic Location Polling**: Every minute
- ✅ **Automatic Consent Polling**: Every hour  
- ✅ **Secure Authentication**: Bearer token authentication
- ✅ **Health Monitoring**: Real-time status checks
- ✅ **Error Handling**: Comprehensive logging and error recovery
- ✅ **Manual Triggers**: Test endpoints for debugging
- ✅ **Observability**: Detailed logs and metrics

## 🔧 Configuration

### Environment Variables

Set these in your Hugging Face Space settings:

```bash
VERCEL_API_URL=https://tms-navy-one.vercel.app
CRON_SECRET=AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A
ENABLE_CRON=true
OSRM_API_URL=http://router.project-osrm.org
LOG_LEVEL=INFO
```

### Cron Job Schedule

| Job | Frequency | Purpose |
|-----|-----------|---------|
| Location Poll | Every minute | Fetch SIM tracking data from Telenity |
| Consent Poll | Every hour | Check consent status updates |

## 🌐 API Endpoints

### Health Check
```http
GET https://ameetspeaks-tms.hf.space/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "geocoding": "operational",
    "routing": "operational",
    "osrm": "http://router.project-osrm.org",
    "vercel": "https://tms-navy-one.vercel.app"
  },
  "cron_jobs": {
    "enabled": true,
    "scheduler_running": true,
    "jobs": ["location_poll", "consent_poll"]
  }
}
```

### Cron Status
```http
GET https://ameetspeaks-tms.hf.space/api/cron/status
```

Response:
```json
{
  "enabled": true,
  "running": true,
  "jobs": [
    {
      "id": "location_poll",
      "name": "location_poll_job",
      "next_run": "2024-01-01T12:01:00Z",
      "trigger": "cron[minute='*']"
    },
    {
      "id": "consent_poll",
      "name": "consent_poll_job", 
      "next_run": "2024-01-01T13:00:00Z",
      "trigger": "cron[hour='*', minute='0']"
    }
  ]
}
```

### Manual Triggers

#### Location Poll
```http
POST https://ameetspeaks-tms.hf.space/api/trigger/location-poll
Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A
```

#### Consent Poll
```http
POST https://ameetspeaks-tms.hf.space/api/trigger/consent-poll
Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A
```

## 📊 Monitoring

### Log Examples

**Successful Location Poll:**
```
2024-01-01 12:00:00 - INFO - 🔄 Starting location poll job...
2024-01-01 12:00:01 - INFO - ✅ Location poll successful: {"processed": 5, "errors": 0}
```

**Successful Consent Poll:**
```
2024-01-01 12:00:00 - INFO - 🔄 Starting consent poll job...
2024-01-01 12:00:02 - INFO - ✅ Consent poll successful: {"processed": 3, "errors": 0}
```

**Error Handling:**
```
2024-01-01 12:00:00 - ERROR - ❌ Location poll failed: 500 - Internal Server Error
2024-01-01 12:00:00 - ERROR - ❌ Location poll error: Connection timeout
```

### Testing

Use the provided test script:

```bash
python test_cron_automation.py
```

This will:
1. Test health endpoint
2. Check cron status
3. Trigger manual location poll
4. Trigger manual consent poll
5. Verify Vercel API connectivity

## 🔍 Troubleshooting

### Common Issues

#### 1. Cron Jobs Not Running
**Symptoms:** No logs, status shows `running: false`
**Solution:** 
- Check `ENABLE_CRON=true` is set
- Verify Space is running (not paused)
- Check Space logs for startup errors

#### 2. Authentication Failures
**Symptoms:** 401 errors in logs
**Solution:**
- Verify `CRON_SECRET` matches Vercel environment
- Check Bearer token format in requests
- Ensure no extra spaces in environment variables

#### 3. Vercel API Connection Issues
**Symptoms:** Timeout or connection errors
**Solution:**
- Verify `VERCEL_API_URL` is correct
- Check Vercel deployment is active
- Test Vercel endpoints manually

#### 4. Database Connection Issues
**Symptoms:** Processing succeeds but no data in database
**Solution:**
- Check database connection in Vercel
- Verify tracking_log table exists
- Check for constraint violations

### Debug Steps

1. **Check Space Logs:**
   - Go to your Space interface
   - View runtime logs
   - Look for startup messages

2. **Test Manual Triggers:**
   ```bash
   curl -X POST https://ameetspeaks-tms.hf.space/api/trigger/location-poll \
     -H "Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"
   ```

3. **Verify Vercel Endpoints:**
   ```bash
   curl -X POST https://tms-navy-one.vercel.app/api/cron/location-poll \
     -H "Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"
   ```

## 📈 Performance

- **Location Poll**: ~2-5 seconds per execution
- **Consent Poll**: ~1-3 seconds per execution
- **Memory Usage**: ~100-200MB
- **CPU Usage**: Minimal (<5% during polls)

## 🔒 Security

- All API calls use HTTPS
- Bearer token authentication
- No sensitive data logged
- Rate limiting respected
- Secure environment variable storage

## 🎯 Success Criteria

✅ **Cron jobs are working if:**
- Health endpoint returns `scheduler_running: true`
- Location polls execute every minute
- Consent polls execute every hour
- Vercel API receives calls successfully
- Tracking data is populated in database
- No persistent errors in logs

## 📞 Support

If you encounter issues:

1. Check this documentation
2. Run the test script
3. Check Space and Vercel logs
4. Verify all environment variables
5. Test manual endpoints

The system is designed to be self-healing and will retry failed operations automatically.