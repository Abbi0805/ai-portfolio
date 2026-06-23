"""Die Schemas sind der *Vertrag* zwischen Python und Remotion.

`ReelSpec`   = kreativer Output des Planners (Text, noch ohne Assets).
`RenderProps`= das, was Remotion als `inputProps` (JSON) tatsächlich konsumiert.

Die Form von `RenderProps` ist 1:1 im Remotion-Projekt als Zod-Schema gespiegelt
(remotion/src/schema.ts). Ändert sich hier ein Feld, muss es dort mitgezogen werden —
das ist die einzige Kopplung zwischen der Python- und der Node-Welt.
"""

from typing import List

from pydantic import BaseModel, Field

# --- Stufe 1: kreativer Plan (Planner-Output) ------------------------------


class Scene(BaseModel):
    """Eine Szene = ein gesprochener Satz + die Suchanfrage für passendes B-Roll."""

    voiceover: str = Field(..., description="Was in dieser Szene gesprochen wird.")
    b_roll_query: str = Field(..., description="Stock-Footage-Suchbegriff, z. B. 'city skyline night'.")


class ReelSpec(BaseModel):
    """Vollständiges Reel-Konzept, vom Planner-LLM erzeugt (AI-Tools-Nische)."""

    topic: str
    tool_name: str = Field(..., description="Das AI-Tool, um das sich dieses Reel dreht (Affiliate-Produkt).")
    hook: str = Field(..., description="Erste 1-2 Sekunden. Wichtigster Satz für die Watch-Time.")
    scenes: List[Scene] = Field(..., min_length=2, max_length=6)
    cta: str = Field(..., description="Affiliate-CTA, verweist auf den Link in Bio.")
    accent_color: str = Field("#00E0A4", description="Hex-Akzentfarbe für Untertitel/Branding.")
    music_mood: str = Field("uplifting", description="Stimmung für die Hintergrundmusik-Auswahl.")


# --- Stufe 2: was Remotion rendert (nach Asset-Anreicherung) ---------------


class CaptionToken(BaseModel):
    """Wort-genaues Untertitel-Timing (kommt aus Whisper nach dem Voiceover)."""

    text: str
    from_ms: int
    to_ms: int


class RenderScene(BaseModel):
    b_roll_url: str
    from_sec: float
    to_sec: float


class RenderProps(BaseModel):
    """Exakt diese Struktur landet als JSON in Remotion. Spiegel: remotion/src/schema.ts."""

    hook: str
    cta: str
    tool_name: str = Field(..., description="AI-Tool im Fokus – wird als Badge eingeblendet.")
    accent_color: str
    audio_url: str = Field(..., description="URL/Pfad zum Voiceover-Audio.")
    duration_in_seconds: float
    scenes: List[RenderScene]
    captions: List[CaptionToken]
