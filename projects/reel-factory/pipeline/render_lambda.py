"""Skalierungs-Stufe: Render auf Remotion Lambda (hunderte Reels parallel).

Nutzt das offizielle `remotion-lambda`-Pip-Paket. Das Props-Format ist identisch
zum lokalen Render — nur das Ziel wechselt von "eigene Maschine, sequenziell" zu
"AWS Lambda, massiv parallel". Das ist der eigentliche Skalierungs-Hebel für das Ziel
"hunderte Reels automatisiert".

Voraussetzung (einmalig, von dir auf AWS einzurichten):
    npx remotion lambda functions deploy
    npx remotion lambda sites create
und die REMOTION_APP_* Variablen in .env setzen.
"""

from config import settings
from pipeline.schema import RenderProps


def render_on_lambda(props: RenderProps) -> dict:
    """Stößt einen Lambda-Render an und pollt bis fertig. Gibt {output_file,...} zurück."""
    if not (settings.REMOTION_APP_REGION and settings.REMOTION_APP_FUNCTION_NAME and settings.REMOTION_APP_SERVE_URL):
        raise RuntimeError("REMOTION_APP_* Variablen fehlen – siehe .env.example und Lambda-Setup.")

    from remotion_lambda import Privacy, RenderMediaParams, RemotionClient

    client = RemotionClient(
        region=settings.REMOTION_APP_REGION,
        serve_url=settings.REMOTION_APP_SERVE_URL,
        function_name=settings.REMOTION_APP_FUNCTION_NAME,
    )

    params = RenderMediaParams(
        composition=settings.REMOTION_COMPOSITION_ID,
        privacy=Privacy.PUBLIC,
        input_props=props.model_dump(),
    )

    response = client.render_media_on_lambda(params)
    if not response:
        raise RuntimeError("Lambda-Render konnte nicht gestartet werden.")

    progress = client.get_render_progress(render_id=response.render_id, bucket_name=response.bucket_name)
    while progress and not progress.done:
        progress = client.get_render_progress(render_id=response.render_id, bucket_name=response.bucket_name)

    return {"output_file": progress.outputFile, "render_id": response.render_id, "bucket": response.bucket_name}
