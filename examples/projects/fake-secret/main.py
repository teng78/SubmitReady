# This value is deliberately fake and exists only to test secret detection.
DEMO_TOKEN = "sk-proj-FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE"


def token_is_configured() -> bool:
    return bool(DEMO_TOKEN)
