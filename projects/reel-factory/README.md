# reel-factory

Automatisierte, skalierbare Pipeline für **faceless Short-Form-Videos** (Instagram Reels /
TikTok / YouTube Shorts): Topic → Script → Voiceover → B-Roll → animierte Untertitel →
gerendertes vertikales Video → (optional) Auto-Posting.

Verbindet die **Python/Azure-LLM-Welt** der übrigen Portfolio-Projekte mit der
**Node/React-Renderschicht** von [Remotion](https://www.remotion.dev/).

## Problem

"Hunderte Reels automatisiert posten" scheitert selten am Rendern, sondern an drei Dingen:
Content-Qualität bei Volumen, Kostenkontrolle und Plattform-Konformität. Diese Pipeline
adressiert alle drei mit denselben Mustern, die die anderen Projekte schon nutzen.

## Architektur

```
topic
  │
  ▼
Planner-LLM (Azure OpenAI)        ── Muster aus ai-workflow-orchestrator
  │  ReelSpec (Pydantic)
  ▼
Guardrail (Brand-Safety/Format)  ── Muster aus nlq-to-sql
  │
  ▼
Asset-Stufe: ElevenLabs (Voice) + Pexels (B-Roll) + Whisper (Caption-Timing)
  │  RenderProps (Pydantic)  ══ JSON ══►  Zod-Schema  (DIE Python↔Node-Brücke)
  ▼
Remotion-Render   lokal (Batch)  ODER  Lambda (hunderte parallel)
  │  out/<slug>.mp4
  ▼
Auto-Post (Instagram/TikTok Graph API)  +  Cost-/Performance-Logging
```

### Die Brücke: ein JSON-Vertrag

Python und Remotion teilen **nur** die Form von `RenderProps`:

- Python-Seite: [`pipeline/schema.py`](pipeline/schema.py) → `RenderProps` (Pydantic)
- Node-Seite: [`remotion/src/schema.ts`](remotion/src/schema.ts) → `reelProps` (Zod)

Beide müssen dieselbe Struktur haben. `render.py` schreibt die Props als JSON-Datei und
ruft `npx remotion render` per subprocess auf. Mehr Kopplung gibt es nicht — die Node-Welt
muss kein Python kennen und umgekehrt.

## Was aus den anderen Projekten wiederverwendet wird

| Konzept | Quelle | Hier als |
|---|---|---|
| Planner erzeugt strukturierten Plan | `ai-workflow-orchestrator` | `pipeline/planner.py` (Script-Generierung) |
| Deterministische Guardrails | `nlq-to-sql/validation/sql_guard.py` | `pipeline/guardrail.py` (Brand-Safety) |
| Cost-Routing (billig/teuer pro Schritt) | `ai-system-hub` Model-Router | `AZURE_OPENAI_DEPLOYMENT_FAST` |
| `.env`-Konvention | alle Projekte | `config/settings.py` |
| Strukturiertes Logging | `ai-system-hub/monitoring` | nächster Schritt (siehe unten) |

## Setup

```bash
# 1. Python-Seite
pip install -r requirements.txt
cp .env.example .env        # Azure / ElevenLabs / Pexels Keys eintragen

# 2. Remotion-Seite (einmalig)
cd remotion && npm install && cd ..
```

> Läuft auch **ohne API-Keys**: Planner, Voiceover und B-Roll fallen dann auf Offline-Stubs
> zurück, sodass die gesamte Pipeline end-to-end durchläuft (Platzhalter-Video).

## Nutzung

```bash
# Einzelnes Reel
python run.py "Warum Zinseszins unterschätzt wird"

# Batch (eine Topic-Zeile pro Reel) – das ist die "skalierbare" Schleife
python run.py --batch topics.txt
```

Remotion-Template interaktiv editieren:

```bash
cd remotion && npm run dev      # öffnet das Remotion Studio
```

## Skalierung: von lokal zu hunderten Reels

1. **Jetzt (lokal):** `run.py --batch` rendert sequenziell. Gut bis ~Dutzende/Tag.
2. **Cloud (parallel):** [`pipeline/render_lambda.py`](pipeline/render_lambda.py) nutzt das
   offizielle `remotion-lambda`-Paket → hunderte Renders parallel. Props-Format bleibt gleich.
3. **Noch zu ergänzen** (vom Subagent-Scan als fehlend identifiziert):
   - **Job-Queue** (Redis/SQS) statt sequenzieller Schleife
   - **Scheduler** (APScheduler/Celery) für festes Posting-Raster
   - **Performance-Feedback-Loop**: Reichweiten-Daten zurück in den Planner

## Ehrliche Einordnung (bitte lesen)

- **Remotion erzeugt Motion-Graphics, keine gefilmte Realität.** Es wird *kein* Video
  produzieren, das wie eine echte, sich selbst filmende Person aussieht. Stark ist es bei
  faceless Content (Fakten, Finanz, Daten-Storys, News-Recaps) — B-Roll + Voiceover +
  Untertitel wirken professionell und "echt genug", ohne eine Person vorzutäuschen.
- **Auto-Posting nur über offizielle APIs.** Inoffizielle Bots = Account-Sperre.
- **Kennzeichnungspflicht.** KI-/synthetischer Content muss als solcher markiert werden
  (Plattform-Richtlinien + EU AI Act). Das Label-Flag gehört in den Publish-Call.
- **Volumen ≠ Reichweite.** Der Hebel ist Hook-Qualität + Nischenkonsistenz, nicht
  Render-Durchsatz. Die Pipeline liefert Volumen *bei gleichbleibender Qualität* — die
  Nische musst du wählen.

## Stack

Python 3.11 · Azure OpenAI · Pydantic v2 · ElevenLabs · Pexels · Remotion 4 (React 19) · Node 22
