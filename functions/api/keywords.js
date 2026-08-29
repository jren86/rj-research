// Cloudflare Pages Function: /api/keywords
// Handles keyword sync between deep-track browser page and automation system.
// Requires KV binding: env.KEYWORD_STORE (see setup instructions below)

export async function onRequest(context) {
  const { request, env } = context;

  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  // GET: return current keyword list
  if (request.method === 'GET') {
    try {
      const raw = await env.KEYWORD_STORE.get('keywords');
      const keywords = raw ? JSON.parse(raw) : [];
      return new Response(JSON.stringify({ keywords }), {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'KV read failed', detail: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }
  }

  // POST: update keyword list
  if (request.method === 'POST') {
    try {
      const body = await request.json();
      if (!body.keywords || !Array.isArray(body.keywords)) {
        return new Response(JSON.stringify({ error: 'invalid body: keywords array required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', ...corsHeaders },
        });
      }

      // Deduplicate and clean
      const cleaned = [...new Set(body.keywords.map(k => k.trim()).filter(Boolean))];

      await env.KEYWORD_STORE.put('keywords', JSON.stringify(cleaned));

      return new Response(JSON.stringify({ ok: true, keywords: cleaned }), {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'KV write failed', detail: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }
  }

  return new Response(JSON.stringify({ error: 'method not allowed' }), {
    status: 405,
    headers: { 'Content-Type': 'application/json', ...corsHeaders },
  });
}
