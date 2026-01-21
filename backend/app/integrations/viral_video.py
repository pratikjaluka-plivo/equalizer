"""
Viral Video Generator - Creates AI-generated videos
for threatening legal action against hospitals, optimized for X/Twitter virality.

Uses:
- Google Veo 3.1 for video generation (via Gemini API)
- OpenAI GPT-4 for script generation
- Gemini for fact validation (prevents hallucination)
- Fallback: Creates viral poster image with DALL-E
"""
import os
import httpx
import json
import base64
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Google Genai SDK for Veo video generation
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")  # Optional fallback
DID_API_KEY = os.getenv("DID_API_KEY", "")  # D-ID for talking head videos

# Initialize Gemini client for Veo
genai_client = None
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)


@dataclass
class VideoRequest:
    """Request for viral video generation"""
    user_photo_base64: str  # Base64 encoded user photo
    patient_name: str
    hospital_name: str
    hospital_city: str
    procedure: str
    billed_amount: float
    fair_amount: float
    overcharge_percentage: float


@dataclass
class VideoResult:
    """Result of video generation"""
    success: bool
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    script: Optional[str] = None
    thumbnail_url: Optional[str] = None
    twitter_text: Optional[str] = None
    error: Optional[str] = None
    fallback_used: bool = False


async def generate_script_with_openai(prompt: str) -> Optional[str]:
    """Generate script using OpenAI GPT-4"""
    if not OPENAI_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"OpenAI error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
    return None


