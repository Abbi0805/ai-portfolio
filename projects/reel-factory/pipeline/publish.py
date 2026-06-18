"""Publishing-Stufe: gerendertes Reel automatisiert posten.

WICHTIG / ehrlich: Automatisiertes Posten läuft ausschließlich über die offiziellen
Graph-APIs (Instagram Content Publishing API, TikTok Content Posting API). Inoffizielle
"Bots" führen zur Account-Sperre. Diese Datei ist bewusst ein dokumentiertes Skelett:
sie zeigt den Ablauf, postet aber erst, wenn echte Tokens gesetzt sind.

Transparenz-Hinweis: KI-/synthetischer Content unterliegt Kennzeichnungspflichten
(Plattform-Richtlinien + EU AI Act). Das `made_with_ai`/Label-Flag gehört in den
echten Publish-Call.
"""

import os

from config import settings


def publish_reel(video_path: str, caption: str, hashtags: list[str]) -> dict:
    """Lädt ein Reel hoch und veröffentlicht es. Dry-Run ohne Social-Tokens."""
    ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    full_caption = caption + "\n\n" + " ".join(f"#{h}" for h in hashtags)

    if not (ig_token and ig_user_id):
        # Dry-Run: protokollieren statt posten, damit die Pipeline ohne Keys läuft.
        return {"status": "dry_run", "video": video_path, "caption": full_caption}

    # Echter Ablauf (Instagram Reels, zweistufig):
    #   1) POST /{ig_user_id}/media  (media_type=REELS, video_url=..., caption=...)
    #      -> liefert creation_id
    #   2) POST /{ig_user_id}/media_publish  (creation_id=...)
    # Hinweis: video_url muss öffentlich erreichbar sein (z. B. S3/CDN aus dem Lambda-Render).
    raise NotImplementedError("Instagram-Tokens gesetzt – echten Graph-API-Upload hier implementieren.")
