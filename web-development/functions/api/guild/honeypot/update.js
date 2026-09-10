export async function onRequestPost(context) {
  const { request, env } = context;
  const formData = await request.formData();

  const guildId = formData.get("guild_id");
  const enforcementAction = formData.get("enforcement_action");
  const logChannelId = formData.get("log_channel_id") || "";
  const sentryEnabled = formData.get("sentry_enabled") === "on";

  // Upsert guild settings directly into Supabase
  await fetch(`${env.SUPABASE_URL}/rest/v1/guild_settings`, {
    method: "POST",
    headers: {
      apikey: env.SUPABASE_KEY,
      Authorization: `Bearer ${env.SUPABASE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "resolution=merge-duplicates",
    },
    body: JSON.stringify({
      guild_id: guildId,
      sentry_enabled: sentryEnabled,
      enforcement_action: enforcementAction,
      log_channel_id: logChannelId,
      updated_at: new Date().toISOString(),
    }),
  });

  const url = new URL(request.url);
  return Response.redirect(`${url.origin}/dash.html?guild_id=${guildId}&status=success`, 303);
}