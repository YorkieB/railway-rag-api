# Environment Variables Setup Guide

This guide lists all environment variables needed for the Jarvis RAG API.

## Quick Start

1. Copy the template below to create your `.env` file
2. Fill in your actual API keys
3. Never commit `.env` to version control

## Required Environment Variables

### Core API Configuration
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

### Database Configuration
```bash
CHROMADB_RAG_DIR=./rag_db
CHROMADB_INDEX_DIR=./index_db
CHROMADB_MEMORY_DIR=./memory_db
```

### Image Generation APIs
```bash
# OpenAI DALL-E (uses OPENAI_API_KEY)
IMAGE_GENERATION_PROVIDER=openai

# Stability AI
STABILITY_API_KEY=your_stability_api_key_here

# Replicate
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

### Spotify Integration
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/callback
```

### Music Creation APIs
```bash
SUNO_API_KEY=your_suno_api_key_here
MUSIC_CREATION_PROVIDER=suno
```

### Social Media APIs
```bash
# Twitter/X
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

# Facebook
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# Instagram
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
```

### Production Database Configuration
```bash
# Enable Firestore for live sessions
USE_FIRESTORE_SESSIONS=true
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
FIRESTORE_SESSIONS_COLLECTION=live_sessions

# Enable BigQuery for memory storage (optional)
USE_BIGQUERY_MEMORY=false
BIGQUERY_DATASET=jarvis
BIGQUERY_MEMORY_TABLE=memories

# Google Cloud Authentication
# Option 1: Service Account Key File
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Option 2: Use default credentials (if running on GCP)
# No GOOGLE_APPLICATION_CREDENTIALS needed
```

### Performance - Redis Caching
```bash
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379
REDIS_DEFAULT_TTL=3600
REDIS_KEY_PREFIX=jarvis:
CACHE_TTL=300
```

### Other Configuration
```bash
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
LOG_JSON=false
SOUND_EFFECTS_LIBRARY=./sound_effects
WORD_PROCESSOR_EXPORT_DIR=./exports
```

## Security Configuration

### JWT Authentication
```bash
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24
```

### Rate Limiting
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_REQUESTS_PER_DAY=10000
```

## Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `OPENAI_API_KEY`

### Spotify
1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Get Client ID and Client Secret
4. Set redirect URI to match `SPOTIFY_REDIRECT_URI`

### Stability AI
1. Go to https://platform.stability.ai/
2. Create an account and get API key

### Replicate
1. Go to https://replicate.com/
2. Get API token from account settings

### Social Media APIs
- **Twitter**: https://developer.twitter.com/en/portal/dashboard
- **Facebook**: https://developers.facebook.com/
- **Instagram**: https://developers.facebook.com/docs/instagram-api
- **LinkedIn**: https://www.linkedin.com/developers/

## Security Notes

1. **Never commit `.env` files** to version control
2. Use environment-specific files (`.env.development`, `.env.production`)
3. Rotate API keys regularly
4. Use secret management services in production (AWS Secrets Manager, GCP Secret Manager)

