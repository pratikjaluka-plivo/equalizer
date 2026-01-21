"""
Negotiation Arena - Real-time AI-powered negotiation assistant.

During a video call, this system:
1. Transcribes what the other person says (via OpenAI Whisper on backend)
2. Analyzes their claims in real-time
3. Generates counter-arguments and fact-checks
4. Sends transparent overlay cards to your screen

Works for ANY topic - not just medical bills.
"""
import os
import json
import asyncio
import httpx
import base64
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


async def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using OpenAI Whisper API"""
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return ""

    try:
        # Save audio to a temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        # Call OpenAI Whisper API
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(temp_path, "rb") as audio_file:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    files={"file": ("audio.webm", audio_file, "audio/webm")},
                    data={"model": "whisper-1", "language": "en"}
                )

            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text", "").strip()
                logger.info(f"Transcribed: {transcript[:100]}...")
                return transcript
            else:
                logger.error(f"Whisper API error: {response.status_code} - {response.text}")
                return ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


@dataclass
class CounterCard:
    """A counter-argument card to display on screen"""
    card_id: str
    timestamp: str
    their_statement: str
    verdict: str  # "FALSE", "MISLEADING", "PARTIALLY_TRUE", "TRUE", "NEEDS_CONTEXT"
    verdict_emoji: str
    explanation: str
    counter_argument: str
    evidence: List[str]
    confidence: int  # 0-100
    suggested_questions: List[str]


@dataclass
class NegotiationSession:
    """Tracks a negotiation session"""
    room_id: str
    topic: str
    your_position: str
    their_position: str
    transcript: List[Dict[str, Any]]
    counter_cards: List[CounterCard]
    created_at: str
    negotiation_score: int  # 0-100, your advantage


# In-memory session storage
sessions: Dict[str, NegotiationSession] = {}


def create_session(room_id: str, topic: str, your_position: str) -> NegotiationSession:
    """Create a new negotiation session"""
    session = NegotiationSession(
        room_id=room_id,
        topic=topic,
        your_position=your_position,
        their_position="Unknown",
        transcript=[],
        counter_cards=[],
        created_at=datetime.now().isoformat(),
        negotiation_score=50
    )
    sessions[room_id] = session
    return session


def get_session(room_id: str) -> Optional[NegotiationSession]:
    """Get an existing session"""
    return sessions.get(room_id)


async def analyze_statement_with_openai(
    statement: str,
    topic: str,
    your_position: str,
    context: List[Dict[str, Any]]
) -> Optional[CounterCard]:
    """
    Analyze a statement and generate counter-arguments using OpenAI.
    """
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured")
        return None

    # Build context from recent transcript
    recent_context = ""
    if context:
        recent_context = "\n".join([
            f"- {item['speaker']}: {item['text']}"
            for item in context[-10:]  # Last 10 exchanges
        ])

    prompt = f"""You are a real-time negotiation assistant. Analyze what the other person just said and help counter it.

NEGOTIATION TOPIC: {topic}

YOUR CLIENT'S POSITION: {your_position}

RECENT CONVERSATION:
{recent_context}

THEIR LATEST STATEMENT: "{statement}"

Analyze this statement and provide:
1. VERDICT: Is their statement TRUE, FALSE, MISLEADING, PARTIALLY_TRUE, or NEEDS_CONTEXT?
2. EXPLANATION: Brief explanation of why (1-2 sentences)
3. COUNTER_ARGUMENT: What your client should say in response (be specific, persuasive, and assertive)
4. EVIDENCE: 2-3 facts, statistics, or logical points that support the counter (these will be displayed as evidence cards)
5. SUGGESTED_QUESTIONS: 2 pointed questions to ask that put them on the defensive
6. CONFIDENCE: How confident are you in this analysis (0-100)?

Respond in this exact JSON format:
{{
    "verdict": "FALSE|MISLEADING|PARTIALLY_TRUE|TRUE|NEEDS_CONTEXT",
    "explanation": "...",
    "counter_argument": "...",
    "evidence": ["fact 1", "fact 2", "fact 3"],
    "suggested_questions": ["question 1?", "question 2?"],
    "confidence": 85
}}

Be aggressive but factual. Help your client WIN this negotiation.
Only respond with JSON, nothing else."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",  # Fast and cheap
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=10.0  # Fast timeout for real-time
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["choices"][0]["message"]["content"].strip()

                # Parse JSON
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]

                result = json.loads(result_text.strip())

                # Map verdict to emoji
                verdict_emojis = {
                    "FALSE": "❌",
                    "MISLEADING": "⚠️",
                    "PARTIALLY_TRUE": "🟡",
                    "TRUE": "✅",
                    "NEEDS_CONTEXT": "❓"
                }

                return CounterCard(
                    card_id=f"card_{datetime.now().strftime('%H%M%S%f')}",
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    their_statement=statement,
                    verdict=result.get("verdict", "NEEDS_CONTEXT"),
                    verdict_emoji=verdict_emojis.get(result.get("verdict", "NEEDS_CONTEXT"), "❓"),
                    explanation=result.get("explanation", ""),
                    counter_argument=result.get("counter_argument", ""),
                    evidence=result.get("evidence", []),
                    confidence=result.get("confidence", 50),
                    suggested_questions=result.get("suggested_questions", [])
                )
            else:
                logger.error(f"OpenAI error: {response.status_code} - {response.text}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")

    return None


