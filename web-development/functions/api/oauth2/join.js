export async function onRequestGet(context) {
    try {
        const { env } = context;

        if (!env.DISCORD_CLIENT_ID || !env.DISCORD_BOT_REDIRECT_URI) {
            return new Response("Server configuration error: Missing environment variables", { status: 500 });
        }

        const clientId = env.DISCORD_CLIENT_ID;
        const redirectUri = encodeURIComponent(env.DISCORD_BOT_REDIRECT_URI);
        const inviteUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&permissions=8&integration_type=0&scope=bot%20applications.commands&redirect_uri=${redirectUri}&response_type=code`;

        return new Response(null, {
            status: 302,
            headers: { "Location": inviteUrl }
        });
    } catch (err) {
        return new Response(`Join Redirect Error: ${err.message}`, { status: 500 });
    }
}