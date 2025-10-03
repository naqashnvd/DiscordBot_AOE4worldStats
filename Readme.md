# AOE4 Discord Bot (Railway Deployment)

This bot checks [AOE4World](https://aoe4world.com/) for your latest matches and posts updates with opponents' Elo and ranks in a Discord channel.

## 🚀 Setup & Deploy on Railway
1. Fork or clone this repo.
2. Push it to your GitHub.
3. On [Railway](https://railway.app/), create a new project → Deploy from GitHub.
4. Railway will detect `railway.json` and run the bot as a **Worker**.
5. Set Environment Variables in Railway:
   - `DISCORD_TOKEN` = your Discord bot token
   - `DISCORD_CHANNEL_ID` = channel ID where the bot should post
   - `PLAYER_PROFILE_ID` = your aoe4world profile id (e.g. `1234567:user1,1234567:user2`)

The bot will check AOE4World every 2 minutes for new matches and post details in your channel.


