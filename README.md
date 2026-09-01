# Movzies 🍿

Telegram bot for movie and TV-series recommendations.

## Current MVP

- `/start`
- 🎬 Movies
- 📺 TV series
- 🎲 Real random movie recommendations from TMDB
- 🎲 Real random TV-series recommendations from TMDB
- Poster, title, year, genres, TMDB rating and synopsis
- 🔎 Filtered recommendation placeholder
- ❤️ Favorites placeholder
- ✅ Watched list placeholder

## Requirements

- Python 3.13+
- Telegram bot token from BotFather
- TMDB API Read Access Token

## Setup

```bash
python -m venv .venv
```

Windows CMD:

```cmd
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a local `.env` file based on `.env.example`:

```env
BOT_TOKEN=your_real_bot_token
TMDB_ACCESS_TOKEN=your_tmdb_api_read_access_token
```

Never commit `.env`.

## TMDB setup

1. Create/sign in to a TMDB account.
2. Open Account Settings → API.
3. Request API access if needed.
4. Copy the **API Read Access Token**.
5. Paste it into `TMDB_ACCESS_TOKEN` in your local `.env` file.

The bot uses TMDB's Bearer-token authentication and the `/discover/movie`, `/discover/tv`, and genre endpoints.

## Run

```cmd
python -m app.bot
```

If `TMDB_ACCESS_TOKEN` is missing, the bot will still start but real recommendations will be disabled.

## Working from another laptop

Before starting work:

```cmd
git pull
```

After making changes:

```cmd
git add .
git commit -m "describe your changes"
git push
```

Do not run the same polling bot token simultaneously on two computers.

## Next

Add recommendation filters, persistent favorites, watched titles, dislikes and personalized recommendations.
