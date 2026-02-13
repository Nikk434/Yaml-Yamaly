import { NextResponse } from 'next/server';

export async function GET(request) {
  try {
    console.log("URL 1 =",request.url);
    
    const { searchParams } = new URL(request.url);
    const room_code = searchParams.get('room_code');
    const session_token = searchParams.get('session_token');

    if (!room_code || !session_token) {
      return NextResponse.json(
        { error: 'Missing room_code or session_token' },
        { status: 400 }
      );
    }

    const url = new URL(`${process.env.BACKEND_URL}/api/sessions/count`);
    url.searchParams.set('room_code', room_code);
    url.searchParams.set('session_token', session_token);
    console.log("++URL++",url);
    
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to fetch session info' },
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