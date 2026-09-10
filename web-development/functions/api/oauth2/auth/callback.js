export async function onRequestGet(context) {
  try {
    const { request, env } = context;
    const url = new URL(request.url);
    const code = url.searchParams.get("code");

    if (!code) {
      return new Response("Missing authorization code.", { status: 400 });
    }

    // 1. Exchange OAuth code for Discord Access Token
    const tokenResponse = await fetch("https://discord.com/api/v10/oauth2/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: env.DISCORD_CLIENT_ID,
        client_secret: env.DISCORD_CLIENT_SECRET,
        grant_type: "authorization_code",
        code: code,
        redirect_uri: env.DISCORD_REDIRECT_URI,
      }),
    });

    if (!tokenResponse.ok) {
      const errText = await tokenResponse.text();
      return new Response(`Discord OAuth exchange failed: ${errText}`, { status: 400 });
    }

    const tokenData = await tokenResponse.json();
    const accessToken = tokenData.access_token;

    // 2. Fetch User Profile
    const userResponse = await fetch("https://discord.com/api/v10/users/@me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!userResponse.ok) {
      return new Response("Failed to fetch Discord user profile.", { status: 400 });
    }
    const userData = await userResponse.json();

    // 3. Fetch User Guilds
    const guildsResponse = await fetch("https://discord.com/api/v10/users/@me/guilds", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!guildsResponse.ok) {
      return new Response("Failed to fetch user guilds.", { status: 400 });
    }
    const allGuilds = await guildsResponse.json();

    // Filter for Administrator permissions (bitmask 0x8 using BigInt for safety)
    const adminGuilds = Array.isArray(allGuilds)
      ? allGuilds.filter((g) => (BigInt(g.permissions) & 8n) === 8n)
      : [];

    // 4. Create Session Record in Supabase via REST API
    const sessionId = crypto.randomUUID();

    const supabaseResponse = await fetch(`${env.SUPABASE_URL}/rest/v1/user_sessions`, {
      method: "POST",
      headers: {
        apikey: env.SUPABASE_KEY,
        Authorization: `Bearer ${env.SUPABASE_KEY}`,
        "Content-Type": "application/json",
        Prefer: "resolution=merge-duplicates",
      },
      body: JSON.stringify({
        id: sessionId,
        user_data: userData,
        access_token: accessToken,
        guilds: adminGuilds,
      }),
    });

    if (!supabaseResponse.ok) {
      const dbErr = await supabaseResponse.text();
      return new Response(`Database session creation failed: ${dbErr}`, { status: 500 });
    }

    // 5. Construct direct 303 response with Location and Set-Cookie headers
    return new Response(null, {
      status: 303,
      headers: {
        "Location": `${url.origin}/manage.html`,
        "Set-Cookie": `session_id=${sessionId}; Path=/; HttpOnly; SameSite=Lax; Secure`
      }
    });

  } catch (err) {
    return new Response(`Callback Execution Error: ${err.message}\n${err.stack}`, { status: 500 });
  }
}