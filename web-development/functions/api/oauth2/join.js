export async function onRequestGet(context) {
  const clientId = context.env.DISCORD_CLIENT_ID;
  const redirectUri = encodeURIComponent(context.env.DISCORD_BOT_REDIRECT_URI);

  const inviteUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&permissions=8&integration_type=0&scope=bot%20applications.commands&redirect_uri=${redirectUri}&response_type=code`;

  return Response.redirect(inviteUrl, 302);
}