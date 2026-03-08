export async function GET(request) {
  const sessionToken = request.cookies.get('session_token')?.value;

  if (!sessionToken) {
    return new Response(JSON.stringify({ error: 'No session token' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const response = await fetch(`${backendUrl}/classes/export`, {
    method: 'GET',
    headers: {
      'X-Session-Token': sessionToken,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    return new Response(JSON.stringify(error), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const yamlContent = await response.text();

  return new Response(yamlContent, {
    status: 200,
    headers: {
      'Content-Type': 'text/yaml',
      'Content-Disposition': 'attachment; filename=data.yaml',
    },
  });
}