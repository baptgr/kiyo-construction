import { NextResponse } from 'next/server';
import { auth } from '@/app/auth';

export async function POST(request) {
  try {
    // Get the session to access tokens
    const session = await auth();
    
    // Parse the incoming request
    const data = await request.json();
    
    if (!data.conversation_id) {
      return NextResponse.json(
        { error: 'conversation_id is required' },
        { status: 400 }
      );
    }
    
    // Forward the request to the backend
    const backendResponse = await fetch(
      `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/conversation/delete`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: data.conversation_id
        }),
      }
    );
    
    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { error: errorData.error || `Backend error: ${backendResponse.status}` },
        { status: backendResponse.status }
      );
    }
    
    // Return the response from the backend
    const responseData = await backendResponse.json();
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('Error in conversation delete API route:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
} 