async def analyze_statement_with_gemini(
    statement: str,
    topic: str,
    your_position: str,
    context: List[Dict[str, Any]]
) -> Optional[CounterCard]:
    """
    Fallback: Analyze using Gemini if OpenAI fails.
    """
    if not GEMINI_API_KEY:
        return None

    recent_context = ""
    if context:
        recent_context = "\n".join([
            f"- {item['speaker']}: {item['text']}"
            for item in context[-10:]
        ])

    prompt = f"""You are a real-time negotiation assistant. Analyze what the other person just said and help counter it.

NEGOTIATION TOPIC: {topic}

YOUR CLIENT'S POSITION: {your_position}

RECENT CONVERSATION:
{recent_context}

THEIR LATEST STATEMENT: "{statement}"

Respond in this exact JSON format only:
{{
    "verdict": "FALSE|MISLEADING|PARTIALLY_TRUE|TRUE|NEEDS_CONTEXT",
    "explanation": "brief explanation",
    "counter_argument": "what to say back",
    "evidence": ["fact 1", "fact 2"],
    "suggested_questions": ["question 1?", "question 2?"],
    "confidence": 85
}}"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7}
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]

                # Parse JSON
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]

                result = json.loads(result_text.strip())

                verdict_emojis = {
                    "FALSE": "❌",
                    "MISLEADING": "⚠️",
                    "PARTIALLY_TRUE": "🟡",
                    "TRUE": "✅",
                    "NEEDS_CONTEXT": "❓"
                }

                return CounterCard(
                    card_id=f"card_{datetime.now().strftime('%H%M%S%f')}",
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    their_statement=statement,
                    verdict=result.get("verdict", "NEEDS_CONTEXT"),
                    verdict_emoji=verdict_emojis.get(result.get("verdict", "NEEDS_CONTEXT"), "❓"),
                    explanation=result.get("explanation", ""),
                    counter_argument=result.get("counter_argument", ""),
                    evidence=result.get("evidence", []),
                    confidence=result.get("confidence", 50),
                    suggested_questions=result.get("suggested_questions", [])
                )

    except Exception as e:
        logger.error(f"Gemini API error: {e}")

    return None


async def analyze_statement(
    room_id: str,
    statement: str,
    speaker: str = "them"
) -> Optional[Dict[str, Any]]:
    """
    Main function to analyze a statement and generate counter-arguments.
    Tries OpenAI first, falls back to Gemini.
    """
    session = get_session(room_id)
    if not session:
        logger.error(f"Session not found: {room_id}")
        return None

    # Add to transcript
    session.transcript.append({
        "speaker": speaker,
        "text": statement,
        "timestamp": datetime.now().isoformat()
    })

    # Only analyze opponent's statements
    if speaker == "you":
        return None

    # Skip very short statements
    if len(statement.strip()) < 10:
        return None

    # Try OpenAI first
    card = await analyze_statement_with_openai(
        statement=statement,
        topic=session.topic,
        your_position=session.your_position,
        context=session.transcript
    )

    # Fallback to Gemini
    if not card:
        card = await analyze_statement_with_gemini(
            statement=statement,
            topic=session.topic,
            your_position=session.your_position,
            context=session.transcript
        )

    if card:
        session.counter_cards.append(card)

        # Update negotiation score based on verdicts
        if card.verdict == "FALSE":
            session.negotiation_score = min(100, session.negotiation_score + 5)
        elif card.verdict == "MISLEADING":
            session.negotiation_score = min(100, session.negotiation_score + 3)
        elif card.verdict == "TRUE":
            session.negotiation_score = max(0, session.negotiation_score - 2)

        return {
            "card": asdict(card),
            "negotiation_score": session.negotiation_score
        }

    return None


def get_transcript(room_id: str) -> List[Dict[str, Any]]:
    """Get full transcript for a session"""
    session = get_session(room_id)
    if session:
        return session.transcript
    return []


def get_session_summary(room_id: str) -> Optional[Dict[str, Any]]:
    """Get summary of a negotiation session"""
    session = get_session(room_id)
    if not session:
        return None

    return {
        "room_id": session.room_id,
        "topic": session.topic,
        "your_position": session.your_position,
        "total_exchanges": len(session.transcript),
        "counter_cards_generated": len(session.counter_cards),
        "negotiation_score": session.negotiation_score,
        "duration": session.created_at,
        "verdicts": {
            "false": sum(1 for c in session.counter_cards if c.verdict == "FALSE"),
            "misleading": sum(1 for c in session.counter_cards if c.verdict == "MISLEADING"),
            "true": sum(1 for c in session.counter_cards if c.verdict == "TRUE"),
        }
    }
