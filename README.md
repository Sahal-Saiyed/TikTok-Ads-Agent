# TikTok-Ads-Agent
AI-assisted command-line agent for simulating TikTok ad creation workflows. Implements OAuth 2.0 Authorization Code flow with PKCE, business rule validation, and Gemini-powered error reasoning, using mock TikTok Ads endpoints to demonstrate campaign creation and submission logic.

Important Note: This project is intentionally built with mock endpoints for ad submission and uses TikTok’s real OAuth endpoints. Currently, an access_token is not successfully received because the authorization code consistently expires before token exchange. This behavior is documented in detail below.

## Project Structure

- main.py
- ai_engine.py
- rules_engine.py
- tiktok_integration.py
- .env (to be created by user)
- README.md

## OAuth-related Functions

**1. get_authorization_url(...)**
- Generates TikTok authorization URL
- Implements PKCE (code_verifier + code_challenge)
  
**2. exchange_code_for_token(...)**
- Attempts to exchange authorization code for an access token
- Uses TikTok’s official OAuth token endpoint

**Mock Endpoint**
- submit_ad_mock(payload, access_token)
- Simulates TikTok ad submission behavior
- Returns predefined error responses based on token and payload

### Mock Ad Submission
- submit_ad_mock(payload, access_token) simulates TikTok Ads API behavior:
**Condition	Mock Response**
1. No access token	--> 401 INVALID_OAUTH_TOKEN
2. Token starts with login_	--> 403 MISSING_ADS_PERMISSION
3. Campaign name starts with geo	--> 403 GEO_RESTRICTED
4. Otherwise	Success with ad_id

These mocks allow testing downstream logic without real ad creation.

### OAuth Limitation (Known Issue)
**Access Token Not Received**
Although the OAuth authorization step completes and returns a code, the application does not receive an access_token during token exchange.

**Observed Behavior:** - TikTok token endpoint responds with an error indicating the auth_code has expired - This occurs even when the code is exchanged immediately

**Impact:** - access_token remains None - Ad submission always fails at the OAuth validation stage

**Likely Causes:** - TikTok OAuth requires a verified app with Ads permissions - Sandbox / development apps may invalidate codes immediately - PKCE + redirect URI must exactly match dashboard configuration

This limitation is expected in the current environment and is intentionally handled and surfaced to the user.

### Environment Variables (.env file)
**What is .env?**
- A .env file is used to store sensitive configuration values outside the source code. This prevents accidental credential leaks and supports environment-based configuration.
**Why it is needed**
- Keeps API keys and secrets out of version control
- Allows easy switching between environments
- Required for OAuth and AI integration

### How to create .env
- Create a file named *.env* in the project root:
GEMINI_API_KEY=your_gemini_api_key_here
TIKTOK_CLIENT_ID=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

## How to Run the Program
**Prerequisites**
- Python 3.0+
- Virtual environment (recommended)

**Install Dependencies**
- pip install python-dotenv google-generativeai requests

*Run the Application*
- python main.py
- Follow the interactive prompts in the terminal.

## Project Workflow
This section explains the end-to-end workflow of the TikTok Ad Creation Agent, from user input to (mock) ad submission.

***Step 1: Application Start***
- The program starts by running main.py.
- Environment variables are loaded from .env (TikTok credentials and Gemini API key).
- An empty agent_state object is initialized to store campaign data.

***Step 2: Campaign & Creative Input Collection***
- The user is prompted to enter:
- Campaign name
- Campaign objective (Traffic or Conversions)
- Ad text (validated for length)
- Call-to-Action (CTA) from a predefined list
- Invalid inputs are rejected.
- Human-friendly error explanations are generated using ai_engine.explain().

***Step 3: Business Rules Validation (Music Selection)***
- The user selects a music option: existing, upload, or none.
- rules_engine.validate_music_rules() enforces objective-based rules.
- Example: Conversion campaigns require music.
- If an existing track is chosen, validate_existing_music() checks it against a mock music library.
This step ensures policy compliance before OAuth or submission.

***Step 4: OAuth Authorization (PKCE Flow)***
- The application generates a TikTok authorization URL using get_authorization_url().
- PKCE is applied using a code_verifier and code_challenge.
- The user opens the URL, authorizes the app, and copies the code from the redirect URL.
This simulates a real-world secure OAuth login flow.

***Step 5: Authorization Code Exchange***
- The pasted authorization code is exchanged using exchange_code_for_token().
- The application attempts to retrieve an access_token from TikTok.
- Current Limitation: - The exchange consistently fails due to the authorization code expiring.
- As a result, no access_token is obtained.
- OAuth errors are interpreted using interpret_oauth_error() to provide clear feedback.

***Step 6: Mock Ad Submission***
- The system proceeds to ad submission using submit_ad_mock().
- Since no valid access_token is available, submission fails predictably.
- The failure context is passed to reason_about_submission_failure().
The AI explains: - Why submission failed - Whether it is retryable - What corrective action might be required

***Step 7: User Feedback & Exit***
- The user receives a structured explanation of the failure.
- The program exits gracefully after surfacing actionable insights.

## Conclusion
* This codebase demonstrates a clean separation of concerns between: - Workflow orchestration - Business rules - OAuth integration - AI-based reasoning
* Despite the OAuth token limitation, the project successfully showcases how an AI-assisted agent can guide users through complex API-driven workflows in a structured and user-friendly manner.

# Disclaimer
* This project is intended for educational and architectural demonstration purposes. It does not create *real TikTok ads*.
