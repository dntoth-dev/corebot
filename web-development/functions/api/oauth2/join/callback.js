export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const guildId = url.searchParams.get("guild_id");

  if (guildId) {
    return Response.redirect(`${url.origin}/dash.html?guild_id=${guildId}`, 303);
  }
  return Response.redirect(`${url.origin}/manage.html`, 303);
}