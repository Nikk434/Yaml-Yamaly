import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function PATCH(request) {
  try {
    const body = await request.json();
    const { class_id, status, review_reason } = body;

    if (!class_id || !status) {
      return NextResponse.json(
        { error: 'class_id and status are required' },
        { status: 400 }
      );
    }

    // Get session token from cookies
    const cookieStore = await cookies();
    const sessionToken = cookieStore.get('session_token')?.value;

    if (!sessionToken) {
      return NextResponse.json(
        { error: 'No session token found' },
        { status: 401 }
      );
    }

    const response = await fetch(`${process.env.BACKEND_URL}/api/classes/${class_id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Token': sessionToken,
      },
      body: JSON.stringify({ 
        status,
        review_reason: review_reason || null
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to review class' },
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