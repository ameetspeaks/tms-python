#!/usr/bin/env python3
"""
Deploy TMS Tracking API to Hugging Face Spaces with automatic cron job setup.
This script helps configure the Hugging Face Space for automatic cron job execution.
"""

import os
import subprocess
import json
import sys
from pathlib import Path

def check_hf_cli():
    """Check if Hugging Face CLI is installed."""
    try:
        result = subprocess.run(['huggingface-cli', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Hugging Face CLI found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Hugging Face CLI not found. Please install it:")
        print("   pip install huggingface_hub")
        print("   huggingface-cli login")
        return False

def create_space_config():
    """Create Hugging Face Space configuration."""
    config = {
        "title": "TMS Tracking API",
        "emoji": "🚛",
        "colorFrom": "blue",
        "colorTo": "green",
        "sdk": "docker",
        "app_port": 7860,
        "env": {
            "VERCEL_API_URL": "https://tms-navy-one.vercel.app",
            "CRON_SECRET": "AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A",
            "ENABLE_CRON": "true",
            "OSRM_API_URL": "http://router.project-osrm.org",
            "LOG_LEVEL": "INFO"
        }
    }
    
    config_path = Path("README.md")
    
    # Read existing README
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update the YAML frontmatter with environment variables
        if "---" in content:
            parts = content.split("---")
            if len(parts) >= 3:
                # Update the YAML config
                yaml_config = []
                yaml_config.append("---")
                yaml_config.append(f"title: {config['title']}")
                yaml_config.append(f"emoji: {config['emoji']}")
                yaml_config.append(f"colorFrom: {config['colorFrom']}")
                yaml_config.append(f"colorTo: {config['colorTo']}")
                yaml_config.append(f"sdk: {config['sdk']}")
                yaml_config.append(f"app_port: {config['app_port']}")
                yaml_config.append("")
                
                # Add environment variables section
                yaml_config.append("**Environment Variables Required:**")
                yaml_config.append("")
                for key, value in config['env'].items():
                    yaml_config.append(f"- `{key}`: {value}")
                yaml_config.append("")
                yaml_config.append("---")
                
                # Combine with the rest of the content
                new_content = "\n".join(yaml_config) + parts[2]
                
                with open(config_path, 'w') as f:
                    f.write(new_content)
                
                print("✅ Updated README.md with environment configuration")
                return True
    
    return False

def create_deployment_instructions():
    """Create deployment instructions."""
    instructions = """
# 🚀 Deploying TMS Tracking API to Hugging Face Spaces

## Prerequisites
1. Install Hugging Face CLI:
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

2. Create a new Space on Hugging Face:
   - Go to https://huggingface.co/spaces/new
   - Choose "Docker" as SDK
   - Set repository name as "tms"
   - Make it private (recommended)

## Deployment Steps

### Option 1: Manual Upload
1. Clone your Hugging Face Space:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/tms
   cd tms
   ```

2. Copy all files from this python folder:
   ```bash
   cp -r /path/to/tmsfinal/python/* .
   ```

3. Configure environment variables:
   - Go to your Space settings: https://huggingface.co/spaces/YOUR_USERNAME/tms/settings
   - Add these environment variables:
     ```
     VERCEL_API_URL=https://tms-navy-one.vercel.app
     CRON_SECRET=AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A
     ENABLE_CRON=true
     OSRM_API_URL=http://router.project-osrm.org
     LOG_LEVEL=INFO
     ```

4. Commit and push:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push
   ```

### Option 2: Using Hugging Face CLI
```bash
# Create space and push in one command
huggingface-cli repo create tms --type space --sdk docker --private
git clone https://huggingface.co/spaces/YOUR_USERNAME/tms
cd tms
cp -r /path/to/tmsfinal/python/* .
git add .
git commit -m "Initial deployment"
git push
```

## Verification

After deployment, verify the cron jobs are running:

1. Check API health: https://YOUR_USERNAME-tms.hf.space/health
2. Check cron status: https://YOUR_USERNAME-tms.hf.space/api/cron/status
3. Monitor logs in the Space interface

## Expected Behavior

- Location poll runs every minute
- Consent poll runs every hour
- Both jobs call your Vercel API endpoints
- Logs are visible in the Space interface

## Troubleshooting

### Cron Jobs Not Running
1. Check if `ENABLE_CRON=true` is set
2. Verify `CRON_SECRET` matches your Vercel environment
3. Check Space logs for errors

### API Calls Failing
1. Verify `VERCEL_API_URL` is correct
2. Check if your Vercel API is accessible
3. Test endpoints manually using curl

### Authentication Issues
1. Ensure `CRON_SECRET` matches exactly between Vercel and HuggingFace
2. Check authorization headers in logs

## Manual Testing

Test the cron jobs manually:
```bash
# Test location poll
curl -X POST https://YOUR_USERNAME-tms.hf.space/api/trigger/location-poll \
  -H "Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"

# Test consent poll
curl -X POST https://YOUR_USERNAME-tms.hf.space/api/trigger/consent-poll \
  -H "Authorization: Bearer AIC0E35w_6wXDYIz0nVtZHN59z5fUZp4o7c0bz8lz5A"
```

"""
    
    with open("DEPLOYMENT.md", "w") as f:
        f.write(instructions)
    
    print("✅ Created DEPLOYMENT.md with detailed instructions")

def main():
    """Main deployment function."""
    print("🚀 TMS Tracking API - Hugging Face Spaces Deployment")
    print("=" * 60)
    
    # Check prerequisites
    if not check_hf_cli():
        return False
    
    # Create configuration
    if create_space_config():
        print("✅ Configuration updated successfully")
    else:
        print("⚠️  Could not update configuration automatically")
    
    # Create deployment instructions
    create_deployment_instructions()
    
    print("\n✅ Deployment preparation complete!")
    print("\nNext steps:")
    print("1. Follow the instructions in DEPLOYMENT.md")
    print("2. Set up your Hugging Face Space")
    print("3. Configure environment variables")
    print("4. Deploy and verify cron jobs are running")
    print("\nThe cron jobs will automatically:")
    print("- Poll location data every minute")
    print("- Poll consent data every hour")
    print("- Call your Vercel API endpoints")
    print("- Keep your tracking data up to date")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)