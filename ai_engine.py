import os
import json
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)

def explain_json(prompt: str) -> dict:
    """Safely gets structured reasoning from Gemini."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Updated to latest stable flash model
            contents=prompt
        )
        raw_text = response.text.strip()

        # Try direct JSON parse or regex extraction
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", raw_text)
            if match:
                return json.loads(match.group())

    except Exception as e:
        print(f"\n[WARN] AI request failed: {e}")

    # Fallback
    return {
        "explanation": "Temporary service issue prevented analysis.",
        "suggestion": "Please retry.",
        "retryable": True
    }


def explain(message: str) -> str:
    """Simple explanation for user feedback."""
    prompt = (
        "You are an assistant helping users create TikTok ad campaigns.\n"
        f"Explain this clearly and briefly: {message}"
    )
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except:
        return message


def reason_about_submission_failure(error_context):
    """Uses AI to interpret a submission failure."""
    prompt = f"""
    The TikTok ad submission failed: {error_context}

    Task:
    1. Explain why it failed
    2. Suggest corrective action
    3. Decide if retryable (true/false)

    Respond in JSON: {{ "explanation": "...", "suggestion": "...", "retryable": bool }}
    """
    return explain_json(prompt)


def interpret_oauth_error(status, response):
    """Interprets OAuth-related failures."""
    # [cite: 26, 27, 28, 29, 30]
    error_str = str(response).lower()

    if status == 400 and "client_secret" in error_str:
        return {"explanation": "Invalid credentials.", "suggestion": "Check Client ID/Secret."}

    if status == 403 and "permission" in error_str:
        return {"explanation": "Missing Permissions.", "suggestion": "Request 'ads_management' scope."}

    if status in [401, 403] and "token" in error_str:
        return {"explanation": "Token expired.", "suggestion": "Re-authenticate."}

    if status == 403 and ("geo" in error_str or "region" in error_str):
        return {"explanation": "Geo-restriction.", "suggestion": "Use a supported region."}

    return {"explanation": "Unknown OAuth error.", "suggestion": "Retry authentication."}