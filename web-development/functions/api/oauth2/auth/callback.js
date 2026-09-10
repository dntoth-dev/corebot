export async function onRequestGet(context) {
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
    return new Response("Failed to authenticate with Discord API.", { status: 400 });
  }

  const tokenData = await tokenResponse.json();
  const accessToken = tokenData.access_token;

  // 2. Fetch User Profile
  const userResponse = await fetch("https://discord.com/api/v10/users/@me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const userData = await userResponse.json();

  // 3. Fetch User Guilds
  const guildsResponse = await fetch("https://discord.com/api/v10/users/@me/guilds", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const allGuilds = await guildsResponse.json();

  // Filter for Administrator permissions (bitmask 0x8)
  const adminGuilds = Array.isArray(allGuilds)
    ? allGuilds.filter((g) => (parseInt(g.permissions) & 0x8) === 0x8)
    : [];

  // 4. Create Session Record in Supabase via REST API
  const sessionId = crypto.randomUUID();

  await fetch(`${env.SUPABASE_URL}/rest/v1/user_sessions`, {
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

  // Set HTTP-only Cookie and redirect to server selection
  const response = Response.redirect(`${url.origin}/manage.html`, 303);
  response.headers.append(
    "Set-Cookie",
    `session_id=${sessionId}; Path=/; HttpOnly; SameSite=Lax; Secure`
  );
  return response;
}