import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request) {
  try {
    const body = await request.json();
    const { room_code } = body;

    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session_token')?.value;

    const params = new URLSearchParams({
      room_code: room_code,
    });

    if (sessionToken) {
      params.append('session_token', sessionToken);
    }

    const url = `${process.env.BACKEND_URL}/api/sessions/join?${params.toString()}`;
    console.log("SESHSHSHSHSHSSHSH = ",url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to join room' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: 200 });

  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
