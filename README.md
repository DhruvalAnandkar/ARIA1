# ARIA — Adaptive Real-time Intelligence Assistant

A universal accessibility app with two modes:

- **SIGN Mode** — For deaf/mute users: ASL hand sign recognition + facial emotion detection → natural sentence → emotion-matched voice output via ElevenLabs
- **GUIDE Mode** — For blind users: camera-based obstacle detection + turn-by-turn walking navigation with voice guidance

React Native (Expo) mobile app connected to a FastAPI backend running on a Jetson Orin Nano Super. All AI processing runs on the Jetson. Data stored in a single SQLite file — no external databases required.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Get Your API Keys](#2-get-your-api-keys)
3. [Backend Setup (Jetson)](#3-backend-setup-jetson)
4. [Verify Backend](#4-verify-backend)
5. [Mobile App Setup](#5-mobile-app-setup)
6. [Cross-Network Setup (Tunnel)](#6-cross-network-setup-tunnel)
7. [Test: Registration & Login](#7-test-registration--login)
8. [Test: SIGN Mode](#8-test-sign-mode)
9. [Test: GUIDE Mode — Obstacle Detection](#9-test-guide-mode--obstacle-detection)
10. [Test: GUIDE Mode — Navigation](#10-test-guide-mode--navigation)
11. [Test: SOS Emergency](#11-test-sos-emergency)
12. [Test: Profile & Preferences](#12-test-profile--preferences)
13. [Run Backend Unit Tests](#13-run-backend-unit-tests)
14. [Development Mode (Hot Reload)](#14-development-mode-hot-reload)
15. [API Reference (Quick)](#15-api-reference-quick)
16. [Architecture](#16-architecture)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Prerequisites

**On the Jetson Orin Nano Super:**
- Ubuntu 22.04, CUDA 12.6
- Python 3.10+
- System libraries: `libgl1-mesa-glx`, `libglib2.0-0` (for OpenCV/MediaPipe)
- At least 4GB free RAM, 5GB free disk

**On your development machine (laptop/desktop):**
- Node.js 18+ and npm
- **Expo Go** app installed on your phone (iOS App Store / Google Play Store)

**Verify Python on Jetson:**
```bash
ssh jetson
python3 --version   # Should be 3.10+
pip3 --version
```

If you need the system libraries:
```bash
sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0
```

---

## 2. Get Your API Keys

You need **at least one** vision API key. Get as many as you can for fallback reliability.

| Service | Get Key At | Required? |
|---|---|---|
| Google Gemini | https://aistudio.google.com/apikey | At least one vision API |
| OpenAI | https://platform.openai.com/api-keys | Fallback |
| Anthropic | https://console.anthropic.com/ | Fallback |
| ElevenLabs | https://elevenlabs.io/ (free tier works) | Yes — for voice output |
| Google Maps | https://console.cloud.google.com/ (enable Directions API) | Yes — for navigation |

---

## 3. Backend Setup (Jetson)

### 3.1 — Clone the repo onto the Jetson

```bash
ssh jetson
cd ~
git clone <your-repo-url> ARIA
cd ARIA/backend
```

### 3.2 — Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.3 — Create the environment file

```bash
cp .env.example .env
nano .env
```

Fill in your actual values:

```env
# API Keys — paste your real keys here
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=xi-...
GOOGLE_MAPS_API_KEY=AIza...

# Auth (generate a random string: openssl rand -hex 32)
JWT_SECRET=your-random-secret-here

# Vision fallback order
VISION_PROVIDER_ORDER=gemini,openai,claude,local

# Debug
DEBUG=false
```

Save and exit (`Ctrl+X`, `Y`, `Enter` in nano).

### 3.4 — Start the backend

```bash
bash run.sh
```

Or manually:
```bash
source venv/bin/activate
mkdir -p audio_output
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Wait until you see:
```
INFO  aria_backend_ready
```

The database (SQLite) is created automatically on first startup — no migrations needed.

---

## 4. Verify Backend

### 4.1 — Basic health check

```bash
# From the Jetson itself:
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "version": "1.0.0", "uptime_seconds": 42.5}
```

### 4.2 — Detailed service health

```bash
curl http://localhost:8000/health/services
```

Expected response:
```json
{
  "database": "ok",
  "vision_providers": {
    "gemini": true,
    "openai": true,
    "claude": true,
    "local": false
  }
}
```

`local: false` is normal if YOLOv8 weights haven't been downloaded yet. The cloud providers are what matter.

### 4.3 — Check from your laptop

Find the Jetson's IP:
```bash
# On the Jetson:
hostname -I
# Example output: 192.168.55.1 ...
```

From your laptop (must be on the same network):
```bash
curl http://192.168.55.1:8000/health
```

---

## 5. Mobile App Setup

### 5.1 — Install dependencies

On your **development machine** (not the Jetson):

```bash
cd ARIA/mobile
npm install
```

### 5.2 — Configure backend URL

The app defaults to `http://192.168.55.1:8000`. You can change the URL in two ways:

**Option A — In-app (recommended):** Go to the **Profile** tab in the app and enter the Jetson's IP or tunnel URL in the Server URL field. This persists across app restarts.

**Option B — Environment variable:** Set before starting Expo:
```bash
EXPO_PUBLIC_BACKEND_URL=http://<jetson-ip>:8000 npx expo start
```

**Option C — Edit config file:** Edit `mobile/src/constants/config.ts`:
```typescript
export const BACKEND_URL = "http://<jetson-ip>:8000";
```

### 5.3 — Start the Expo dev server

```bash
npx expo start
```

You'll see a QR code in the terminal.

### 5.4 — Open on your phone

1. Open **Expo Go** on your phone
2. Scan the QR code
3. The app should load and show the ARIA login screen

If the QR code doesn't scan, try pressing `s` in the terminal to switch to Expo Go mode, then scan again.

---

## 6. Cross-Network Setup (Tunnel)

If your Jetson and phone are on **different networks** (e.g., Jetson on eduroam, phone on mobile data), you need a tunnel to give the backend a public URL.

### Option A — Cloudflare Tunnel (free, no account needed)

On the Jetson:
```bash
# Install cloudflared (one time)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Start the tunnel (run alongside the backend)
cloudflared tunnel --url http://localhost:8000
```

Cloudflared will print a public URL like:
```
https://random-words.trycloudflare.com
```

### Option B — ngrok

```bash
# Install ngrok and authenticate (one time)
# Then:
ngrok http 8000
```

### Use the tunnel URL on your phone

1. Open the ARIA app on your phone
2. Go to the **Profile** tab
3. Paste the tunnel URL (e.g. `https://random-words.trycloudflare.com`) into the **Server URL** field
4. Tap **Save**
5. The status dot should turn green — you're connected

This works from **any network** — mobile data, different WiFi, hotspot, etc.

---


## 7. API Reference (Quick)

All endpoints (except health and auth) require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Basic health check |
| `GET` | `/health/services` | Detailed service status |
| `POST` | `/auth/register` | Register `{email, password, name}` |
| `POST` | `/auth/login` | Login `{email, password}` → `{token}` |
| `GET` | `/user/profile` | Get user profile |
| `PATCH` | `/user/profile` | Update profile |
| `GET` | `/user/preferences` | Get user preferences |
| `PATCH` | `/user/preferences` | Update preferences |
| `WS` | `/ws/sign?token=X` | Real-time SIGN mode (send frames, receive letters/sentences) |
| `POST` | `/sign/speak` | Manual TTS `{text, emotion}` |
| `POST` | `/sign/sos` | Trigger SOS emergency |
| `GET` | `/sign/transcript?session_id=X` | Get session transcript |
| `POST` | `/guide/obstacle` | Obstacle detection `{frame}` |
| `POST` | `/guide/navigate` | Get walking directions `{lat, lng, destination}` |
| `WS` | `/ws/guide/nav?token=X&route_id=Y` | Real-time nav step advancement |
| `POST` | `/guide/speak` | Guide mode TTS `{text}` |
| `GET` | `/audio/{filename}` | Serve generated audio files |

Interactive API docs available at: `http://<jetson-ip>:8000/docs`

---

## 8. Architecture

```
Phone (Expo)                          Jetson Orin Nano
┌──────────────┐                     ┌───────────────────────────────────┐
│  SIGN Screen │──WebSocket──────────│──► FastAPI + Uvicorn (:8000)     │
│  (phone cam) │   frames @ 10fps   │       │                           │
│              │                     │       ├── SQLite (aria.db)        │
│  GUIDE Screen│──REST + WS─────────│───────┤   users, transcripts,     │
│  (phone cam) │   obstacle frames  │       │   navigation, preferences │
│              │   location updates  │       │                           │
│  Profile     │──REST──────────────│───────┤── In-memory sessions      │
│  (server URL)│                     │       │   (sign mode buffers)     │
└──────────────┘                     │       │                           │
                                     │  Vision APIs (fallback chain):   │
        ┌── Tunnel (optional) ──┐    │  Gemini → OpenAI → Claude →      │
        │  cloudflared / ngrok  │    │  YOLOv8 local (GPU)              │
        │  for cross-network    │    │                                   │
        └───────────────────────┘    │  ElevenLabs TTS (emotion voice)  │
                                     │  Google Maps (walking nav)        │
                                     └───────────────────────────────────┘
```

**Data storage:**
- **SQLite** (`aria.db`) — users, auth, transcripts, navigation logs, SOS events, API usage, user profiles, user preferences
- **In-memory** — per-user sign session state (letter buffers, current emotion) — ephemeral, cleared on restart

**Vision fallback chain:**
1. Gemini 3 Flash (fastest, free tier)
2. OpenAI GPT-4o-mini (reliable fallback)
3. Claude Sonnet (third option)
4. YOLOv8n local on Jetson GPU (obstacle detection only, no sentence building)

---

## 17. Troubleshooting

| Problem | Diagnosis | Fix |
|---|---|---|
| Backend won't start | Check terminal output for errors | Missing env var or dependency — check `.env` and `pip install -r requirements.txt` |
| "Backend offline" on phone | `curl http://<ip>:8000/health` | Check Jetson IP, ensure same network or use tunnel (Section 6) |
| Can't connect from different WiFi | Devices on different networks | Use cloudflared or ngrok tunnel (Section 6) |
| Registration returns 500 | Check terminal logs | Usually a DB issue — delete `aria.db` and restart |
| No audio plays | Check ElevenLabs key is set | Verify key in `.env`, check ElevenLabs quota |
| Vision returns errors | Check terminal logs for `vision_call` | Check the relevant API key; system auto-falls back to next provider |
| Camera not working on phone | Expo Go needs camera permission | Go to phone Settings → Expo Go → Camera → Allow |
| Location not working | Expo Go needs location permission | Go to phone Settings → Expo Go → Location → While Using |
| Navigation returns empty steps | Check Google Maps API key | Ensure Directions API is enabled in Google Cloud Console |
| WebSocket won't connect | Check backend is running | Ensure uvicorn is running on 0.0.0.0:8000 |
| Slow obstacle detection | Check which provider is responding | Look at terminal logs for `vision_call` entries with latency |
| SQLite locked errors | Multiple processes accessing DB | Only run one uvicorn instance at a time |

### View logs:

Backend logs appear directly in the terminal where you ran `bash run.sh`. For background mode:

```bash
# Run in background with logs to file
bash run.sh > aria.log 2>&1 &

# View logs
tail -f aria.log

# Stop the server
kill %1
```

### Full reset:

```bash
cd ~/ARIA/backend
rm -f aria.db        # Deletes all data — tables recreated on next start
bash run.sh
```

---

*Built for Kent Hack Enough 2026 at Kent State University.*
*ARIA: Because everyone deserves a voice.*
