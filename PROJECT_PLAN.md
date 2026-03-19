# Political Blog Automation — Project Plan

**Created for:** Jan
**Date:** March 18, 2026

---

## What We're Building

An automated system that monitors your favorite political YouTube channels, turns new videos into blog posts written in simple Slovak, and publishes them to your website — with your approval before anything goes live.

---

## How It Works (The Pipeline)

```
═══════════════════════════════════════════════
  CLOUD (GitHub Actions — runs 24/7, free)
═══════════════════════════════════════════════
  Check YouTube RSS feeds for new videos
        ↓
  New video found → save to queue file
        ↓
  Push update to GitHub repository
═══════════════════════════════════════════════

═══════════════════════════════════════════════
  YOUR COMPUTER (Cowork — when computer is on)
═══════════════════════════════════════════════
  Pick up queued videos
        ↓
  Get Video Transcript
        ↓
  Create Outline from Transcript
        ↓
  Write Blog Post from Outline
        ↓
  Rewrite for SEO + Simple Language
        ↓
  Translate to Slovak
        ↓
  Save as Draft → Email You for Review
        ↓
  You Approve → Published on Your Blog
═══════════════════════════════════════════════
```

---

## The 6 Phases

### Phase 1: Set Up the Blog Website
**What:** Create a simple, clean blog site and deploy it for free.

- Build a blog template using plain HTML and CSS (no complex frameworks)
- The design will be clean, mobile-friendly, and optimized for reading
- Deploy to **Netlify** (free subdomain like `yourname.netlify.app`)
- Set up the folder structure for blog posts

**You'll need to:** Create a free Netlify account at netlify.com

---

### Phase 2: Build the YouTube Monitor (Cloud)
**What:** A GitHub Actions workflow that checks your YouTube channels for new videos — runs in the cloud, no computer needed.

- Use YouTube RSS feeds (free, no API key needed) to detect new uploads
- Runs automatically twice a day on GitHub's servers (free tier: 2,000 min/month)
- When a new video is found, it's added to a queue file in the GitHub repository
- Track which videos have already been processed (so no duplicates)
- Your computer does NOT need to be on for this step

**You'll need to:** Create a free GitHub account (if you don't have one) and provide your YouTube channel URLs

---

### Phase 3: Build the Content Pipeline
**What:** The AI-powered system that turns videos into blog posts.

- **Step 1 — Get Transcript:** Download the video's subtitles/transcript automatically
- **Step 2 — Create Outline:** Claude analyzes the transcript and creates a structured outline
- **Step 3 — Write Blog Post:** Claude writes a full blog post from the outline
- **Step 4 — SEO + Simplify:** Claude rewrites the post to be search-engine friendly and easy to read (targeting roughly an 8th-grade reading level)
- **Step 5 — Translate to Slovak:** Claude translates the final post into natural, readable Slovak

**You'll need to:** Nothing — this is all handled by Claude

---

### Phase 4: Set Up the Review & Approval Flow
**What:** You get an email with each draft so you can approve or reject it.

- When a draft is ready, you receive an email with the post title and a preview
- Drafts are saved in a "drafts" folder on your blog
- To approve: you reply or click a link, and the post goes live
- To reject: you simply ignore it or reply with edits

**You'll need to:** Confirm which email address to use (currently: jankosara@gmail.com)

---

### Phase 5: Set Up Automation (Cloud + Cowork)
**What:** Wire together the cloud monitor and the local content generator.

- **GitHub Actions** (cloud): Runs twice daily to check YouTube feeds — always on, even if your computer is off
- **Cowork scheduled task** (your computer): Picks up any queued videos and generates blog posts
- If your computer was off when videos were queued, Cowork processes them as soon as you turn it on
- No videos are ever missed — the cloud catches them, your computer processes them when available

**You'll need to:** Nothing special — just turn on your computer at some point each day

---

### Phase 6: Testing & Go Live
**What:** Test the whole system end-to-end before going live.

- Add 1-2 test YouTube channels
- Run the pipeline manually to verify each step works
- Check the blog post quality, Slovak translation, and SEO
- Fine-tune the writing style and tone to your liking
- Go live!

---

## Important Notes

**About the cloud + local split:** YouTube monitoring runs on GitHub's servers for free, so new videos are never missed even if your computer is off. The blog post generation runs locally via Cowork when your computer is on. If you were away for a day, Cowork will simply process all queued videos the next time you open your laptop.

**About YouTube transcripts:** Not all videos have transcripts/subtitles available. For videos without them, we have two options: skip them, or use audio-to-text tools (which adds complexity). We'll start with transcript-available videos.

**About the free subdomain:** You'll get something like `jans-political-blog.netlify.app`. You can always upgrade to a custom domain later (typically ~$12/year).

---

## Suggested Build Order

| Step | Phase | Estimated Time |
|------|-------|---------------|
| 1 | Phase 1: Blog Website | ~1 session |
| 2 | Phase 2: YouTube Monitor | ~1 session |
| 3 | Phase 3: Content Pipeline | ~1-2 sessions |
| 4 | Phase 4: Email Review Flow | ~1 session |
| 5 | Phase 5: Scheduled Task | ~1 session |
| 6 | Phase 6: Testing | ~1 session |

Each "session" is roughly one conversation with me where we build that piece together.

---

## What You'll Need to Provide

1. **YouTube channel URLs** — the channels you want to follow
2. **Blog name/title** — what to call your blog
3. **GitHub account** — free signup at github.com (for the cloud monitor + hosting)
4. **Netlify account** — free signup at netlify.com (for blog hosting)
5. **Your preferred schedule** — what times of day to check for new videos
6. **Style preferences** — any preferences on how the blog posts should sound/feel

---

## Ready to Start?

We can begin with **Phase 1** (building the blog website) right now if you'd like. Just say the word!
