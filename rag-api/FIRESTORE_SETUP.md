# Firestore Setup Guide

This guide explains how to set up and use Firestore for production storage in Jarvis.

## Prerequisites

1. Google Cloud Platform (GCP) account
2. GCP project with Firestore enabled
3. Service account with Firestore permissions

## Setup Steps

### 1. Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2. Enable Firestore

1. Navigate to Firestore in the GCP Console
2. Create a database (Native mode recommended)
3. Choose a location (e.g., `us-central`)
4. Wait for database creation to complete

### 3. Create Service Account

1. Go to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Name it (e.g., `jarvis-firestore`)
4. Grant role: **Cloud Datastore User** (for Firestore)
5. Click "Done"

### 4. Create and Download Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose JSON format
5. Download the key file
6. **Keep this file secure!**

### 5. Configure Environment Variables

Add to your `.env` file:

```bash
# Enable Firestore
USE_FIRESTORE_SESSIONS=true
GOOGLE_CLOUD_PROJECT=your-project-id
FIRESTORE_SESSIONS_COLLECTION=live_sessions

# Path to service account key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 6. Install Dependencies

```bash
pip install google-cloud-firestore
```

Or add to `requirements.txt`:
```
google-cloud-firestore>=2.11.0
```

### 7. Test Connection

Start your server:
```bash
cd rag-api
uvicorn app:app --reload
```

You should see:
```
✅ Using Firestore for live session storage
```

## Firestore Collections

The application will automatically create the following collections:

- **`live_sessions`** - Stores live session data

### Collection Structure

**live_sessions** document structure:
```json
{
  "id": "session-uuid",
  "user_id": "user123",
  "mode": "LS1A",
  "state": "LIVE",
  "started_at": "2025-12-25T10:00:00Z",
  "paused_at": null,
  "ended_at": null,
  "transcript_partial": "Hello, how can I help?",
  "transcript_final": null,
  "audio_minutes_used": 2.5,
  "frames_processed": 0,
  "daily_budget_remaining": {
    "audioMin": 57.5,
    "videoTokens": 50000.0,
    "screenTokens": 50000.0
  },
  "recording_consent": false,
  "secrets_blurred": [],
  "transcript_url": null,
  "recording_url": null
}
```

## Security Best Practices

1. **Never commit service account keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly**
4. **Use least privilege** - only grant necessary permissions
5. **Enable audit logging** in GCP Console
6. **Set up alerts** for unusual activity

## Firestore Security Rules

Set up Firestore security rules to protect your data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Live sessions - users can only access their own sessions
    match /live_sessions/{sessionId} {
      allow read, write: if request.auth != null 
        && resource.data.user_id == request.auth.uid;
      allow create: if request.auth != null 
        && request.resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Monitoring

### View Data in Console

1. Go to Firestore in GCP Console
2. Navigate to your collection
3. View documents and query data

### Set Up Alerts

1. Go to Monitoring > Alerting
2. Create alert for:
   - High read/write rates
   - Error rates
   - Storage usage

## Migration from In-Memory

If you're migrating from in-memory storage:

1. **Backup existing data** (if any)
2. **Set environment variables** as shown above
3. **Restart the server**
4. **Verify** new sessions are being stored in Firestore
5. **Monitor** for any errors

## Troubleshooting

### Error: "Failed to initialize Firestore"

**Possible causes:**
- Missing `GOOGLE_APPLICATION_CREDENTIALS`
- Invalid service account key
- Insufficient permissions
- Firestore not enabled in project

**Solutions:**
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file
2. Check service account has "Cloud Datastore User" role
3. Verify Firestore is enabled in GCP Console
4. Check project ID is correct

### Error: "Permission denied"

**Solution:**
- Grant "Cloud Datastore User" role to service account
- Verify service account key is correct

### Fallback to In-Memory

If Firestore initialization fails, the app will automatically fall back to in-memory storage. Check logs for error messages.

## Cost Considerations

Firestore pricing:
- **Free tier**: 50K reads, 20K writes, 20K deletes per day
- **Paid**: $0.06 per 100K document reads, $0.18 per 100K writes

Monitor usage in GCP Console > Firestore > Usage

## Next Steps

- Set up BigQuery for memory storage (optional)
- Configure Firestore security rules
- Set up monitoring and alerts
- Plan for scaling

