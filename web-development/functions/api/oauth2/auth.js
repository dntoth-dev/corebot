export async function onRequestGet(context) {
    const clientId = context.env.DISCORD_CLIENT_ID;
    const redirectUri = encodeURIComponent(context.env.DISCORD_REDIRECT_URI);

    const authUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=identify%20guilds`;
}