async def validate_script_with_gemini(script: str, facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the generated script using Gemini to ensure factual accuracy.
    Returns validation result with any corrections needed.
    """
    if not GEMINI_API_KEY:
        # If no Gemini, skip validation
        return {"valid": True, "script": script}

    validation_prompt = f"""You are a fact-checker. Verify this script contains EXACTLY these facts:

REQUIRED FACTS:
- Patient Name: {facts['patient_name']}
- Hospital Name: {facts['hospital_name']}
- Hospital City: {facts['hospital_city']}
- Procedure: {facts['procedure']}
- Bill Amount: ₹{facts['billed_amount']:,.0f}
- Fair/CGHS Rate: ₹{facts['fair_amount']:,.0f}
- Overcharge Amount: ₹{facts['overcharge_amount']:,.0f}
- Overcharge Percentage: {facts['overcharge_percentage']:.0f}%

SCRIPT TO VERIFY:
{script}

CHECK:
1. Are ALL the numbers in the script matching the facts above?
2. Is the hospital name spelled correctly?
3. Is the patient name correct?
4. Is the overcharge percentage accurate?

RESPOND IN THIS EXACT JSON FORMAT:
{{"valid": true/false, "errors": ["list of factual errors if any"], "corrected_script": "if invalid, provide corrected version with exact facts"}}

Only respond with the JSON, nothing else."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": validation_prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON from response
                result_text = result_text.strip()
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                validation_result = json.loads(result_text.strip())
                logger.info(f"Gemini validation result: {validation_result}")

                if validation_result.get("valid", False):
                    return {"valid": True, "script": script}
                else:
                    # Return corrected script if available
                    corrected = validation_result.get("corrected_script", script)
                    errors = validation_result.get("errors", [])
                    logger.warning(f"Script validation failed: {errors}")
                    return {"valid": False, "script": corrected, "errors": errors}
            else:
                logger.error(f"Gemini error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Gemini validation error: {e}")

    # On error, return original script as valid
    return {"valid": True, "script": script}


async def create_video_with_did(
    photo_base64: str,
    script: str,
    request: 'VideoRequest'
) -> Optional[Dict[str, Any]]:
    """
    Create a talking head video using D-ID API.
    D-ID animates a photo to create a video of the person speaking the script.

    Flow:
    1. Create a talk request with the photo and script
    2. Poll for completion
    3. Return the video URL
    """
    if not DID_API_KEY:
        logger.warning("D-ID API key not configured")
        return None

    did_base_url = "https://api.d-id.com"
    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Create talk request
            logger.info("Creating D-ID talk video...")

            # Prepare the photo - D-ID accepts base64 or URL
            # We'll use base64 with data URI
            photo_data_uri = f"data:image/jpeg;base64,{photo_base64}"

            talk_payload = {
                "source_url": photo_data_uri,
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-IN-PrabhatNeural"  # Indian English male voice
                    }
                },
                "config": {
                    "fluent": True,
                    "pad_audio": 0.5,
                    "stitch": True
                }
            }

            create_response = await client.post(
                f"{did_base_url}/talks",
                headers=headers,
                json=talk_payload
            )

            if create_response.status_code not in [200, 201]:
                error_text = create_response.text
                logger.error(f"D-ID create talk error: {create_response.status_code} - {error_text}")

                # Check for specific errors
                if "insufficient_credits" in error_text.lower() or "quota" in error_text.lower():
                    logger.error("D-ID credits exhausted. Add credits at https://studio.d-id.com/")

                return None

            talk_data = create_response.json()
            talk_id = talk_data.get("id")

            if not talk_id:
                logger.error(f"D-ID response missing talk ID: {talk_data}")
                return None

            logger.info(f"D-ID talk created with ID: {talk_id}")

            # Step 2: Poll for completion (max 2 minutes)
            max_attempts = 24  # 24 * 5 seconds = 2 minutes
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(5)
                attempt += 1

                status_response = await client.get(
                    f"{did_base_url}/talks/{talk_id}",
                    headers=headers
                )

                if status_response.status_code != 200:
                    logger.error(f"D-ID status check error: {status_response.status_code}")
                    continue

                status_data = status_response.json()
                status = status_data.get("status")

                logger.info(f"D-ID video status: {status} (attempt {attempt}/{max_attempts})")

                if status == "done":
                    result_url = status_data.get("result_url")
                    if result_url:
                        logger.info(f"D-ID video ready: {result_url}")
                        return {
                            "video_url": result_url,
                            "video_id": f"did_{talk_id}",
                            "thumbnail_url": status_data.get("thumbnail_url"),
                            "duration": status_data.get("duration", 30),
                            "source": "d-id"
                        }
                    else:
                        logger.error("D-ID video done but no result_url")
                        return None

                elif status == "error":
                    error_msg = status_data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"D-ID video generation failed: {error_msg}")
                    return None

                elif status in ["created", "started", "processing"]:
                    continue
                else:
                    logger.warning(f"Unknown D-ID status: {status}")

            logger.error("D-ID video generation timed out")
            return None

    except httpx.TimeoutException:
        logger.error("D-ID API request timed out")
        return None
    except Exception as e:
        logger.error(f"D-ID API error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


async def create_video_with_did_clips(
    photo_base64: str,
    script: str,
    request: 'VideoRequest'
) -> Optional[Dict[str, Any]]:
    """
    Alternative D-ID method using clips API for longer videos.
    Falls back to this if standard talks API fails.
    """
    if not DID_API_KEY:
        return None

    did_base_url = "https://api.d-id.com"
    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            logger.info("Creating D-ID clip video...")

            photo_data_uri = f"data:image/jpeg;base64,{photo_base64}"

            clip_payload = {
                "presenter_id": "amy-jcwCkr1grs",  # D-ID default presenter
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-IN-PrabhatNeural"
                    }
                },
                "background": {
                    "color": "#FFFFFF"
                },
                "presenter_config": {
                    "crop": {
                        "type": "rectangle"
                    }
                }
            }

            # If user provided their photo, use it as custom presenter
            if photo_base64:
                clip_payload["source_url"] = photo_data_uri

            create_response = await client.post(
                f"{did_base_url}/clips",
                headers=headers,
                json=clip_payload
            )

            if create_response.status_code not in [200, 201]:
                logger.error(f"D-ID clips error: {create_response.status_code} - {create_response.text}")
                return None

            clip_data = create_response.json()
            clip_id = clip_data.get("id")

            if not clip_id:
                return None

            logger.info(f"D-ID clip created: {clip_id}")

            # Poll for completion
            max_attempts = 36  # 3 minutes
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(5)
                attempt += 1

                status_response = await client.get(
                    f"{did_base_url}/clips/{clip_id}",
                    headers=headers
                )

                if status_response.status_code != 200:
                    continue

                status_data = status_response.json()
                status = status_data.get("status")

                logger.info(f"D-ID clip status: {status}")

                if status == "done":
                    result_url = status_data.get("result_url")
                    if result_url:
                        return {
                            "video_url": result_url,
                            "video_id": f"did_clip_{clip_id}",
                            "thumbnail_url": status_data.get("thumbnail_url"),
                            "duration": status_data.get("duration", 30),
                            "source": "d-id-clips"
                        }
                    return None

                elif status == "error":
                    logger.error(f"D-ID clip failed: {status_data.get('error')}")
                    return None

            logger.error("D-ID clip timed out")
            return None

    except Exception as e:
        logger.error(f"D-ID clips error: {e}")
        return None


