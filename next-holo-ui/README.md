# Jarvis Holo UI (Next.js)

Touch-friendly, holographic-inspired frontend for the existing FastAPI + Gemini Live backend. Includes chat, artifact viewer, and real-time audio/video streaming to `/gemini-live/ws/{session_id}`.

## Prereqs
- Node.js 18+ and npm (or pnpm/yarn).
- Backend base URL (e.g., your Cloud Run FastAPI service) exposed over HTTPS.

## Quick start
```bash
cd next-holo-ui
npm install
npm run dev
```
Open http://localhost:3000 and set the API base in Settings.

## Environment
- Set `NEXT_PUBLIC_API_BASE` to your backend (HTTPS), e.g.:
  ```
  NEXT_PUBLIC_API_BASE=https://rag-api-883324649002.us-central1.run.app
  ```
- For local dev, copy `.env.example` to `.env.local` and edit as needed.

## Deploy (Vercel)
**Dashboard path**
1) Push this folder to a repo.  
2) In Vercel, import the repo.  
3) Set env var `NEXT_PUBLIC_API_BASE` to your Cloud Run backend URL.  
4) Deploy; after deploy, open Settings in the UI to confirm the base URL.

**CLI quick path**
```bash
npm i -g vercel
vercel login
vercel --prod --yes --env NEXT_PUBLIC_API_BASE=https://rag-api-883324649002.us-central1.run.app --build-env NEXT_PUBLIC_API_BASE=https://rag-api-883324649002.us-central1.run.app
```
Notes:
- `--yes` accepts defaults; remove it if you want interactive prompts.
- `--build-env` ensures the same value during build.
- First run will ask to create/link the project and select scope.

## Features mapped to backend
- Chat → POST `/query`.
- Upload → POST `/upload` (PDF/DOCX/TXT/MD).
- Health check → GET `/health`.
- Gemini Live → POST `/gemini-live/create-session`, then WS `/gemini-live/ws/{session_id}`.

## Notes
- Mic/camera capture runs client-side; audio chunks and video frames are sent Base64 over WS.
- Keys entered in Settings are stored locally (browser localStorage) only.

