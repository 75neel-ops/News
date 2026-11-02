"""Configuration: API key, model name, output folder."""
import os

# Override with:  export GEMINI_MODEL=<any Gemini model that supports Google Search grounding>
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OUTPUT_DIR = os.getenv("NEWSLETTER_OUT", "output")
MAX_WORKERS = 4          # parallel Gemini calls
MAX_RETRIES = 3


def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise SystemExit(
            "Missing API key. Set it first:\n"
            "  export GEMINI_API_KEY='your-key'      (Linux/macOS)\n"
            "  setx GEMINI_API_KEY \"your-key\"        (Windows)"
        )
    return key
