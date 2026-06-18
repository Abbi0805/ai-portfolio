"""Asset-Stufe: reichert ein ReelSpec zu RenderProps an.

Hier entsteht aus reinem Text das, was ein Reel "echt" wirken lässt:
- Voiceover via ElevenLabs (natürliche Stimme statt Roboter-TTS)
- echtes Stock-B-Roll via Pexels (gefilmte Realität, kein KI-Look)
- wort-genaues Untertitel-Timing via Whisper (der größte Watch-Time-Hebel)

Jede Funktion hat einen Offline-Stub, wenn der jeweilige API-Key fehlt, damit die
Pipeline ohne Credentials komplett durchläuft. Die echten Call-Shapes stehen daneben.
"""

import os
from typing import List

from config import settings
from pipeline.schema import CaptionToken, ReelSpec, RenderProps, RenderScene

WORDS_PER_SECOND = 2.6  # grobe Sprechrate zur Dauer-/Timing-Schätzung


def build_render_props(spec: ReelSpec) -> RenderProps:
    """Erzeugt aus dem kreativen Plan die finalen Remotion-Props inkl. Assets."""
    os.makedirs(settings.ASSET_DIR, exist_ok=True)

    full_script = " ".join([spec.hook, *(s.voiceover for s in spec.scenes), spec.cta])
    audio_url = synth_voiceover(full_script)

    # Szenen-Timing aus der geschätzten Sprechdauer pro Satz ableiten.
    scenes: List[RenderScene] = []
    cursor = len(spec.hook.split()) / WORDS_PER_SECOND  # Hook läuft vorab
    for scene in spec.scenes:
        dur = max(1.5, len(scene.voiceover.split()) / WORDS_PER_SECOND)
        scenes.append(
            RenderScene(b_roll_url=fetch_b_roll(scene.b_roll_query), from_sec=cursor, to_sec=cursor + dur)
        )
        cursor += dur
    total = cursor + len(spec.cta.split()) / WORDS_PER_SECOND

    captions = transcribe_captions(audio_url, full_script, total)

    return RenderProps(
        hook=spec.hook,
        cta=spec.cta,
        accent_color=spec.accent_color,
        audio_url=audio_url,
        duration_in_seconds=round(total, 2),
        scenes=scenes,
        captions=captions,
    )


def synth_voiceover(text: str) -> str:
    """ElevenLabs -> MP3. Stub: Pfad-Platzhalter ohne Key."""
    if not settings.ELEVENLABS_API_KEY:
        return "PLACEHOLDER_AUDIO"  # Remotion-Template zeigt Stille / Demo-Ton

    # Echte Anbindung (vereinfacht):
    #   from elevenlabs.client import ElevenLabs
    #   client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    #   audio = client.text_to_speech.convert(
    #       voice_id=settings.ELEVENLABS_VOICE_ID, model_id="eleven_turbo_v2_5", text=text)
    #   path = os.path.join(settings.ASSET_DIR, "voiceover.mp3")
    #   with open(path, "wb") as f: f.write(b"".join(audio))
    #   return path
    raise NotImplementedError("ElevenLabs-Key gesetzt – echte Synthese hier implementieren.")


def fetch_b_roll(query: str) -> str:
    """Pexels-Videosuche -> URL des besten vertikalen Clips. Stub ohne Key."""
    if not settings.PEXELS_API_KEY:
        return "PLACEHOLDER_BROLL"

    # Echte Anbindung (vereinfacht):
    #   import requests
    #   r = requests.get("https://api.pexels.com/videos/search",
    #       headers={"Authorization": settings.PEXELS_API_KEY},
    #       params={"query": query, "orientation": "portrait", "per_page": 1})
    #   return r.json()["videos"][0]["video_files"][0]["link"]
    raise NotImplementedError("Pexels-Key gesetzt – echte Suche hier implementieren.")


def transcribe_captions(audio_url: str, script: str, total_sec: float) -> List[CaptionToken]:
    """Whisper -> wort-genaues Timing. Stub: gleichmäßig verteilt über die Dauer."""
    words = script.split()
    if not words:
        return []
    step_ms = int((total_sec * 1000) / len(words))
    # Realer Pfad: @remotion/install-whisper-cpp oder Azure Whisper transkribiert die MP3
    # und liefert echte Wort-Zeitstempel. Hier gleichmäßige Verteilung als Fallback.
    return [CaptionToken(text=w, from_ms=i * step_ms, to_ms=(i + 1) * step_ms) for i, w in enumerate(words)]