async def generate_viral_script(request: VideoRequest) -> str:
    """
    Generate a viral script using dual-LLM approach:
    1. OpenAI (GPT-4) generates the script
    2. Gemini validates factual accuracy
    3. If validation fails, use corrected version
    4. Fallback to Anthropic or default script
    """
    overcharge_amount = request.billed_amount - request.fair_amount

    facts = {
        "patient_name": request.patient_name,
        "hospital_name": request.hospital_name,
        "hospital_city": request.hospital_city,
        "procedure": request.procedure,
        "billed_amount": request.billed_amount,
        "fair_amount": request.fair_amount,
        "overcharge_amount": overcharge_amount,
        "overcharge_percentage": request.overcharge_percentage
    }

    prompt = f"""You are writing a short, powerful video script for a person who has been overcharged by a hospital.
The video will be posted on X/Twitter to go viral and pressure the hospital.

CASE DETAILS (USE THESE EXACT VALUES):
- Patient Name: {request.patient_name}
- Hospital: {request.hospital_name}, {request.hospital_city}
- Procedure: {request.procedure}
- Bill Amount: ₹{request.billed_amount:,.0f}
- Government CGHS Rate: ₹{request.fair_amount:,.0f}
- Overcharge: ₹{overcharge_amount:,.0f} ({request.overcharge_percentage:.0f}% above govt rate)

WRITE A 30-45 SECOND SCRIPT (about 80-100 words) that:
1. Opens with a hook that grabs attention
2. States the overcharge clearly with EXACT numbers from above
3. Mentions filing consumer court case and RTI
4. Threatens to expose the hospital
5. Calls for others to share and retweet
6. Ends with a powerful statement

TONE: Angry but articulate, confident, determined. Like a citizen who knows their rights.

CRITICAL REQUIREMENTS:
- Use the EXACT numbers provided above - do not round or change them
- Use the EXACT hospital name and patient name
- Use simple Hindi-English mix that Indians relate to
- Keep it punchy, each line should hit hard

Return ONLY the script text, nothing else."""

    # Step 1: Generate with OpenAI (Primary)
    script = await generate_script_with_openai(prompt)

    if script:
        logger.info("Script generated with OpenAI, validating with Gemini...")
        # Step 2: Validate with Gemini
        validation = await validate_script_with_gemini(script, facts)

        if validation.get("valid"):
            logger.info("Script validated successfully")
            return validation["script"]
        else:
            logger.info("Using Gemini-corrected script")
            return validation["script"]

    # Step 3: Fallback to Anthropic
    if ANTHROPIC_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    script = data["content"][0]["text"].strip()
                    # Validate Anthropic output too
                    validation = await validate_script_with_gemini(script, facts)
                    return validation["script"]
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")

    # Step 4: Default script if all APIs fail
    logger.warning("All LLMs failed, using default script")
    return f"""Namaste, my name is {request.patient_name}.

{request.hospital_name} in {request.hospital_city} charged me ₹{request.billed_amount:,.0f} for {request.procedure}.

The government CGHS rate? Only ₹{request.fair_amount:,.0f}.

That's {request.overcharge_percentage:.0f}% overcharging - ₹{overcharge_amount:,.0f} extra!

I've filed RTI requests. I'm going to Consumer Court.
I have all the evidence. CGHS rates, NABH guidelines, everything.

{request.hospital_name}, you have 48 hours to respond.

Otherwise, this video goes to every news channel, every consumer forum, every social media platform.

India, please share this. RT karo. Help me fight back.

Medical loot band karo!"""


def generate_twitter_text(request: VideoRequest) -> str:
    """Generate the Twitter post text to accompany the video"""
    overcharge_amount = request.billed_amount - request.fair_amount

    return f"""🚨 EXPOSED: {request.hospital_name} OVERCHARGED me {request.overcharge_percentage:.0f}%!

💰 Bill: ₹{request.billed_amount:,.0f}
📋 Govt CGHS Rate: ₹{request.fair_amount:,.0f}
😡 Overcharge: ₹{overcharge_amount:,.0f}

I'm taking them to Consumer Court.

Filing RTI. Have ALL evidence.

{request.hospital_name}, your move.

India, RT & help me fight medical loot! 🙏

#MedicalScam #ConsumerRights #HospitalLoot #India"""


