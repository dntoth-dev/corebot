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
        if not self.url or not self.key:
            raise ValueError("Supabase URL or Key is missing.")
        self.client = await acreate_client(self.url, self.key)