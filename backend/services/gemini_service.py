import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are Bharat Mitra, an empathetic AI civic companion for Indian citizens. 
Reply in the same language the user asks (Hindi, English, Tamil, Bengali, Marathi, etc.). 
Simplify government jargon into 3-5 short friendly sentences. 
Always mention official portal/source when relevant.
Use respectful tone (aap in Hindi). Add relevant emojis. Be warm and helpful."""

# ✅ Updated to latest model
text_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)
vision_model = genai.GenerativeModel("gemini-2.0-flash")


def chat_with_bharat_mitra(message, history=None):
    try:
        chat = text_model.start_chat(history=history or [])
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_civic_issue(image_bytes, description=""):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        prompt = f"""Analyze this civic issue photo. Return JSON with these keys:
- category (pothole/garbage/streetlight/water/sewage/traffic/other)
- severity (low/medium/high)
- description (1-line)
- department (which municipal department handles this)
- suggested_action (what citizen should do next)

User note: {description}"""
        response = vision_model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


def recommend_schemes(profile, schemes):
    prompt = f"""User profile: {profile}

Available government schemes: {schemes}

Pick the TOP 3 most relevant schemes for this user based on their profile.

For each scheme, format like this:

✅ **[Scheme Name]**
💰 Benefit: ...
📋 Documents needed: ...
🔗 Apply at: ...
❓ Why this fits you: (1 line reason)

Be warm, encouraging, and use emojis! Reply in English."""
    response = text_model.generate_content(prompt)
    return response.text