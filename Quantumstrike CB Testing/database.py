import os
from supabase import acreate_client, Client
import config


class SupabaseManager:
    def __init__(self):
        self.url: str | None = config.SUPABASE_URL
        self.key: str | None = config.SUPABASE_KEY
        self.client: Client | None = None

    async def initialize(self):
        """Initializes the async Supabase client."""
        self.client = await acreate_client(self.url, self.key)



# Usage:
"""
    async def get_server_settings(self, guild_id: int):
        # Fetches settings for a specific guild.
        response = await self.client.table("server_settings").select("sentry_enabled, sentry_channel_id").eq("guild_id", guild_id).execute()
        # Returns the first matching row or None
        return response.data[0] if response.data else None

    async def update_server_settings(self, guild_id: int, enabled: bool, channel_id: int = None):
        # Upserts settings using Supabase's upsert functionality.
        payload = {
            "guild_id": guild_id,
            "sentry_enabled": enabled
        }
        if channel_id is not None:
            payload["sentry_channel_id"] = channel_id

        # 'upsert' acts as our INSERT ... ON CONFLICT statement
        await self.client.table("server_settings").upsert(payload).execute()
"""