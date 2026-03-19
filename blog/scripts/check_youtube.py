#!/usr/bin/env python3
"""
Juraj Orwell — YouTube Monitor
Checks configured YouTube channels for new videos via RSS feeds.
Adds any new videos to video-queue.json for processing by Cowork.
"""

import json
import os
import feedparser
from datetime import datetime, timezone

# Paths (relative to blog/ directory, where GitHub Actions runs)
CHANNELS_FILE = "channels.json"
QUEUE_FILE = "video-queue.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_rss_url(channel_id):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def check_channel(channel):
    """Fetch the RSS feed for a channel and return list of recent videos."""
    channel_id = channel.get("channel_id", "")
    if channel_id == "REPLACE_WITH_CHANNEL_ID" or not channel_id:
        print(f"  ⚠ Skipping '{channel['name']}' — channel ID not set yet.")
        return []

    rss_url = get_rss_url(channel_id)
    print(f"  Checking: {channel['name']} ({rss_url})")

    try:
        feed = feedparser.parse(rss_url)
        if feed.bozo:
            print(f"  ⚠ Could not parse feed for {channel['name']}")
            return []

        videos = []
        for entry in feed.entries[:5]:  # Check latest 5 videos
            videos.append({
                "video_id": entry.get("yt_videoid", ""),
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "channel_name": channel["name"],
                "channel_id": channel_id,
                "published": entry.get("published", ""),
                "description": entry.get("summary", "")[:500],  # First 500 chars
            })
        return videos

    except Exception as e:
        print(f"  ✗ Error fetching {channel['name']}: {e}")
        return []


def main():
    print("=== Juraj Orwell — YouTube Monitor ===")
    print(f"Running at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()

    # Load channels and queue
    channels = load_json(CHANNELS_FILE)
    queue = load_json(QUEUE_FILE)

    # Build a set of all already-seen video IDs
    seen_ids = set()
    for video in queue.get("pending", []):
        seen_ids.add(video["video_id"])
    for video in queue.get("processed", []):
        seen_ids.add(video["video_id"])

    print(f"Monitoring {len(channels)} channel(s). Already seen {len(seen_ids)} video(s).")
    print()

    new_videos = []

    for channel in channels:
        print(f"Checking channel: {channel['name']}")
        videos = check_channel(channel)

        for video in videos:
            if video["video_id"] and video["video_id"] not in seen_ids:
                print(f"  ✓ NEW VIDEO: {video['title']}")
                video["queued_at"] = datetime.now(timezone.utc).isoformat()
                new_videos.append(video)
                seen_ids.add(video["video_id"])
            else:
                print(f"  - Already seen: {video['title'][:60]}...")

        print()

    if new_videos:
        queue["pending"].extend(new_videos)
        save_json(QUEUE_FILE, queue)
        print(f"✅ Added {len(new_videos)} new video(s) to the queue.")
    else:
        print("✅ No new videos found.")

    print()
    print(f"Queue status: {len(queue['pending'])} pending, {len(queue['processed'])} processed")


if __name__ == "__main__":
    main()
