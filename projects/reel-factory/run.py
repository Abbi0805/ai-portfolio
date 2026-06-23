"""End-to-End-Orchestrator der Reel-Factory.

    topic -> plan -> guardrail -> assets -> render -> publish

Batch-Modus: über eine Liste von Topics loopen = "skalierbar hunderte Reels".
Lokal sequenziell (jeder Render nutzt alle Kerne); für echte Parallelität auf
render_on_lambda() umstellen (siehe pipeline/render_lambda.py).

Usage:
    python run.py "Warum Zinseszins unterschätzt wird"
    python run.py --batch topics.txt
"""

import sys

from pipeline.assets import build_render_props
from pipeline.guardrail import check_reel
from pipeline.planner import plan_reel
from pipeline.publish import publish_reel
from pipeline.render import render_local


def slugify(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower())[:40].strip("-")


def make_reel(topic: str) -> dict:
    """Erzeugt aus einem Topic ein fertiges (lokal gerendertes) Reel."""
    print(f"\n=== {topic} ===")

    spec = plan_reel(topic)
    print(f"  Hook: {spec.hook}")

    guard = check_reel(spec)
    if not guard.ok:
        print(f"  ABGELEHNT durch Guardrail: {guard.violations}")
        return {"topic": topic, "status": "rejected", "violations": guard.violations}

    props = build_render_props(spec)
    print(f"  {len(props.scenes)} Szenen, ~{props.duration_in_seconds}s, {len(props.captions)} Caption-Tokens")

    video_path = render_local(props, slugify(topic))
    print(f"  gerendert: {video_path}")

    result = publish_reel(
        video_path,
        caption=spec.hook,
        hashtags=["aitools", "productivity", "automation", slugify(spec.tool_name)],
    )
    print(f"  publish: {result['status']}")
    return {"topic": topic, "status": "ok", "video": video_path, "publish": result}


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--batch":
        with open(args[1], encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
    else:
        topics = [" ".join(args)]

    for topic in topics:
        make_reel(topic)


if __name__ == "__main__":
    main()
