export async function onRequestGet(context) {
    try {
        const { env } = context;

        if (!env.DISCORD_CLIENT_ID || !env.DISCORD_REDIRECT_URI) {
            return new Response("Server configuration error: Missing environment variables", { status: 500 });
        }

        const clientId = env.DISCORD_CLIENT_ID;
        const redirectUri = encodeURIComponent(env.DISCORD_REDIRECT_URI);
        const authUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=identify%20guilds`;

        return new Response(null, {
            status: 302,
            headers: { "Location": authUrl }
        });
    } catch (err) {
        return new Response(`Auth Redirect Error: ${err.message}`, { status: 500 });
    }
}