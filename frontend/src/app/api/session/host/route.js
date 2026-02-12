import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const { room_code, owner_secret } = body;

    const params = new URLSearchParams({
      room_code: room_code,
      owner_secret: owner_secret
    });

    const url = `${process.env.BACKEND_URL}/api/sessions/host?${params.toString()}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to create host session' },
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