import os
import discord
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN environment variable is required.")

DEV_ID = int(os.getenv("DEV_ID") or os.getenv("DEV") or 0)
DEV = os.getenv("DEV")
SHADOW_ID = os.getenv("SHADOW_ID")
SHADOW = os.getenv("SHADOW")

SHADOW_GUILD_ID = int(os.getenv("SHADOWS_COMMUNITY_GUILD_ID") or 0)
GUILD_OBJ = discord.Object(id=SHADOW_GUILD_ID)

# Role IDs (converted to integers for proper role verification checks)
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID") or 0)
SHADOW_ROLE_ID = int(os.getenv("SHADOW_ROLE_ID") or 0)
MODERATOR_ROLE_ID = int(os.getenv("MODERATOR_ROLE_ID") or 0)

YT_API = os.getenv("YOUTUBE_API_KEY")
SM_CH_ID = os.getenv("SM_YT_CHANNEL_ID")

# Global YouTube client instance
youtube = build('youtube', 'v3', developerKey=YT_API) if YT_API else None