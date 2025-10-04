import discord
from discord.ext import commands, tasks
import aiohttp
import os
from dotenv import load_dotenv

# Load .env if exists (local dev), Railway uses environment variables
load_dotenv()

# ---- CONFIG ----
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
PLAYER_PROFILE_IDS = os.getenv("PLAYER_PROFILE_IDS", "")
PLAYER_PROFILE_IDS = [p.strip() for p in PLAYER_PROFILE_IDS.split(",") if p.strip()]

if not DISCORD_TOKEN or not PLAYER_PROFILE_IDS or not DISCORD_CHANNEL_ID:
    raise ValueError("Missing required environment variables!")

AOE4_API_TEMPLATE = "https://aoe4world.com/api/v0/players/{}/games?limit=1"

# ---- BOT SETUP ----
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store last match per player
last_seen_matches = {}  # {profile_id: last_match_id}


async def fetch_latest_match(profile_id):
    url = AOE4_API_TEMPLATE.format(profile_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("games"):
                    return data["games"][0]  # latest match
    return None


def format_match_info(match):
    match_id = match.get("game_id")
    map_name = match.get("map", "Unknown")
    started = match.get("started_at")
    teams = match.get("teams", [])

    def player_str(p):
        return f"**{p['name']}** (ELO: {p.get('rating','N/A')}, Result: {p.get('result','N/A')})"

    team_texts = []
    for idx, team in enumerate(teams, start=1):
        players = [player_str(p["player"]) for p in team]
        team_texts.append(f"**Team {idx}:**\n" + "\n".join(players))

    return (
        f"🛡 **New Match Detected!**\n"
        f"Map: {map_name}\n"
        f"Start Time: {started}\n\n"
        + "\n\n".join(team_texts)
        + f"\n\nMatch ID: `{match_id}`"
    )


@tasks.loop(minutes=2)
async def check_matches():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        return

    for profile_id in PLAYER_PROFILE_IDS:
        try:
            match = await fetch_latest_match(profile_id)
            if match:
                match_id = match["game_id"]

                # Only post if this match is not in any player's last_seen
                if match_id not in last_seen_matches.values():
                    await channel.send(format_match_info(match))

                # Always update this player's last_seen match
                last_seen_matches[profile_id] = match_id

        except Exception as e:
            print(f"Error fetching match for profile {profile_id}: {e}")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_matches.start()


bot.run(DISCORD_TOKEN)
