# Anime Stream Bot

A Telegram bot to browse and stream anime. Deploys easily to Heroku.

## Features
- `/new` – Browse newest anime (paginated)
- `/search <name>` – Search by title
- Detailed info: language/type, rating, episodes, release date
- Inline episode list & streaming links
- Owner broadcast to support group

## Setup
1. Create a Heroku app.
2. Add config vars: `TELEGRAM_TOKEN`, `OWNER_ID`, `SUPPORT_CHAT`.
3. Push code: `git push heroku main`.
4. `heroku scale worker=1`.

Enjoy!
