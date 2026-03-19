# GitHub Setup Guide
## How to get the blog live and the YouTube monitor running

---

## Step 1 — Find the YouTube Channel ID

You need the channel ID for @GDiesen1 (and any other channels you add later).
It looks like this: `UCxxxxxxxxxxxxxxxxxx`

**How to find it:**
1. Go to **https://www.youtube.com/@GDiesen1** in your browser
2. Right-click anywhere on the page → click **"View Page Source"**
3. Press **Ctrl+F** (or Cmd+F on Mac) to search
4. Search for: `"channelId"`
5. You'll see something like: `"channelId":"UCa1b2c3d4e5f6g7h8i9j0"`
6. Copy that ID (starts with `UC`, about 24 characters long)

**Then:**
- Open the file `blog/channels.json` in Cursor or any text editor
- Replace `REPLACE_WITH_CHANNEL_ID` with the ID you copied
- Save the file

---

## Step 2 — Create a GitHub Repository

1. Go to **https://github.com** and sign in
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `juraj-orwell` (or any name you like)
   - **Visibility:** Public ✅ (required for free Netlify deployment)
   - Leave everything else as default
4. Click **"Create repository"**
5. GitHub will show you a page with setup instructions — keep this tab open

---

## Step 3 — Upload the Blog to GitHub

GitHub will show you a command like this on the setup page. Open **Terminal** (Mac) or **Command Prompt** (Windows) and run these commands one by one:

```bash
# Navigate to your blog folder first
cd "path/to/Political Blog/blog"

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial blog setup"

# Connect to your GitHub repo (copy the exact URL from GitHub's setup page)
git remote add origin https://github.com/YOUR_USERNAME/juraj-orwell.git

# Push everything to GitHub
git branch -M main
git push -u origin main
```

> **Tip:** Replace `YOUR_USERNAME` with your actual GitHub username, and `juraj-orwell` with whatever you named the repository.

---

## Step 4 — Connect to Netlify (Go Live!)

1. Go to **https://netlify.com** and sign up for a free account
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"GitHub"** and authorize Netlify to access your account
4. Select your `juraj-orwell` repository
5. Fill in build settings:
   - **Branch:** `main`
   - **Build command:** *(leave empty)*
   - **Publish directory:** `/` *(or leave as default)*
6. Click **"Deploy site"**
7. In about 30 seconds your blog will be live at a URL like `juraj-orwell.netlify.app`

---

## Step 5 — Enable the YouTube Monitor

The GitHub Actions workflow is already set up in the repository. It will run automatically at **7:00 AM and 7:00 PM UTC** every day.

To test it manually right now:
1. Go to your GitHub repository
2. Click the **"Actions"** tab
3. Click **"YouTube Monitor"** in the left sidebar
4. Click **"Run workflow"** → **"Run workflow"** (green button)
5. Watch the logs to see it check your channels

---

## Adding More YouTube Channels Later

Open `blog/channels.json` and add more entries:

```json
[
  {
    "name": "GDiesen1",
    "channel_id": "UCa1b2c3d4e5f6g7h8i9j0",
    "url": "https://www.youtube.com/@GDiesen1"
  },
  {
    "name": "Another Channel",
    "channel_id": "UCxxxxxxxxxxxxxxxxxx",
    "url": "https://www.youtube.com/@AnotherChannel"
  }
]
```

Then commit and push the change to GitHub — the monitor will pick it up automatically.

---

## How the Queue Works

When the monitor finds a new video, it adds it to `video-queue.json` under `"pending"`.
Cowork checks this file and processes each pending video into a blog post.
After processing, the video moves to `"processed"` so it's never done twice.

---

## Need Help?

If you get stuck on any step, just paste the error message into Cowork and I'll help you fix it.
