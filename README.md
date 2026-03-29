# ARIA — Adaptive Real-time Intelligence Assistant

A universal accessibility app with two modes:

- **SIGN Mode** — For deaf/mute users: ASL hand sign recognition + facial emotion detection → natural sentence → emotion-matched voice output via ElevenLabs
- **GUIDE Mode** — For blind users: camera-based obstacle detection + turn-by-turn walking navigation with voice guidance

React Native (Expo) mobile app connected to a FastAPI backend running on a Jetson Orin Nano Super. All AI processing runs on the Jetson. Databases (PostgreSQL + MongoDB + Redis) are self-hosted — no third-party data storage.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Get Your API Keys](#2-get-your-api-keys)
3. [Backend Setup (Jetson)](#3-backend-setup-jetson)
4. [Run Database Migrations](#4-run-database-migrations)
5. [Verify Backend Services](#5-verify-backend-services)
6. [Mobile App Setup](#6-mobile-app-setup)
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
- Docker 29.3+ and Docker Compose v5+
- At least 4GB free RAM, 10GB free disk
- Network accessible from your phone (same WiFi or USB network)

**On your development machine (laptop/desktop):**
- Node.js 18+ and npm
- **Expo Go** app installed on your phone (iOS App Store / Google Play Store)
- Phone and Jetson on the same network

**Verify Docker on Jetson:**
```bash
ssh jetson
docker --version        # Should be 29.3+
docker compose version  # Should be v5+
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
cd ARIA
```

### 3.2 — Create the environment file

```bash
cd docker
cp .env.example .env
nano .env
```

Fill in your actual values:

```env
# Database passwords (pick anything, these are local-only)
POSTGRES_PASSWORD=ariapass
MONGO_PASSWORD=ariapass

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

### 3.3 — Build and start all services

```bash
cd ~/ARIA/docker
docker compose up --build -d
```

This starts 5 services:
- **nginx** on port 80 (reverse proxy)
- **api** on port 8000 (FastAPI backend)
- **postgres** on port 5432
- **mongo** on port 27017
- **redis** on port 6379

First build takes 5-10 minutes (downloads base images, installs Python packages, etc.).

### 3.4 — Watch the logs until everything is healthy

```bash
docker compose logs -f
```

Wait until you see:
```
api-1  | INFO  aria_backend_ready
```

Then press `Ctrl+C` to stop following logs.

### 3.5 — Verify all containers are running

```bash
docker compose ps
```

All 5 services should show `Up` or `healthy`. If any show `Restarting` or `Exit`, check the troubleshooting section.

---

## 4. Run Database Migrations

This creates the PostgreSQL tables (users, transcripts, navigation logs, etc.):

```bash
docker compose exec api alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, Initial tables
```

If you see `No module named 'app'`, make sure you're running the command from the `docker/` directory and the api container is running.

---

## 5. Verify Backend Services

### 5.1 — Basic health check

```bash
# From the Jetson itself:
curl http://localhost/health
```

Expected response:
```json
{"status": "ok", "version": "1.0.0", "uptime_seconds": 42.5}
```

### 5.2 — Detailed service health

```bash
curl http://localhost/health/services
```

Expected response (all should be `true`):
```json
{
  "postgres": true,
  "mongo": true,
  "redis": true,
  "vision_providers": {
    "gemini": true,
    "openai": true,
    "claude": true,
    "local": false
  },
  "gpu_available": true
}
```

`local: false` is normal if YOLOv8 weights haven't been downloaded yet. The cloud providers are what matter.

### 5.3 — Check from your laptop

Find the Jetson's IP:
```bash
# On the Jetson:
hostname -I
# Example output: 192.168.55.1 ...
```

From your laptop:
```bash
curl http://192.168.55.1/health
```

If this works, your phone can reach the backend too.

---

## 6. Mobile App Setup

### 6.1 — Install dependencies

On your **development machine** (not the Jetson):

```bash
cd ARIA/mobile
npm install
```

### 6.2 — Configure backend URL

Edit `mobile/src/constants/config.ts`:

```typescript
export const BACKEND_URL = "http://192.168.55.1";  // <-- Your Jetson's IP
export const WS_URL = "ws://192.168.55.1";          // <-- Same IP, ws:// protocol
```

If you're using USB networking (default Jetson setup), the IP is `192.168.55.1`.
If you're on WiFi, use whatever `hostname -I` showed.

### 6.3 — Start the Expo dev server

```bash
npx expo start
```

You'll see a QR code in the terminal.

### 6.4 — Open on your phone

1. Open **Expo Go** on your phone
2. Scan the QR code
3. The app should load and show the ARIA login screen

If the QR code doesn't scan, try pressing `s` in the terminal to switch to Expo Go mode, then scan again.

---

## 7. Test: Registration & Login

### Step 1 — Register a new account

1. On the login screen, tap **"Create account"** (or the register link)
2. Enter:
   - **Name:** Your name
   - **Email:** test@example.com
   - **Password:** testpass123
3. Tap **Register**
4. You should be taken to the Home screen

### Step 2 — Verify the home screen

You should see:
- The **ARIA** logo
- A green **"Backend connected"** indicator
- Two mode cards: **SIGN** and **GUIDE**

If you see a red "Backend offline" indicator, double-check:
- The Jetson IP in `config.ts` is correct
- Your phone is on the same network as the Jetson
- The backend is running (`docker compose ps` on Jetson)

### Step 3 — Test logout and login

1. Go to the **Profile** tab (bottom navigation)
2. Tap **Logout**
3. You should be back at the login screen
4. Log in with the credentials you just registered
5. You should be back on the Home screen

### Verify via API directly (optional)

```bash
# Register
curl -X POST http://192.168.55.1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"curl@test.com","password":"test123","name":"Curl User"}'

# Login
curl -X POST http://192.168.55.1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"curl@test.com","password":"test123"}'

# Response includes a token:
# {"user_id":"...","token":"eyJhbGci..."}
```

Save the token for testing protected endpoints:
```bash
export TOKEN="eyJhbGci..."  # paste the token from the login response
```

---

## 8. Test: SIGN Mode

### From the mobile app:

1. Tap the **SIGN** card on the Home screen (or the Sign tab)
2. Grant **camera permission** when prompted
3. The camera preview should appear
4. Hold your hand in front of the phone camera and make ASL letter shapes:
   - **L shape** (index finger up + thumb out) → should detect "L"
   - **Fist with thumb out** → should detect "A"
   - **All fingers up, thumb across palm** → should detect "B"
5. Watch the **letter buffer** build up at the top
6. After 6 letters (or a space gesture), the system:
   - Sends letters to the LLM to form a natural sentence
   - Detects your facial emotion from the camera
   - Generates speech with emotion-matched voice
   - Plays the audio through your phone speaker
7. The sentence appears in the **transcript feed** with an emotion badge

### What to expect:

- Letters appear in the buffer as you sign
- Emotion badge updates (NEUTRAL, HAPPY, SAD, FEAR, etc.)
- After sentence formation: audio plays automatically
- Transcript feed scrolls down with each new sentence

### Language selector:

- Tap **EN**, **ES**, or **FR** to change language
- The next sentence will be translated before being spoken

### Test via API (optional):

```bash
# Manual speak — tests TTS without camera
curl -X POST http://192.168.55.1/sign/speak \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text":"Hello, I need help","emotion":"fear"}'

# Response: {"sentence":"Hello, I need help","audio_url":"/audio/xxx.mp3"}

# Play the audio:
curl -O http://192.168.55.1/audio/xxx.mp3  # replace xxx with actual filename
# Open the MP3 file to hear it
```

---

## 9. Test: GUIDE Mode — Obstacle Detection

### From the mobile app:

1. Tap the **GUIDE** card on the Home screen (or the Guide tab)
2. Grant **camera** and **location** permissions when prompted
3. The rear camera preview should appear
4. Tap **Start Scanning**
5. Point your phone camera at objects around you:
   - A chair → "Chair ahead, move left"
   - A wall → "Wall directly ahead"
   - Open hallway → "Path is clear"
6. Audio warnings play automatically through the speaker
7. The warning banner at the top shows the latest detection
8. Severity levels trigger different haptic feedback:
   - **clear** — no haptic
   - **caution** — light vibration
   - **danger** — heavy vibration
9. Tap **Stop Scanning** to pause

### What to expect:

- A new scan happens every 1.5 seconds
- Each scan takes 1-3 seconds (depends on which vision API responds)
- The red scanning indicator shows when active
- Audio plays for each scan result

### Test via API (optional):

You can test with a base64-encoded image:

```bash
# Encode a test image
BASE64_IMG=$(base64 -w0 /path/to/test-image.jpg)

curl -X POST http://192.168.55.1/guide/obstacle \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"frame\":\"$BASE64_IMG\"}"

# Response: {"warning":"Chair on your left","severity":"caution","audio_url":"/audio/yyy.mp3"}
```

---

## 10. Test: GUIDE Mode — Navigation

### From the mobile app:

1. While in GUIDE mode, type a destination in the text input at the bottom
   - Example: "Kent State University Library"
   - Example: "Starbucks"
   - Example: "123 Main Street, Kent, OH"
2. Tap **Go**
3. The app will:
   - Get your current GPS location
   - Request walking directions from Google Maps
   - Display the first step in a green card
   - Speak the first instruction aloud
4. As you walk, location updates are sent via WebSocket
5. When you get close to a waypoint, the next step is automatically spoken
6. When you arrive, you'll hear "You have arrived at your destination"

### What to expect:

- Step card shows: "Step 1 of 5 — Head north on Main St for 200m"
- Audio plays for each new step
- Navigation and obstacle scanning work simultaneously

### Test via API (optional):

```bash
# Get walking directions (use real coordinates near you)
curl -X POST http://192.168.55.1/guide/navigate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"lat":41.1499,"lng":-81.3415,"destination":"Kent State Library"}'

# Response:
# {
#   "route_id": "nav_abc123",
#   "steps": [
#     {"instruction":"Head north on S Lincoln St","distance":"0.2 mi","duration":"4 mins",...},
#     ...
#   ],
#   "total_distance": "0.8 mi",
#   "total_duration": "16 mins"
# }
```

---

## 11. Test: SOS Emergency

### From the mobile app (SIGN mode):

1. In SIGN mode, tap the red **SOS** button at the bottom right
2. The phone will:
   - Vibrate in an urgent pattern (3 long pulses)
   - Play a loud emergency message: "EMERGENCY — I NEED IMMEDIATE HELP..."
   - Log the SOS event with your GPS coordinates in the database
3. The transcript feed shows the SOS entry highlighted in red

### Test via API (optional):

```bash
curl -X POST http://192.168.55.1/sign/sos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"location":{"lat":41.1499,"lng":-81.3415}}'

# Response: {"sentence":"EMERGENCY...","audio_url":"/audio/zzz.mp3"}
```

---

## 12. Test: Profile & Preferences

### From the mobile app:

1. Go to the **Profile** tab
2. You should see your name and email
3. Tap to edit your name
4. Changes save automatically

### Test via API:

```bash
# Get profile
curl http://192.168.55.1/user/profile \
  -H "Authorization: Bearer $TOKEN"

# Update profile
curl -X PATCH http://192.168.55.1/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"New Name"}'

# Get preferences
curl http://192.168.55.1/user/preferences \
  -H "Authorization: Bearer $TOKEN"

# Update preferences
curl -X PATCH http://192.168.55.1/user/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"default_mode":"guide","obstacle_scan_interval_ms":2000}'
```

---

## 13. Run Backend Unit Tests

### On the Jetson (inside the API container):

```bash
cd ~/ARIA/docker

# Run all tests
docker compose exec api python -m pytest tests/ -v

# Run specific test files
docker compose exec api python -m pytest tests/test_asl_classifier.py -v
docker compose exec api python -m pytest tests/test_vision_fallback.py -v
docker compose exec api python -m pytest tests/test_auth.py -v
docker compose exec api python -m pytest tests/test_sign.py -v
docker compose exec api python -m pytest tests/test_guide.py -v
```

### Test descriptions:

| File | Tests | What it covers |
|---|---|---|
| `test_asl_classifier.py` | 11 tests | ASL letter recognition (A, D, E, F, I, K, L, W, Y), edge cases |
| `test_vision_fallback.py` | 7 tests | Vision provider interface, mock providers, health checks |
| `test_auth.py` | 7 tests | Registration validation, login failures, auth protection |
| `test_sign.py` | 4 tests | SIGN endpoint auth requirements, payload validation |
| `test_guide.py` | 5 tests | GUIDE endpoint auth requirements, payload validation |

---

## 14. Development Mode (Hot Reload)

For active development with live code reloading:

```bash
cd ~/ARIA/docker

# Start with dev overrides
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This gives you:
- **Backend hot reload** — edit Python files, uvicorn auto-restarts
- **Exposed database ports** — connect with any DB client:
  - PostgreSQL: `localhost:5432` (user: `aria`, db: `aria`)
  - MongoDB: `localhost:27017` (user: `aria`)
  - Redis: `localhost:6379`
- **Debug logging** enabled
- **No GPU requirement** — works on machines without NVIDIA GPU

For the mobile app, `npx expo start` already hot-reloads on file save.

---

## 15. API Reference (Quick)

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

## 16. Architecture

```
Phone (Expo)                          Jetson Orin Nano (Docker Compose)
┌──────────────┐                     ┌─────────────────────────────────────┐
│  SIGN Screen │──WebSocket──────────│─► Nginx (:80) ──► FastAPI (:8000)  │
│  (phone cam) │   frames @ 10fps   │      │               │              │
│              │                     │      │    ┌──────────┼──────────┐   │
│  GUIDE Screen│──REST + WS─────────│──────┘    │          │          │   │
│  (phone cam) │   obstacle frames  │           ▼          ▼          ▼   │
│              │   location updates  │     PostgreSQL   MongoDB    Redis   │
│  Profile     │──REST──────────────│──────►    │                         │
└──────────────┘                     │     Vision APIs (fallback chain):  │
                                     │     Gemini → OpenAI → Claude →     │
                                     │     YOLOv8 local (GPU)             │
                                     │                                     │
                                     │     ElevenLabs TTS (emotion voice) │
                                     │     Google Maps (walking nav)      │
                                     └─────────────────────────────────────┘
```

**Database split:**
- **PostgreSQL** — users, auth, transcripts, navigation logs, SOS events, API usage tracking
- **MongoDB** — user profiles, user preferences (flexible documents)
- **Redis** — per-user sign session state (letter buffers, current emotion)

**Vision fallback chain:**
1. Gemini 1.5 Flash (fastest, free tier)
2. OpenAI GPT-4o-mini (reliable fallback)
3. Claude Sonnet (third option)
4. YOLOv8n local on Jetson GPU (obstacle detection only, no sentence building)

---

## 17. Troubleshooting

| Problem | Diagnosis | Fix |
|---|---|---|
| `docker compose up` fails | Check `docker compose logs api` | Usually a missing env var — verify `.env` file |
| "Backend offline" on phone | Run `curl http://<ip>/health` from phone's network | Check Jetson IP, ensure same network, check firewall |
| Health check shows postgres `false` | `docker compose logs postgres` | Wait for postgres to initialize (30s), or check password in `.env` |
| `alembic upgrade` fails | `docker compose exec api alembic current` | Make sure postgres is healthy first |
| Registration returns 500 | `docker compose logs api` | Usually a DB connection issue — check DATABASE_URL |
| No audio plays | Check ElevenLabs key is set | Verify key in `.env`, check ElevenLabs quota at elevenlabs.io |
| Vision returns errors | `docker compose logs api \| grep vision` | Check the relevant API key; system auto-falls back to next provider |
| Camera not working on phone | Expo Go needs camera permission | Go to phone Settings → Expo Go → Camera → Allow |
| Location not working | Expo Go needs location permission | Go to phone Settings → Expo Go → Location → While Using |
| Navigation returns empty steps | Check Google Maps API key | Ensure Directions API is enabled in Google Cloud Console |
| WebSocket won't connect | Check nginx config | Ensure `/ws/` paths are proxied with upgrade headers |
| GPU not detected | `docker compose exec api nvidia-smi` | Install NVIDIA Container Toolkit on Jetson |
| Tests fail with import errors | `docker compose exec api pip list` | Run tests inside the container, not on host |
| Slow obstacle detection | Check which provider is responding | Look at api logs for `vision_call` entries with latency |

### View logs:

```bash
# All services
docker compose logs -f

# Just the API (most useful)
docker compose logs -f api

# Last 100 lines
docker compose logs --tail 100 api
```

### Restart a single service:

```bash
docker compose restart api
```

### Full reset (nuclear option):

```bash
docker compose down -v   # WARNING: deletes all database data
docker compose up --build -d
docker compose exec api alembic upgrade head
```

---

*Built for Kent Hack Enough 2026 at Kent State University.*
*ARIA: Because everyone deserves a voice.*
