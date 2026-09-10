export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const guildId = url.searchParams.get("guild_id");

    const redirectTarget = guildId
      ? `${url.origin}/dash.html?guild_id=${encodeURIComponent(guildId)}`
      : `${url.origin}/manage.html`;

    return new Response(null, {
      status: 303,
      headers: { "Location": redirectTarget }
    });
  } catch (err) {
    return new Response(`Bot callback error: ${err.message}`, { status: 500 });
  }
}