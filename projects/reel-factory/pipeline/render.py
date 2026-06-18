"""Lokaler Render: RenderProps -> MP4 über die Remotion-CLI.

Das ist die konkrete Python<->Node-Brücke: Wir schreiben die Props als JSON und
rufen `npx remotion render` per subprocess auf. Für Batch-Rendering loopt run.py
einfach über mehrere Topics.

Skalierung später: pipeline/render_lambda.py ersetzt diesen Aufruf durch parallele
Cloud-Renders, ohne dass sich das Props-Format ändert.
"""

import json
import os
import subprocess

from config import settings
from pipeline.schema import RenderProps


def render_local(props: RenderProps, output_name: str) -> str:
    """Rendert ein einzelnes Reel lokal und gibt den Ausgabepfad zurück."""
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(settings.OUTPUT_DIR, f"{output_name}.mp4")

    # Props als temporäre JSON-Datei (umgeht Shell-Quoting bei großen Payloads).
    props_path = os.path.join(settings.OUTPUT_DIR, f"{output_name}.props.json")
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(props.model_dump(), f, ensure_ascii=False)

    cmd = [
        "npx",
        "remotion",
        "render",
        settings.REMOTION_COMPOSITION_ID,
        output_path,
        f"--props={props_path}",
    ]
    # cwd = Remotion-Projekt, sodass dessen package.json / Composition gefunden wird.
    subprocess.run(cmd, cwd=settings.REMOTION_PROJECT_DIR, check=True)
    return output_path
