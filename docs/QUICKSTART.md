# ARIA Quickstart Guide

## Prerequisites

- **Jetson Orin Nano Super** with Ubuntu 22.04, CUDA 12.6, Docker 29.3+, Compose v5+
- **Expo Go** app on your phone (iOS/Android)
- API keys: Gemini, OpenAI, Anthropic, ElevenLabs, Google Maps (at least one vision API required)

## 1. Clone and Configure

```bash
ssh jetson   # IP: 192.168.55.1
cd ~/ARIA

# Set up environment variables
cp docker/.env.example docker/.env
nano docker/.env   # Fill in your API keys and passwords
```

### Required Environment Variables

| Variable | Description |
|---|---|
| `POSTGRES_PASSWORD` | PostgreSQL password (set anything) |
| `MONGO_PASSWORD` | MongoDB password (set anything) |
| `JWT_SECRET` | Random string for token signing |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS API key |
| `GOOGLE_MAPS_API_KEY` | Google Maps Directions API key |
| `VISION_PROVIDER_ORDER` | Fallback order, e.g. `gemini,openai,claude,local` |

You need **at least one** vision API key (Gemini, OpenAI, or Anthropic). The local YOLOv8 fallback handles obstacle detection only.

## 2. Start Backend Services

```bash
cd docker

# First run — builds images and initializes databases
docker compose up --build -d

# Check all services are healthy
docker compose ps
```

All 5 services should show as healthy:
- **nginx** (:80) — reverse proxy
- **api** (:8000) — FastAPI backend
- **postgres** (:5432) — relational data
- **mongo** (:27017) — user profiles/preferences
- **redis** (:6379) — session state

Verify the API is running:

```bash
curl http://localhost/health
# {"status":"ok","version":"1.0.0","uptime_seconds":...}

curl http://localhost/health/services
# Shows status of postgres, mongo, redis, vision providers
```

## 3. Run Database Migrations

```bash
docker compose exec api alembic upgrade head
```

## 4. Start Mobile App

On your development machine (not the Jetson):

```bash
cd mobile
npm install
```

Create `mobile/.env`:
```
EXPO_PUBLIC_BACKEND_URL=http://192.168.55.1
EXPO_PUBLIC_WS_URL=ws://192.168.55.1
```

Replace `192.168.55.1` with your Jetson's IP if different.

```bash
npx expo start
```

Scan the QR code with Expo Go on your phone. Make sure your phone and Jetson are on the same network.

## 5. Using ARIA

### Register / Login
Open the app and create an account. This stores your data locally on the Jetson.

### SIGN Mode (for deaf/mute users)
1. Tap **SIGN** on the home screen
2. Grant camera permission
3. Hold your hand in front of the phone camera
4. The app captures frames at 10 FPS, sends to Jetson for ASL recognition
5. Letters accumulate in a buffer and auto-form sentences
6. Detected emotion modulates the TTS voice
7. Use the **SOS** button for emergencies

### GUIDE Mode (for blind users)
1. Tap **GUIDE** on the home screen
2. Grant camera and location permissions
3. **Obstacle scanning** starts automatically — point the phone camera forward
4. Enter a destination and tap **Go** for turn-by-turn walking directions
5. Audio warnings play for obstacles; navigation steps are spoken aloud

## 6. Development

### Hot Reload (Backend)
```bash
cd docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
This mounts the backend source and enables uvicorn auto-reload.

### Logs
```bash
# All services
docker compose logs -f

# Just the API
docker compose logs -f api
```

### Database Access (Dev)
With dev compose overrides, ports are exposed:
- PostgreSQL: `localhost:5433`
- MongoDB: `localhost:27018`
- Redis: `localhost:6380`

## 7. Troubleshooting

| Issue | Fix |
|---|---|
| `curl: (7) Failed to connect` | Check `docker compose ps` — restart unhealthy services |
| Vision API errors | Verify API keys in `docker/.env`, check `docker compose logs api` |
| Mobile can't connect | Ensure phone and Jetson on same network, check IP in `mobile/.env` |
| GPU not detected | Verify NVIDIA runtime: `docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi` |
| Camera permission denied | Reinstall Expo Go or reset app permissions |
| Audio not playing | Check ElevenLabs API key is set and has quota remaining |

## Architecture

```
Phone (Expo) ──REST/WS──> Jetson Nginx (:80) ──> FastAPI (:8000)
                                                    ├── PostgreSQL (transcripts, nav, auth)
                                                    ├── MongoDB (profiles, preferences)
                                                    ├── Redis (session buffers)
                                                    └── Vision APIs (Gemini/OpenAI/Claude/YOLOv8)
```
