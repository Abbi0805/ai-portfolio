"""Planner-Stufe: Topic -> strukturiertes Reel-Konzept (ReelSpec).

Übernimmt das Planner-Muster aus ai-workflow-orchestrator: ein LLM erzeugt einen
validierten, strukturierten Plan statt Freitext. Hier per `with_structured_output`,
sodass das Pydantic-Schema die Form garantiert.

Ohne Azure-Credentials liefert die Funktion einen Offline-Stub, damit die gesamte
Pipeline auch ohne Keys end-to-end durchläuft.
"""

from config import settings
from pipeline.schema import ReelSpec, Scene

SYSTEM_PROMPT = """Du bist Script-Writer für virale, faceless Short-Form-Videos
(Instagram Reels / TikTok / YouTube Shorts) in einer festen Content-Nische.

Regeln:
- Der Hook (erster Satz) muss in <2 Sekunden Neugier oder Spannung erzeugen.
- 3-5 Szenen, jede ein kurzer, gesprochener Satz (max. ~14 Wörter).
- Konkret, faktenbasiert, kein generisches LLM-Geschwafel, keine Floskeln.
- Pro Szene ein präziser englischer Stock-Footage-Suchbegriff (b_roll_query).
- Endet mit einem klaren, kurzen Call-to-Action.
"""


def plan_reel(topic: str) -> ReelSpec:
    """Erzeugt aus einem Topic ein vollständiges Reel-Konzept."""
    if not settings.has_azure():
        return _stub(topic)

    from langchain_openai import AzureChatOpenAI

    # Hooks profitieren vom stärkeren Modell -> Cost-Routing wie in ai-system-hub.
    llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        temperature=0.8,
    )
    structured = llm.with_structured_output(ReelSpec)
    return structured.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Erstelle ein Reel-Script zum Thema: {topic}"),
        ]
    )


def _stub(topic: str) -> ReelSpec:
    """Deterministischer Platzhalter ohne LLM-Aufruf (für Offline-Tests)."""
    return ReelSpec(
        topic=topic,
        hook=f"Most people get {topic} completely wrong.",
        scenes=[
            Scene(voiceover=f"Here is what nobody tells you about {topic}.", b_roll_query="city timelapse aerial"),
            Scene(voiceover="The data shows a very different story.", b_roll_query="financial charts screen"),
            Scene(voiceover="And it changes how you should think about it.", b_roll_query="person thinking window"),
        ],
        cta="Follow for the part two.",
        accent_color="#00E0A4",
        music_mood="uplifting",
    )
