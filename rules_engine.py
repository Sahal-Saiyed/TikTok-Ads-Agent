# Simulated TikTok Ads music library
VALID_MUSIC_IDS = {
    "music_001": {"name": "Upbeat", "licensed": True},
    "music_002": {"name": "Chill", "licensed": True},
    "music_003": {"name": "Beat", "licensed": True},
    "music_004": {"name": "End", "licensed": False},
    "music_005": {"name": "Desert", "licensed": False},
    "music_006": {"name": "Sunshine", "licensed": True}
}

def validate_music_rules(objective, music_choice):
    """Enforces business rules for music based on objective."""
    if objective.lower() == "conversions" and music_choice == "none":
        return False, "Music is required for conversion campaigns."
    return True, None

def validate_existing_music(music_id):
    """Validates whether the music ID exists in the simulated catalog."""
    if music_id not in VALID_MUSIC_IDS:
        return False, "The provided music ID does not exist in the music library."
    return True, None