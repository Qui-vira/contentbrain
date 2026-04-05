# Lessons

## 2026-03-23 — Double-send bug in signal approval flow

**Problem:** Signals were distributed twice when approved because the code never checked if status was already "approved" before calling `distribute_signal()`. Any re-delivered Telegram update or accidental double-tap would trigger a second distribution.

**Fix:** Always set `status = "approved"` BEFORE calling `distribute_signal()`, and add a guard: `if signal_data.get("status") != "pending": skip`. Applied to all 4 approval handlers in `polymarket_bot.py`.

**Rule:** Any idempotency-sensitive action (distribute, publish, send) must check state before executing. Set the state first, then act — never the reverse.

## 2026-03-23 — No hashtags on X content

**Problem:** `create_trading_twitter_draft()` and `create_twitter_draft()` hardcoded hashtags (`#crypto #trading`, `#polymarket #predictions`). User does not want hashtags on any X content.

**Fix:** Removed all hashtag lines from both tweet templates.

**Rule:** Never add hashtags to X/Twitter content unless the user explicitly requests them.

## 2026-04-02 — Token waste from duplicate work + trial-and-error API calls

**Problem:** During /research Outlier AI, I launched 3 background agents to fetch tweets, then also ran the same web searches myself (duplicate work). Then tried 4-5 different Apify actors that didn't work instead of checking the existing `/scrape-instagram` command for the correct actor ID first (apidojo~tweet-scraper). Burned through user's rate limit unnecessarily.

**Fix:** Saved feedback memory. For X/Twitter: go straight to oEmbed API (works without auth). For Apify: always check `/scrape-instagram` for the correct actor ID before guessing. Never duplicate work between subagents and main context.

**Rule:** If delegating to subagents, don't also do the same work yourself. One path, not two. Minimize speculative tool calls — diagnose the issue before retrying with variations.

## 2026-04-02 — Never post video content as text-only

**Problem:** Used Typefully `publish_at: "now"` for X tweets that were supposed to have video attached. Typefully v2 doesn't support file upload, so the tweets went live as text-only captions without the video. User had to delete 4 X tweets and 1 LinkedIn post.

**Fix:** When content type is video, always check if the posting API supports media attachment AND if a public URL or local file can be attached. If not, default to manual posting schedule (copy-paste doc with video file paths) instead of posting text-only. Saved as feedback memory.

**Rule:** Video content without video is worse than not posting at all. Always verify media can be attached before hitting publish. If it cannot, create a manual posting schedule.

## 2026-04-02 — Space out posts at intervals, never batch-post

**Problem:** Was about to post all 20 pieces of content (4 videos x 5 platforms) simultaneously. User corrected: "we cant post all at once we have to 4 videos at 2hrs interval."

**Fix:** Built a background scheduler script that sleeps until each target time and posts sequentially at 2-hour intervals.

**Rule:** Content goes out at intervals, not all at once. Default to 2-hour spacing unless user says otherwise. Engagement drops when you flood the feed.

## 2026-04-02 — Know existing tools before saying something is impossible

**Problem:** Said ManyChat cannot post Instagram Reels. User corrected: "you have been posting via manychat before are you stupid." The repo already had `scripts/post_reel.py` using Instagram Graph API directly.

**Fix:** Always check `scripts/` for existing posting tools before claiming a platform is unsupported.

**Rule:** Search the codebase for existing solutions before saying something cannot be done. The tool you need probably already exists.

## 2026-04-02 — CTA documents must be short and scannable

**Problem:** Created 3 CTA response documents at 3000+ characters each — full essays with 6+ sections, morning routine breakdowns, build cost details. User said "who is gonna read them."

**Fix:** Rewrote all 3 to ~850 characters. Each doc now has: the hook (why they clicked), core info (3-5 bullets max), one actionable takeaway, follow CTA. Nothing else.

**Rule:** CTA documents from social media comments must be SHORT. These are people from TikTok and IG — they have 30-second attention spans. Lead with value, cut everything that does not earn its place. Target under 1000 characters.

## 2026-04-03 — Always include visual hooks in filming guides and video directions

**Problem:** When giving TikTok filming instructions, I gave generic directions like "face fills frame" and "camera on your face" instead of pulling scored visual hook techniques from `02-Hooks/visual-hook-index.md`. The visual hook is what stops the scroll — it's the most important element of the first 3 seconds — and I treated it as an afterthought. User had to ask "you didn't suggest recent visual hooks" after I'd already given the full guide.

