"""Zentrale Konfiguration der Reel-Factory.

Übernimmt die Azure-OpenAI-Konventionen aus den anderen Portfolio-Projekten
(nlq-to-sql, ai-system-hub) und ergänzt die Variablen für Voiceover (ElevenLabs),
B-Roll (Pexels) und den Remotion-Render (lokal + Lambda).
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Azure OpenAI (identisch zu den übrigen Projekten) ---------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Günstiges Modell für Fülltext, teures für Hooks (Cost-Routing, siehe ai-system-hub)
AZURE_OPENAI_DEPLOYMENT_FAST = os.getenv("AZURE_OPENAI_DEPLOYMENT_FAST", AZURE_OPENAI_DEPLOYMENT)

# --- Nische & Affiliate-Funnel (AI-Tools) ----------------------------------
# Content-Library-Strategie: ALLE Reels drehen sich um EIN Affiliate-Produkt
# und trichtern auf denselben Link. Das maximiert die Conversion pro Klick.
NICHE = os.getenv("NICHE", "ai-tools")
AFFILIATE_TOOL_NAME = os.getenv("AFFILIATE_TOOL_NAME", "the tool")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK", "")  # landet in Bio / Pinned-Comment
AFFILIATE_DISCLOSURE = os.getenv("AFFILIATE_DISCLOSURE", "#ad")  # Pflicht-Kennzeichnung

# --- Asset-Provider --------------------------------------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# --- Remotion --------------------------------------------------------------
# Lokaler Render: Pfad zum Remotion-Projekt in diesem Repo.
REMOTION_PROJECT_DIR = os.getenv(
    "REMOTION_PROJECT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "remotion"),
)
REMOTION_COMPOSITION_ID = os.getenv("REMOTION_COMPOSITION_ID", "Reel")

# Lambda-Render (späterer Skalierungsschritt, siehe pipeline/render_lambda.py).
REMOTION_APP_REGION = os.getenv("REMOTION_APP_REGION")
REMOTION_APP_FUNCTION_NAME = os.getenv("REMOTION_APP_FUNCTION_NAME")
REMOTION_APP_SERVE_URL = os.getenv("REMOTION_APP_SERVE_URL")

# --- Video-Format ----------------------------------------------------------
FPS = 30
WIDTH = 1080
HEIGHT = 1920  # 9:16 vertikal für Reels / TikTok / Shorts

# --- Ausgabeverzeichnisse --------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ASSET_DIR = os.path.join(OUTPUT_DIR, "assets")


def has_azure() -> bool:
    """True, wenn echte Azure-Credentials gesetzt sind (sonst Offline-Stub)."""
    return bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_DEPLOYMENT)
