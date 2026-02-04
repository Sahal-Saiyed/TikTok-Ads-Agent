import secrets
import hashlib
import base64
import requests


# --- PKCE Logic ---
def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(verifier):
    sha256 = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(sha256).decode("utf-8").rstrip("=")

# --- OAuth Logic ---
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
_verifier_store = {}

def get_authorization_url(client_id, redirect_uri, state="secure_state"):
    verifier = generate_code_verifier()
    _verifier_store[state] = verifier

    # return the url at redirect_uri i.e.localhost with auth_code
    return (
        f"{AUTH_URL}?client_key={client_id}&response_type=code"
        f"&scope=user.info.basic&redirect_uri={redirect_uri}"
        f"&state={state}&code_challenge={generate_code_challenge(verifier)}"
        f"&code_challenge_method=S256"
    )

def exchange_code_for_token(client_id, client_secret, auth_code, redirect_uri, state="secure_state"):
    verifier = _verifier_store.get(state)
    if not verifier:
        return None, {"error": "Missing PKCE verifier"}

    try:
        response = requests.post(TOKEN_URL, data={
            "client_key": client_id,
            "client_secret": client_secret,
            "code": auth_code,  # Changed from auth_code
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": verifier
        }, timeout=10)

        # If the response is not JSON, it might raise an error,
        # so we check status first or handle parsing safely.
        if response.status_code == 200:
            return response.status_code, response.json()
        else:
            return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}

# --- Mock Submission Logic ---
def submit_ad_mock(payload, access_token):
    if not access_token:
        return {"error_type": "INVALID_OAUTH_TOKEN", "status": 401}
    # TikTok access tokens usually don't start with "login_" in production,
    # but for this logic we keep it as mock exception.
    elif access_token.startswith("login_"):
        return {"error_type": "MISSING_ADS_PERMISSION", "status": 403}
    elif payload["campaign_name"].lower().startswith("geo"):
        return {"error_type": "GEO_RESTRICTED", "status": 403}
    else:
        return {"success": True, "ad_id": "ad_123456"}