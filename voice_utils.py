def pick_preferred_voice(language, voices):
    if not voices:
        return None

    preferred_prefixes = ["ur", "ur-pk", "ur-in"] if str(language).lower() == "ur" else ["en", "en-us", "en-gb", "en-au"]

    for voice in voices:
        lang = str(voice.get("lang", "")).lower()
        if any(lang.startswith(prefix) for prefix in preferred_prefixes):
            return voice

    for voice in voices:
        name = str(voice.get("name", "")).lower()
        if str(language).lower() == "ur" and "urdu" in name:
            return voice
        if str(language).lower() != "ur" and "english" in name:
            return voice

    return voices[0]
