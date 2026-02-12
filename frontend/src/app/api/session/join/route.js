import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const { room_code } = body;

    const params = new URLSearchParams({
      room_code: room_code
    });

    const url = `${process.env.BACKEND_URL}/api/sessions/join?${params.toString()}`;

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