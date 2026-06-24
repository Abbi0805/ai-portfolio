"""Planner-Stufe: Topic -> strukturiertes Reel-Konzept (ReelSpec).

Übernimmt das Planner-Muster aus ai-workflow-orchestrator: ein LLM erzeugt einen
validierten, strukturierten Plan statt Freitext. Hier per `with_structured_output`,
sodass das Pydantic-Schema die Form garantiert.

Ohne Azure-Credentials liefert die Funktion einen Offline-Stub, damit die gesamte
Pipeline auch ohne Keys end-to-end durchläuft.
"""

from config import settings
from pipeline.schema import ReelSpec, Scene

# Nische: AI-Tools. Strategie: jedes Reel zeigt EINEN konkreten Use-Case des
# Affiliate-Tools und trichtert auf den Link in Bio (Content-Library-Funnel).
SYSTEM_PROMPT = """Du bist Script-Writer für virale, faceless AI-Tool-Tutorials
(Instagram Reels / TikTok / YouTube Shorts). Zielgruppe: Creators, Solopreneure,
Knowledge-Worker, die mit AI-Tools schneller arbeiten wollen.

Das Reel dreht sich um EIN konkretes Tool: {tool}. Es zeigt EINEN konkreten,
sofort nachvollziehbaren Use-Case (kein generischer "Tool X ist großartig"-Pitch).

Regeln:
- Hook (<2 Sek): ein konkretes Ergebnis/Problem, das Neugier weckt
  (z. B. "Ich habe 3 Stunden Recherche auf 4 Minuten reduziert").
- 3-5 Szenen, jede ein kurzer gesprochener Satz (max. ~14 Wörter), die den
  Workflow Schritt für Schritt zeigen. Konkret, kein Buzzword-Geschwafel.
- b_roll_query: zeige Screen-/UI-/Tech-Ästhetik (z. B. "screen recording laptop ui",
  "person typing keyboard closeup", "dashboard analytics screen").
- KEINE Übertreibungen ("ersetzt deinen Job", "garantiert"), keine Falschaussagen
  über Tool-Fähigkeiten.
- cta: Affiliate-Funnel, verweist auf den Link in Bio, z. B.
  "Link in Bio, um {tool} kostenlos zu testen.".
- tool_name im Output ist immer exakt: {tool}.
"""


def plan_reel(topic: str) -> ReelSpec:
    """Erzeugt aus einem Topic (= Use-Case) ein Reel rund um das Affiliate-Tool."""
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
    tool = settings.AFFILIATE_TOOL_NAME
    structured = llm.with_structured_output(ReelSpec)
    return structured.invoke(
        [
            ("system", SYSTEM_PROMPT.format(tool=tool)),
            ("human", f"Use-Case für ein Reel über {tool}: {topic}"),
        ]
    )


def _stub(topic: str) -> ReelSpec:
    """Deterministischer Platzhalter ohne LLM-Aufruf (für Offline-Tests)."""
    tool = settings.AFFILIATE_TOOL_NAME
    return ReelSpec(
        topic=topic,
        tool_name=tool,
        hook=f"This {tool} workflow saved me three hours today.",
        scenes=[
            Scene(voiceover="Here is the exact workflow, step by step.", b_roll_query="screen recording laptop ui"),
            Scene(voiceover="Paste your input and pick the template.", b_roll_query="person typing keyboard closeup"),
            Scene(voiceover="It does in seconds what took me hours.", b_roll_query="dashboard analytics screen"),
        ],
        cta=f"Link in bio to try {tool} for free.",
        accent_color="#00E0A4",
        music_mood="uplifting",
    )