def create_video_with_veo_sync(
    script: str,
    request: 'VideoRequest'
) -> Optional[Dict[str, Any]]:
    """
    Create a talking video using Google Veo 3.1 via Gemini SDK.
    This is a synchronous function that uses the google-genai SDK.
    """
    global genai_client

    if not genai_client:
        logger.warning("Gemini client not initialized for Veo")
        return None

    try:
        # Create video prompt with dialogue
        video_prompt = f"""A close up video of an Indian person speaking directly to camera with passion and determination.

The person is delivering this speech with emotion, looking at the camera:
"{script}"

The person speaks clearly in Hindi-English mix, with angry but articulate tone.
Professional news interview lighting, clean background.
The person occasionally gestures with hands while speaking."""

        logger.info("Starting Veo 3.1 video generation with SDK...")
        logger.info(f"Prompt: {video_prompt[:200]}...")

        # Start video generation using SDK
        operation = genai_client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=video_prompt,
        )

        logger.info(f"Veo operation started, polling for completion...")

        # Poll until video is ready (max 3 minutes)
        max_attempts = 18  # 18 * 10 seconds = 3 minutes
        attempt = 0

        while not operation.done and attempt < max_attempts:
            logger.info(f"Waiting for video generation... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(10)
            operation = genai_client.operations.get(operation)
            attempt += 1

        if not operation.done:
            logger.error("Veo 3.1 video generation timed out")
            return None

        # Get the generated video
        if operation.response and operation.response.generated_videos:
            generated_video = operation.response.generated_videos[0]

            # Save video to temp file
            video_filename = f"viral_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
            video_path = f"/tmp/{video_filename}"

            # Download the video file
            genai_client.files.download(file=generated_video.video)
            generated_video.video.save(video_path)

            logger.info(f"Veo 3.1 video saved to: {video_path}")

            # Read video as base64 for frontend
            with open(video_path, "rb") as f:
                video_base64 = base64.b64encode(f.read()).decode()

            return {
                "video_url": f"data:video/mp4;base64,{video_base64}",
                "video_id": f"veo_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "video_path": video_path,
                "thumbnail_url": None,
                "duration": 8,
                "source": "veo_3.1"
            }
        else:
            logger.error(f"Veo completed but no video in response: {operation}")
            return None

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            logger.error("=" * 60)
            logger.error("VEO BILLING ERROR: Your Gemini API quota is exhausted!")
            logger.error("Veo video generation requires a PAID Google AI plan.")
            logger.error("Go to https://aistudio.google.com/ and add billing.")
            logger.error("Pricing: ~$0.15-$0.40 per second of video")
            logger.error("=" * 60)
        else:
            logger.error(f"Veo 3.1 SDK error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        return None


async def create_video_with_veo(
    photo_base64: str,
    script: str,
    request: 'VideoRequest'
) -> Optional[Dict[str, Any]]:
    """
    Async wrapper for Veo video generation.
    Runs the sync SDK call in a thread pool.
    """
    import concurrent.futures

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            create_video_with_veo_sync,
            script,
            request
        )
    return result


async def create_viral_poster(request: VideoRequest, script: str) -> Optional[str]:
    """
    Fallback: Create a viral poster image using DALL-E if video generation fails.
    Returns base64 encoded image.
    """
    if not OPENAI_API_KEY:
        return None

    prompt = f"""Create a dramatic protest poster with this text overlay:

"{request.hospital_name} EXPOSED"
"Charged: ₹{request.billed_amount:,.0f}"
"Govt Rate: ₹{request.fair_amount:,.0f}"
"OVERCHARGE: {request.overcharge_percentage:.0f}%"

Style: Bold red and black colors, protest aesthetic, angry Indian citizen theme,
high contrast, attention-grabbing, suitable for Twitter/X viral post.
Include medical/hospital imagery in background.
The overall mood should be accusatory and powerful."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "response_format": "b64_json"
                },
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["b64_json"]

    except Exception as e:
        logger.error(f"DALL-E error: {e}")

    return None


async def generate_viral_video(request: VideoRequest) -> VideoResult:
    """
    Main function to generate a viral video with the user's face.

    Flow:
    1. Generate viral script using OpenAI + Gemini validation
    2. Create video with D-ID (talking head from user's photo) - PRIMARY
    3. If D-ID fails, try Veo 3.1 (Gemini)
    4. If all video fails, create a viral poster image
    5. Return video/image URL and Twitter text
    """
    # Step 1: Generate the script (OpenAI + Gemini validation)
    script = await generate_viral_script(request)
    logger.info(f"Generated script: {script[:100]}...")

    # Step 2: Generate Twitter text
    twitter_text = generate_twitter_text(request)

    # Step 3: Create video with D-ID (PRIMARY - best for user photos)
    if DID_API_KEY:
        logger.info("Generating video with D-ID (talking head)...")
        video_result = await create_video_with_did(
            photo_base64=request.user_photo_base64,
            script=script,
            request=request
        )

        if video_result:
            logger.info("Video generated successfully with D-ID")
            return VideoResult(
                success=True,
                video_url=video_result["video_url"],
                video_id=video_result["video_id"],
                script=script,
                thumbnail_url=video_result.get("thumbnail_url"),
                twitter_text=twitter_text,
                fallback_used=False
            )

        # Try D-ID clips API as fallback
        logger.info("D-ID talks failed, trying clips API...")
        video_result = await create_video_with_did_clips(
            photo_base64=request.user_photo_base64,
            script=script,
            request=request
        )

        if video_result:
            logger.info("Video generated successfully with D-ID clips")
            return VideoResult(
                success=True,
                video_url=video_result["video_url"],
                video_id=video_result["video_id"],
                script=script,
                thumbnail_url=video_result.get("thumbnail_url"),
                twitter_text=twitter_text,
                fallback_used=False
            )
    else:
        logger.info("D-ID API key not configured, skipping D-ID")

    # Step 4: Fallback to Veo 3.1 (Gemini)
    if GEMINI_API_KEY:
        logger.info("D-ID failed, trying Veo 3.1 (Gemini)...")
        video_result = await create_video_with_veo(
            photo_base64=request.user_photo_base64,
            script=script,
            request=request
        )

        if video_result:
            logger.info("Video generated successfully with Veo 3.1")
            return VideoResult(
                success=True,
                video_url=video_result["video_url"],
                video_id=video_result["video_id"],
                script=script,
                thumbnail_url=video_result.get("thumbnail_url"),
                twitter_text=twitter_text,
                fallback_used=False
            )
    else:
        logger.info("Gemini API key not configured, skipping Veo")

    # Step 5: Fallback to poster image
    logger.info("All video generation failed, creating poster fallback...")
    poster_base64 = await create_viral_poster(request, script)

    if poster_base64:
        return VideoResult(
            success=True,
            video_url=f"data:image/png;base64,{poster_base64}",
            script=script,
            twitter_text=twitter_text,
            fallback_used=True,
            error="Video generation failed (D-ID and Veo). Created viral poster instead."
        )

    # Complete failure
    return VideoResult(
        success=False,
        script=script,
        twitter_text=twitter_text,
        error="Video and image generation failed. Please check API configurations (DID_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY)."
    )


async def check_video_status(video_id: str) -> Dict[str, Any]:
    """Check the status of a video generation operation (D-ID or Veo)"""

    # D-ID video IDs
    if video_id.startswith("did_"):
        if not DID_API_KEY:
            return {"error": "D-ID API not configured"}

        talk_id = video_id.replace("did_", "")
        did_base_url = "https://api.d-id.com"
        headers = {
            "Authorization": f"Basic {DID_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{did_base_url}/talks/{talk_id}",
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": data.get("status", "unknown"),
                        "video_id": video_id,
                        "result_url": data.get("result_url"),
                        "thumbnail_url": data.get("thumbnail_url"),
                        "source": "d-id"
                    }
                else:
                    return {"error": f"D-ID status check failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"D-ID status check error: {str(e)}"}

    # D-ID clip IDs
    if video_id.startswith("did_clip_"):
        if not DID_API_KEY:
            return {"error": "D-ID API not configured"}

        clip_id = video_id.replace("did_clip_", "")
        did_base_url = "https://api.d-id.com"
        headers = {
            "Authorization": f"Basic {DID_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{did_base_url}/clips/{clip_id}",
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": data.get("status", "unknown"),
                        "video_id": video_id,
                        "result_url": data.get("result_url"),
                        "thumbnail_url": data.get("thumbnail_url"),
                        "source": "d-id-clips"
                    }
                else:
                    return {"error": f"D-ID clip status check failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"D-ID clip status check error: {str(e)}"}

    # Veo video IDs starting with "veo_" are local IDs, not operation names
    if video_id.startswith("veo_"):
        return {"status": "completed", "video_id": video_id, "source": "veo"}

    # Otherwise, treat as Veo operation name and check status
    if not GEMINI_API_KEY:
        return {"error": "Gemini API not configured"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://generativelanguage.googleapis.com/v1beta/{video_id}",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=30.0
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status check failed: {response.status_code}"}
