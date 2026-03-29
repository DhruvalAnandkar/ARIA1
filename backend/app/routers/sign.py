import uuid

import mediapipe as mp
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import async_session_factory
from app.dependencies import get_current_user, get_db
from app.models.postgres.transcript import SignSession, TranscriptEntry
from app.models.postgres.user import User
from app.schemas.sign import SOSRequest, SpeakRequest, SpeakResponse
from app.services.asl_classifier import classify_asl
from app.services.auth_service import decode_access_token
from app.services.emotion_detector import detect_emotion_from_frame
from app.services.session_manager import (
    append_letter,
    clear_buffer,
    delete_session,
    get_and_clear_buffer,
    get_session,
    set_emotion,
    set_language,
    should_build_sentence,
)
from app.services.sos_service import contains_sos_trigger, trigger_sos
from app.services.tts_service import speak
from app.services.vision.manager import vision_manager
from app.utils.image import decode_base64_image
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# MediaPipe Hands — initialized once, reused for all WebSocket connections
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(
    static_image_mode=True,  # True because we process individual frames
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)


def _extract_landmarks(frame_b64: str) -> list[list[float]] | None:
    """Extract hand landmarks from a base64 JPEG frame using MediaPipe."""
    try:
        import cv2

        image = decode_base64_image(frame_b64)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = _hands.process(rgb)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0]
            return [[l.x, l.y, l.z] for l in lm.landmark]
        return None
    except Exception:
        logger.exception("landmark_extraction_error")
        return None


@router.websocket("/ws/sign")
async def sign_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time SIGN mode.

    Client sends frames from phone camera.
    Server processes MediaPipe → ASL classification → emotion → sentence → TTS.
    """
    # Auth via query param
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    logger.info("sign_ws_connected", user_id=user_id)

    # Create a sign session in DB
    db_session_id = None
    try:
        async with async_session_factory() as db:
            sign_session = SignSession(user_id=uuid.UUID(user_id))
            db.add(sign_session)
            await db.flush()
            db_session_id = sign_session.id
            await db.commit()
    except Exception:
        logger.exception("sign_session_create_error")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "frame":
                frame_b64 = data.get("frame", "")
                if not frame_b64:
                    continue

                session = await get_session(user_id)

                # Extract hand landmarks from frame
                landmarks = _extract_landmarks(frame_b64)

                if landmarks:
                    # Classify ASL letter
                    letter = classify_asl(landmarks)
                    if letter:
                        session = await append_letter(user_id, letter)
                        buffer_str = "".join(session["letter_buffer"])
                        await websocket.send_json({
                            "type": "letter",
                            "letter": letter,
                            "buffer": buffer_str,
                        })

                # Emotion detection (every 5th frame to save CPU)
                if session["frame_count"] % 5 == 0 and frame_b64:
                    emotion, confidence = detect_emotion_from_frame(frame_b64)
                    await set_emotion(user_id, emotion, confidence)
                    await websocket.send_json({
                        "type": "emotion",
                        "emotion": emotion,
                        "confidence": confidence,
                    })

                # Check if we should build a sentence
                if await should_build_sentence(user_id):
                    raw_text, emotion = await get_and_clear_buffer(user_id)

                    if raw_text:
                        # Check for SOS
                        if contains_sos_trigger(raw_text):
                            async with async_session_factory() as db:
                                sentence, audio_file = await trigger_sos(user_id, db)
                                await db.commit()
                            await websocket.send_json({
                                "type": "sos_triggered",
                                "text": sentence,
                                "audio_url": f"/audio/{audio_file}",
                            })
                            continue

                        # Build sentence via vision manager
                        try:
                            result = await vision_manager.build_sentence(raw_text, emotion)
                            sentence = result.text
                        except Exception:
                            sentence = raw_text  # Fallback: use raw letters

                        # Translate if needed
                        lang = session.get("language", "en")
                        if lang != "en":
                            try:
                                tr = await vision_manager.translate(sentence, lang)
                                sentence = tr.text
                            except Exception:
                                pass

                        # Generate TTS
                        audio_file = await speak(sentence, emotion=emotion)

                        # Log transcript
                        if db_session_id:
                            try:
                                async with async_session_factory() as db:
                                    entry = TranscriptEntry(
                                        session_id=db_session_id,
                                        text=sentence,
                                        raw_letters=raw_text,
                                        emotion=emotion,
                                        language=lang,
                                    )
                                    db.add(entry)
                                    await db.commit()
                            except Exception:
                                logger.exception("transcript_save_error")

                        await websocket.send_json({
                            "type": "sentence",
                            "text": sentence,
                            "emotion": emotion,
                            "audio_url": f"/audio/{audio_file}",
                        })

            elif msg_type == "clear_buffer":
                await clear_buffer(user_id)
                await websocket.send_json({"type": "letter", "letter": "", "buffer": ""})

            elif msg_type == "set_language":
                lang = data.get("language", "en")
                await set_language(user_id, lang)

    except WebSocketDisconnect:
        logger.info("sign_ws_disconnected", user_id=user_id)
    except Exception:
        logger.exception("sign_ws_error", user_id=user_id)
    finally:
        await delete_session(user_id)
        # End the DB session
        if db_session_id:
            try:
                async with async_session_factory() as db:
                    from sqlalchemy import update
                    from datetime import datetime, timezone

                    await db.execute(
                        update(SignSession)
                        .where(SignSession.id == db_session_id)
                        .values(ended_at=datetime.now(timezone.utc))
                    )
                    await db.commit()
            except Exception:
                pass


@router.post("/speak", response_model=SpeakResponse)
async def manual_speak(
    req: SpeakRequest,
    user: User = Depends(get_current_user),
):
    """Manually speak any text — for testing or manual input."""
    text = req.text

    if req.language != "en":
        try:
            result = await vision_manager.translate(text, req.language)
            text = result.text
        except Exception:
            pass

    audio_file = await speak(text, emotion=req.emotion)
    return SpeakResponse(sentence=text, audio_url=f"/audio/{audio_file}")


@router.post("/sos", response_model=SpeakResponse)
async def manual_sos(
    req: SOSRequest = SOSRequest(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger SOS from the app's emergency button."""
    sentence, audio_file = await trigger_sos(
        str(user.id), db, latitude=req.latitude, longitude=req.longitude
    )
    return SpeakResponse(sentence=sentence, audio_url=f"/audio/{audio_file}")


@router.get("/transcript")
async def get_transcript(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transcript entries for a sign session."""
    from sqlalchemy import select

    result = await db.execute(
        select(TranscriptEntry)
        .where(TranscriptEntry.session_id == uuid.UUID(session_id))
        .order_by(TranscriptEntry.created_at)
    )
    entries = result.scalars().all()

    return {
        "entries": [
            {
                "id": str(e.id),
                "text": e.text,
                "raw_letters": e.raw_letters,
                "emotion": e.emotion,
                "language": e.language,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]
    }
