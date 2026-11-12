import os
from urllib.parse import urlencode
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

app = FastAPI(title="Core Bot API")

# Setup CORS to allow requests from your Cloudflare Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://core-bot.pages.dev", # rmk: change url to always match
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
SUPABASE_URL: str = str(os.getenv("SUPABASE_URL")) # TODO: Place SUPABASE URL in .env on CFP host.
SUPABASE_KEY: str = str(os.getenv("SUPABASE_KEY")) # TODO: Place SUPABASE KEY in .env on CFP host.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://core-bot.pages.dev")


@app.post("/api/guild/sentry/update")
async def update_sentry_settings(
    guild_id: str = Form(...),
    sentry_enabled: str = Form(None),
    enforcement_action: str = Form(...),
    log_channel_id: str = Form(None)
):
    # Standardize checkbox value to boolean
    is_enabled = (sentry_enabled == "on")

    # Clean channel ID string
    clean_channel_id = log_channel_id.strip() if log_channel_id else ""

    try:
        # Upsert configuration into the Supabase 'guild_configs' table
        payload = {
            "guild_id": guild_id,
            "sentry_enabled": is_enabled,
            "enforcement_action": enforcement_action,
            "log_channel_id": clean_channel_id,
        }

        # Perform database upsert (Insert or Update if guild_id matches primary key)
        supabase.table("guild_configs").upsert(payload).execute() # TODO: Assign / Create real Supabase table. [Maybe different tables for different modules, e.g. sentry, moderate, etc.]

        # Build query parameters to pass current state back to static HTML
        query_params = urlencode({
            "guild_id": guild_id,
            "sentry_enabled": True if is_enabled else False,
            "enforcement_action": enforcement_action,
            "log_channel_id": clean_channel_id,
            "updated": "true"
        })

        # Redirect user back to Cloudflare Pages dashboard
        return RedirectResponse(
            url=f"{FRONTEND_URL}/dashboard.html?{query_params}",
            status_code=303
        )

    except Exception as e:
        print(f"Database update failed: {e}")
        
        # Build query parameters with error status
        query_params = urlencode({
            "guild_id": guild_id,
            "error": "true"
        })

        return RedirectResponse(
            url=f"{FRONTEND_URL}/dashboard.html?{query_params}",
            status_code=303
        )