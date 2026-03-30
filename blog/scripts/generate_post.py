#!/usr/bin/env python3
"""
Juraj Orwell — Content Pipeline
Reads video-queue.json, fetches YouTube transcripts, generates Slovak blog
post drafts using Claude, and saves them to blog/drafts/ as JSON files.
Run from the blog/ directory (same as check_youtube.py).
"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# ── Paths (relative to blog/) ──────────────────────────────────────────────
QUEUE_FILE  = "video-queue.json"
DRAFTS_DIR  = Path("drafts")

# ── Claude model ───────────────────────────────────────────────────────────
MODEL       = "claude-haiku-4-5-20251001"
MAX_TOKENS  = 2048
TRANSCRIPT_LIMIT = 9000   # chars sent to Claude (keeps cost low)


# ── Helpers ────────────────────────────────────────────────────────────────

def load_queue():
    if not Path(QUEUE_FILE).exists():
        return {"pending": [], "processed": []}
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def slugify(text):
    """Convert title to URL-safe slug (handles Slovak/Czech diacritics)."""
    nfd = unicodedata.normalize("NFD", text.lower())
    ascii_str = "".join(c for c in nfd if not unicodedata.combining(c))
    ascii_str = re.sub(r"[^a-z0-9\s-]", "", ascii_str)
    return re.sub(r"[\s-]+", "-", ascii_str).strip("-")[:60]


def get_transcript(video_id):
    """Fetch transcript for a YouTube video. Tries EN first, then any language."""
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
    except NoTranscriptFound:
        try:
            # Fall back to any available transcript in any language
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Try manual transcripts first, then generated, in any language
            transcript = None
            for t in transcript_list:
                transcript = t
                break  # take the first available
            if transcript is None:
                print(f"    ✗ No transcripts found at all.")
                return None
            segments = transcript.fetch()
            print(f"    Using transcript language: {transcript.language} ({transcript.language_code})")
        except Exception as e:
            print(f"    ✗ No transcript available: {e}")
            return None
    except TranscriptsDisabled:
        print("    ✗ Transcripts are disabled for this video.")
        return None
    except Exception as e:
        print(f"    ✗ Transcript error: {e}")
        return None

    full_text = " ".join(seg["text"] for seg in segments)
    return full_text


def generate_post(video, transcript, client):
    """Call Claude to produce a Slovak blog post JSON from the transcript or description."""

    title       = video.get("title", "Untitled Video")
    channel     = video.get("channel_name", "Unknown")
    video_url   = f"https://www.youtube.com/watch?v={video['video_id']}"
    description = video.get("description", "")

    if transcript:
        source_label = "Prepis videa (môže byť v rôznych jazykoch — angličtina, ruština, nemčina atď.):"
        source_text  = transcript[:TRANSCRIPT_LIMIT]
    else:
        source_label = "Popis videa (prepis nie je k dispozícii — vychádzaj z názvu a popisu):"
        source_text  = description[:2000] or "(Popis nie je dostupný)"

    prompt = f"""Si redaktor slovenského politického blogu "Juraj Orwell" — analytický, kritický, nezávislý.
Tvoja úloha je napísať originálny, zaujímavý blogový príspevok v slovenčine na základe tohto YouTube videa.

Video: {title}
Kanál: {channel}
URL: {video_url}

{source_label}
{source_text}

Napíš príspevok v slovenčine, ktorý:
• Má pútavý, analytický nadpis (NIE len preklad názvu videa)
• Analyzuje hlavné myšlienky a argumenty z videa
• Dáva ich do kontextu európskej a slovenskej politiky
• Je písaný živým, publicistickým štýlom (nie akademicky)
• Má 500–800 slov
• Obsah je vo formáte HTML — použi <p>, <h2>, <strong>, <em>, <ul>, <li>
  (BEZ tagov <html>, <body>, <head>, <style>)

Odpovedz VÝLUČNE platným JSON objektom (bez markdown obalov, bez komentárov):
{{
  "title": "Slovenský nadpis článku",
  "tags": ["tag1", "tag2", "tag3"],
  "content": "<p>HTML obsah...</p>"
}}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if Claude wraps the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def save_draft(video, post_data):
    """Persist the generated post as a JSON draft file."""
    DRAFTS_DIR.mkdir(exist_ok=True)

    slug      = slugify(post_data["title"])
    date_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename  = f"{date_str}-{slug}.json"

    draft = {
        "title":              post_data["title"],
        "slug":               slug,
        "date":               date_str,
        "tags":               post_data.get("tags", ["politika"]),
        "source_url":         f"https://www.youtube.com/watch?v={video['video_id']}",
        "content":            post_data["content"],
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "source_video_title": video.get("title", ""),
    }

    path = DRAFTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)

    print(f"    ✓ Draft saved: {filename}")
    return filename


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=== Juraj Orwell — Content Pipeline ===")
    print(f"Running at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("✗ ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    queue   = load_queue()
    pending = queue.get("pending", [])

    if not pending:
        print("✅ No pending videos in queue. Nothing to do.")
        return

    print(f"Found {len(pending)} pending video(s) to process.\n")

    still_pending  = []
    processed_list = queue.get("processed", [])
    new_drafts     = []

    for video in pending:
        video_id = video["video_id"]
        title    = video.get("title", video_id)
        print(f"▶ {title}")
        print(f"  ID: {video_id}")

        # 1. Transcript (optional — falls back to description if unavailable)
        print("  Fetching transcript…")
        transcript = get_transcript(video_id)
        if transcript:
            print(f"  Transcript: {len(transcript):,} chars")
        else:
            print("  No transcript — will use title + description instead.")

        # 2. Generate post (works with or without transcript)
        print("  Generating Slovak post with Claude…")
        try:
            post_data = generate_post(video, transcript, client)
        except json.JSONDecodeError as e:
            print(f"    ✗ JSON parse error: {e}")
            still_pending.append(video)
            continue
        except Exception as e:
            print(f"    ✗ Generation error: {e}")
            still_pending.append(video)
            continue

        # 3. Save draft
        draft_file = save_draft(video, post_data)
        new_drafts.append(draft_file)

        # 4. Mark processed
        video["processed_at"] = datetime.now(timezone.utc).isoformat()
        video["draft_file"]   = draft_file
        processed_list.append(video)
        print()

    # Update queue
    queue["pending"]   = still_pending
    queue["processed"] = processed_list
    save_queue(queue)

    print(f"\n✅ Done. Generated {len(new_drafts)} draft(s).")
    if new_drafts:
        for f in new_drafts:
            print(f"   • {f}")

    # Signal to GitHub Actions how many drafts were made
    gha_output = os.environ.get("GITHUB_OUTPUT")
    if gha_output:
        with open(gha_output, "a") as fh:
            fh.write(f"new_drafts={len(new_drafts)}\n")
            fh.write(f"draft_files={','.join(new_drafts)}\n")


if __name__ == "__main__":
    main()
