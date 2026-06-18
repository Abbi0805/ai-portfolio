"""Guardrail-Schicht für Reels.

Adaptiert das deterministische Guard-Muster aus nlq-to-sql/validation/sql_guard.py:
statt SQL-Sicherheit prüfen wir Brand-Safety und Format-Constraints, bevor teure
Render-/Posting-Schritte laufen. Bei Hunderten automatisierten Reels ist diese
Stufe der Unterschied zwischen "skaliert sauber" und "Account gesperrt".
"""

from dataclasses import dataclass, field
from typing import List

from pipeline.schema import ReelSpec

# Begriffe, die in einer brand-safe Pipeline nie automatisiert gepostet werden sollten.
BLOCKED_TERMS = {
    "guaranteed returns",
    "get rich quick",
    "miracle cure",
    "financial advice",  # rechtlich heikel -> bewusst blocken
}

MAX_HOOK_WORDS = 16
MAX_SCENE_WORDS = 16


@dataclass
class GuardResult:
    ok: bool
    violations: List[str] = field(default_factory=list)


def check_reel(spec: ReelSpec) -> GuardResult:
    """Validiert ein Reel-Konzept. Gibt alle Verstöße zurück (nicht nur den ersten)."""
    violations: List[str] = []

    if len(spec.hook.split()) > MAX_HOOK_WORDS:
        violations.append(f"Hook zu lang (> {MAX_HOOK_WORDS} Wörter).")

    full_text = " ".join([spec.hook, spec.cta, *(s.voiceover for s in spec.scenes)]).lower()
    for term in BLOCKED_TERMS:
        if term in full_text:
            violations.append(f"Blockierter Begriff im Skript: '{term}'.")

    for i, scene in enumerate(spec.scenes):
        if len(scene.voiceover.split()) > MAX_SCENE_WORDS:
            violations.append(f"Szene {i + 1} zu lang (> {MAX_SCENE_WORDS} Wörter).")
        if not scene.b_roll_query.strip():
            violations.append(f"Szene {i + 1} hat keinen B-Roll-Suchbegriff.")

    if not spec.accent_color.startswith("#"):
        violations.append("accent_color ist keine Hex-Farbe.")

    return GuardResult(ok=not violations, violations=violations)
