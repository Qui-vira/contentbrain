# API Setup Guide

Instructions for setting up each API key used in the publishing pipeline. All keys go in .env in the vault root.

---

## Typefully API Key
1. Go to typefully.com and sign in
2. Go to Settings → API
3. Copy your API key
4. Paste in .env as TYPEFULLY_API_KEY

## Buffer Access Token
1. Go to buffer.com and sign in
2. Go to buffer.com/developers/api
3. Create an app or get your access token
4. Run: curl https://api.bufferapp.com/1/profiles.json?access_token=YOUR_TOKEN
5. Note the profile IDs for TikTok and Instagram
6. Paste in .env as BUFFER_ACCESS_TOKEN, BUFFER_TIKTOK_PROFILE_ID, BUFFER_INSTAGRAM_PROFILE_ID

## ManyChat API Key
1. Go to manychat.com and sign in
2. Go to Settings → API
3. Copy your API key
4. Paste in .env as MANYCHAT_API_KEY
5. Also save your login email and password for Playwright automation

## Telegram Bot Token
1. Open Telegram, search for @BotFather
2. Send /newbot
3. Follow the prompts to name your bot
4. Copy the token BotFather gives you
5. Paste in .env as TELEGRAM_BOT_TOKEN
6. To get your chat ID: send a message to your bot, then visit https://api.telegram.org/bot[YOUR_TOKEN]/getUpdates and find your chat_id
7. Paste in .env as TELEGRAM_CHAT_ID

---

## fal.ai API Key (Image + Video Generation)
1. Go to fal.ai and sign up
2. Go to Dashboard → Keys
3. Create a new API key
4. Paste in .env as FAL_KEY
5. This single key powers both Nano Banana 2 (images, $0.08/image) and Kling 3.0 (video, $0.084-$0.224/sec)
6. Model IDs: fal-ai/nano-banana-pro (images), fal-ai/kling-video/v3/standard/text-to-video (video), fal-ai/kling-video/v3/pro/image-to-video (pro video)
7. Install client: npm install --save @fal-ai/client (already installed in content-studio/)

## MiniMax API Key (Voice Cloning + TTS)
1. Go to platform.minimax.io and sign up
2. Go to Dashboard → API Keys
3. Create a new API key
4. Paste in .env as MINIMAX_API_KEY
5. To clone your voice: upload 10sec-5min audio via /v1/files/upload (purpose: voice_clone)
6. Then call /v1/voice_clone with the file_id to create your custom voice_id
7. Use your voice_id with the T2A API for automated voiceover generation
8. Model: speech-2.8-hd, Pricing: $50/M chars (HD), $3/voice clone

## ElevenLabs API Key (Voiceover Fallback)
1. Go to elevenlabs.io and sign up
2. Go to Profile → API Keys
3. Copy your API key
4. Paste in .env as ELEVENLABS_API_KEY
5. Free tier: 10,000 chars/month, 3 custom voices
6. Starter ($5/mo): 30,000 chars, 10 custom voices
7. Voice cloning available on all paid plans
