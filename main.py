import os
from dotenv import load_dotenv

# Import from our new consolidated files
from rules_engine import validate_music_rules, validate_existing_music
from ai_engine import explain, interpret_oauth_error, reason_about_submission_failure
from tiktok_integration import get_authorization_url, exchange_code_for_token, submit_ad_mock

load_dotenv()

CLIENT_ID = os.getenv("TIKTOK_CLIENT_ID")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080/"

agent_state = {
    "campaign_name": "",
    "objective": "",
    "creative": {
        "text": "",
        "cta": "",
        "music_id": ""}
}

print("=== TikTok Ad Creation Agent ===")

# --- 1. Collect Inputs (Campaign, Objective, Text, CTA) ---

# Campaign details
while True:
    campaign = input("Campaign name (min 3 characters): ").strip()

    if len(campaign) < 3:
        print("\n " + explain("Campaign name must be at least 3 characters long."))
        continue

    break

agent_state["campaign_name"] = campaign

# Objective
while True:
    objective = input("Objective (Traffic/Conversions): ").strip().lower()

    if objective not in ["traffic", "conversions"]:
        print("\n " + explain(
            "Objective must be either Traffic or Conversions."
        ))
        continue

    objective = objective.capitalize()
    break

agent_state["objective"] = objective

# Ad Text
while True:
    ad_text = input("Ad Text (max 100 characters): ").strip()

    if not ad_text:
        print("\n " + explain("Ad text is required."))
        continue

    if len(ad_text) > 100:
        print("\n " + explain(
            f"Ad text is too long ({len(ad_text)} characters). Maximum allowed is 100."
        ))
        continue

    break

agent_state["creative"]["text"] = ad_text

# Create a list of allowed CTA's(Call to Action)

ALLOWED_CTAS = [
    "Shop Now",
    "Learn More",
    "Sign Up",
    "Download",
    "Contact Us"
]

while True:
    print("\nAvailable CTAs:")
    for cta in ALLOWED_CTAS:
        print("-", cta)

    cta = input("Choose a CTA: ").strip()

    if cta not in ALLOWED_CTAS:
        print("\n " + explain(
            "Please choose a CTA from the available options."
        ))
        continue

    break

agent_state["creative"]["cta"] = cta


# --- 2. Music Selection ---
while True:
    music_choice = input("\nMusic option (existing / upload / none): ").strip().lower()

    valid, error = validate_music_rules(agent_state["objective"], music_choice)
    if not valid:
        print(f"\n {explain(error)}")
        continue

    if music_choice == "existing":
        music_id = input("Enter existing Music ID: ").strip()
        is_valid, error = validate_existing_music(music_id)
        if not is_valid:
            print(f"\n {explain(error)}")
            continue
        break

    elif music_choice == "upload":
        print("Uploading custom music...")
        music_id = f"upl_{agent_state['campaign_name'].lower()[:5]}"
        print(f"Generated Music ID: {music_id}")
        break

    elif music_choice == "none":
        music_id = None
        break

agent_state["creative"]["music_id"] = music_id

# --- 3. OAuth Step ---
print("\n=== TikTok OAuth Authorization (PKCE) ===")
auth_url = get_authorization_url(CLIENT_ID, REDIRECT_URI)

print("\n1. Open this URL in your browser:")
print(auth_url)
print("\n2. Authorize the app.")
print("3. When you see the 'Unable to connect' page, look at the URL bar.")
print("4. Copy the code from: .../?code=THIS_CODE_HERE&state=...")
auth_code = input("\nPaste the authorization code here: ").strip()

access_token = None

if auth_code:
    status, token_response = exchange_code_for_token(
        CLIENT_ID, CLIENT_SECRET, auth_code, REDIRECT_URI
    )

    print(token_response)

    if status == 200 and "access_token" in token_response:
        access_token = token_response["access_token"]
        print("\n OAuth successful.")
    else:
        oauth_error = interpret_oauth_error(status, token_response)
        print("\n OAuth failed:")
        print("Reason:", oauth_error["explanation"])
        print("Fix:", oauth_error["suggestion"])
        access_token = None
        exit(1)

# --- 4. Submission ---
print("\n=== Attempting Ad Submission ===")
result = submit_ad_mock(agent_state, access_token)

if not result.get("success"):
    ai_reasoning = reason_about_submission_failure(result)
    print(f"\n Ad submission failed: {ai_reasoning['explanation']}")
    print(f"Suggestion: {ai_reasoning['suggestion']}")
else:
    print(f"\n Ad submitted successfully! Ad ID: {result['ad_id']}")