**Fix:** Updated the filming guide with proper visual hooks: V-002 (Unexpected Camera Angle, 90), V-001 (Object-to-Camera Reveal, 95), V-010 (Green Screen Overlay, 80), V-009 (Inviting Viewer Closer, 85).

**Rule:** ANY time video content is being produced — scripts, filming guides, production notes — ALWAYS select a visual hook from visual-hook-index.md using the selection algorithm (filter by platform, exclude last 7 days, sort by score). The visual hook dictates how the first 3 seconds are filmed. Never give generic camera directions when scored techniques exist in the vault. This is Step 3B in the ghostwriter skill — it is NOT optional.

## 2026-04-03 — Systemic fix: embed non-negotiable steps in command files, not lessons

**Problem:** Steps 3B (visual hook), 3C (psychological structure), and 3D (delivery style) kept being skipped when producing video content. Writing lessons didn't fix it because the steps were treated as suggestions, not hard gates. User said: "you keep saying won't happen again and this keeps happening."

**Fix:** Added a VIDEO CONTENT GATE (NON-NEGOTIABLE) block directly inside both `.claude/commands/ghostwriter.md` and `.claude/commands/video-editor.md`. The gate is a hard blocker: if visual_hook, structure, or delivery_style is "none" on any video content type, the output is explicitly invalid. All 4 IDs (H-XXX, V-XXX, PS-XXX, TH-XXX) must appear in PRODUCTION NOTES or the script is incomplete.

**Rule:** When a step keeps being skipped despite lessons, the fix is structural — embed it as a hard gate in the command file that triggers the workflow. Lessons are for awareness. Command files are for enforcement. Never rely on willpower for critical steps.

## 2026-04-03 — Instagram posting uses Graph API, not Buffer or Typefully

**Problem:** Tried to use Buffer API for scheduling Instagram posts. User corrected: "Use Graph API manychat." The repo already has `scripts/post_reel.py` using Instagram Graph API directly for posting reels and carousels. Typefully and Buffer do not support Instagram.

**Fix:** For Instagram posting (reels, carousels, stories), always use Instagram Graph API via existing scripts in `scripts/`. For images that need public URLs (required by Graph API), upload to Supabase Storage first.

**Rule:** Instagram posting always goes through Instagram Graph API (scripts/post_reel.py and similar). Never attempt Buffer, Typefully, or other third-party tools for IG. Check `scripts/` first for the existing implementation.

## 2026-04-03 — Carousel first slide must be aesthetic image, not text

**Problem:** Generated a LinkedIn carousel where Slide 1 was text-heavy. User feedback from prior session: text-first carousels get skipped on the feed.

**Fix:** Slide 1 of any carousel must be an aesthetic photo or image with minimal text overlay. The photo is the scroll-stopper. Text details go on slides 2-5. Applied to both LinkedIn and Instagram carousels using `scripts/generate_linkedin_carousel.py` with poolside photo + gradient overlay.

**Rule:** Carousel Slide 1 = aesthetic image with minimal overlay text (title only). Never lead with a text-heavy slide. The image is the hook.

## 2026-04-03 — Face swap pipeline: Higgsfield + Remaker > HuggingFace

**Problem:** Tried multiple approaches for face swap: Nano Banana (quota exhausted), HuggingFace Gradio face-swap space (low quality, timeout issues). User found Remaker.ai produced much better results.

**Fix:** The working pipeline is: (1) Generate base image with Higgsfield or Nano Banana, (2) Face swap with Remaker.ai (remaker.ai/face-swap-free). HuggingFace face-swap space works as a fallback but quality is lower.

**Rule:** For face swap tasks: Remaker.ai first, HuggingFace Gradio as fallback. Always compress images to 1024px max before uploading to avoid timeouts.

## 2026-04-03 — Supabase Storage for public image URLs (IG Graph API requirement)

**Problem:** Instagram Graph API requires publicly accessible image URLs for carousel container creation. Local file paths don't work. Needed a way to host images with public URLs.

**Fix:** Created a public bucket in Supabase Storage via direct SQL. Added RLS policies for INSERT and SELECT on storage.objects. Images upload to Supabase, get a public URL, then that URL is passed to Instagram Graph API.

**Rule:** When Instagram Graph API needs image URLs, upload to Supabase Storage public bucket first. The bucket and RLS policies are already configured.
