import os
import uuid
import requests
from typing import Optional, Dict, Any
from fastapi import FastAPI, Form, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

app = FastAPI(title="Core Security Infrastructure API")

# Setup templates for rendering dashboard and static HTML pages dynamically
templates = Jinja2Templates(directory="templates")

# Static files mounting (CSS, JS, assets if applicable)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration Environment Variables
DISCORD_CLIENT_ID: str = str(os.getenv("DISCORD_CLIENT_ID", ""))
DISCORD_CLIENT_SECRET: str = str(os.getenv("DISCORD_CLIENT_SECRET", ""))
DISCORD_REDIRECT_URI: str = str(os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/api/oauth2/auth/callback"))
DISCORD_BOT_REDIRECT_URI: str = str(os.getenv("DISCORD_BOT_REDIRECT_URI", "http://localhost:8000/api/oauth2/join/callback"))

SUPABASE_URL: str = str(os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY: str = str(os.getenv("SUPABASE_KEY", ""))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# In-Memory Session Store (Mapping session_id -> user session dict)
# In production, persist sessions to Redis or Supabase table
SESSIONS: Dict[str, Dict[str, Any]] = {}


# ========================================================
# SESSION HELPER FUNCTIONS
# ========================================================

def get_session(request: Request) -> Optional[Dict[str, Any]]:
    """Retrieves session data from HTTP-only session_id cookie."""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSIONS:
        return SESSIONS[session_id]
    return None


# ========================================================
# 1. DISCORD OAUTH2 FLOWS (USER LOGIN & BOT INVITE)
# ========================================================

@app.get("/api/oauth2/auth")
def oauth_user_auth():
    """Initiates Discord User OAuth2 login prompt with 'identify' and 'guilds' scopes."""
    discord_auth_url = (
        f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    )
    return RedirectResponse(url=discord_auth_url)


@app.get("/api/oauth2/auth/callback")
def oauth_user_auth_callback(code: str):
    """
    Exchanges OAuth code for access token, fetches user identity and admin guilds,
    sets HTTP-only cookie session, and redirects to manage.html.
    """
    token_url = "https://discord.com/api/v10/oauth2/token"
    payload = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    token_res = requests.post(token_url, data=payload, headers=headers)
    if token_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to authenticate with Discord API."
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    # Fetch User Identity
    user_res = requests.get(
        "https://discord.com/api/v10/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_res.json() if user_res.status_code == 200 else {}

    # Fetch User Guilds
    guilds_res = requests.get(
        "https://discord.com/api/v10/users/@me/guilds",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    all_guilds = guilds_res.json() if guilds_res.status_code == 200 else []

    # Filter guilds where the user has Administrator permissions (0x8)
    admin_guilds = [
        g for g in all_guilds 
        if (int(g.get("permissions", 0)) & 0x8) == 0x8
    ]

    # Create session state
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "user": user_data,
        "access_token": access_token,
        "guilds": admin_guilds
    }

    # Set HTTP-only Cookie and redirect to manage.html
    response = RedirectResponse(url="/manage.html", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    return response


@app.get("/api/oauth2/join")
def oauth_bot_join():
    """Initiates Discord Bot Invite prompt with 'bot' and 'applications.commands' scopes."""
    bot_invite_url = (
        f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}"
        f"&permissions=8&integration_type=0&scope=bot%20applications.commands"
        f"&redirect_uri={DISCORD_BOT_REDIRECT_URI}&response_type=code"
    )
    return RedirectResponse(url=bot_invite_url)


@app.get("/api/oauth2/join/callback")
def oauth_bot_join_callback(guild_id: Optional[str] = None):
    """
    Handles bot join callback and redirects user directly to the dashboard 
    for the server they added the bot to.
    """
    if guild_id:
        return RedirectResponse(url=f"/dash.html?guild_id={guild_id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/manage.html", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/api/auth/logout")
def logout(request: Request):
    """Destroys current session and clears HTTP-only session cookie."""
    session_id = request.cookies.get("session_id")
    if session_id in SESSIONS:
        del SESSIONS[session_id]

    response = RedirectResponse(url="/index.html", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session_id")
    return response


# ========================================================
# 2. FRONTEND PAGE ROUTING & DYNAMIC RENDERING
# ========================================================

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def render_index(request: Request):
    """Renders landing page. Updates 'Get Started' to 'Dashboard' if logged in."""
    session = get_session(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_logged_in": session is not None,
            "user": session.get("user") if session else None
        }
    )


@app.get("/tos.html", response_class=HTMLResponse)
def render_tos(request: Request):
    """Renders Terms of Service page."""
    session = get_session(request)
    return templates.TemplateResponse(
        "tos.html",
        {
            "request": request,
            "is_logged_in": session is not None
        }
    )


@app.get("/privacy-policy.html", response_class=HTMLResponse)
def render_privacy_policy(request: Request):
    """Renders Privacy Policy page."""
    session = get_session(request)
    return templates.TemplateResponse(
        "privacy-policy.html",
        {
            "request": request,
            "is_logged_in": session is not None
        }
    )


@app.get("/manage.html", response_class=HTMLResponse)
def render_manage(request: Request):
    """
    Renders server selection page listing only servers where 
    the logged-in user holds Administrator permissions.
    """
    session = get_session(request)
    if not session:
        return RedirectResponse(url="/api/oauth2/auth", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "manage.html",
        {
            "request": request,
            "user": session.get("user"),
            "guilds": session.get("guilds", [])
        }
    )


@app.get("/dash.html", response_class=HTMLResponse)
def render_dash(request: Request, guild_id: Optional[str] = None):
    """
    Renders server command configuration workspace. Fetches 
    persisted /sentry settings from Supabase database.
    """
    session = get_session(request)
    if not session:
        return RedirectResponse(url="/api/oauth2/auth", status_code=status.HTTP_303_SEE_OTHER)

    # Fallback to first available admin guild if no guild_id specified
    user_guilds = session.get("guilds", [])
    if not guild_id and user_guilds:
        guild_id = user_guilds[0]["id"]
    elif not guild_id:
        guild_id = "TARGET_GUILD_ID"

    # Fetch guild target name
    active_guild = next((g for g in user_guilds if g.get("id") == guild_id), None)
    guild_name = active_guild.get("name", "Target Guild") if active_guild else "Target Guild"

    # Query Supabase database for existing settings
    res = supabase.table("guild_settings").select("*").eq("guild_id", guild_id).execute()
    guild_data = res.data[0] if res.data else {}

    sentry_enabled = guild_data.get("sentry_enabled", True)
    enforcement_action = guild_data.get("enforcement_action", "ban")
    log_channel_id = guild_data.get("log_channel_id", "")

    return templates.TemplateResponse(
        "dash.html",
        {
            "request": request,
            "guild_id": guild_id,
            "guild_name": guild_name,
            "sentry_enabled": sentry_enabled,
            "enforcement_action": enforcement_action,
            "log_channel_id": log_channel_id,
            "user": session.get("user")
        }
    )


# ========================================================
# 3. FORM SUBMISSION ENDPOINT (SUPABASE SYNC)
# ========================================================

@app.post("/api/guild/honeypot/update")
def update_sentry_settings(
    request: Request,
    guild_id: str = Form(...),
    enforcement_action: str = Form(...),
    log_channel_id: Optional[str] = Form(None),
    sentry_enabled: Optional[str] = Form(None)
):
    """
    Handles form POST from /sentry panel on dash.html.
    Persists rule updates in Supabase and redirects back to dashboard.
    """
    session = get_session(request)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired or unauthorized."
        )

    # Form sends "on" when toggle is checked
    is_enabled = sentry_enabled in ["on", "true", "1"]

    config_payload = {
        "guild_id": guild_id,
        "sentry_enabled": is_enabled,
        "enforcement_action": enforcement_action,
        "log_channel_id": log_channel_id or "",
        "updated_at": "now()",
    }

    # Upsert configuration in Supabase
    supabase.table("guild_settings").upsert(config_payload).execute()

    # Redirect back to server dashboard with success status
    return RedirectResponse(
        url=f"/dash.html?guild_id={guild_id}&status=success", 
        status_code=status.HTTP_303_SEE_OTHER
    )