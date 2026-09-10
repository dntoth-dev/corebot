export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const response = Response.redirect(`${url.origin}/index.html`, 303);

  // Clear HTTP-only session cookie
  response.headers.append(
    "Set-Cookie",
    "session_id=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax; Secure"
  );
  return response;
}