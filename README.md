# Movzies 🍿

Telegram bot for movie and TV-series recommendations.

## Current MVP

- `/start`
- 🎬 Movies
- 📺 TV series
- 🎲 Random recommendation placeholder
- 🔎 Filtered recommendation placeholder
- ❤️ Favorites placeholder
- ✅ Watched list placeholder

## Requirements

- Python 3.13+
- Telegram bot token from BotFather

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
```

Never commit `.env`.

## Run

```cmd
python -m app.bot
```

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

Connect a movie database API, then add persistent favorites, watched titles, dislikes and personalized recommendations.
