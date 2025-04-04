import { NextResponse } from 'next/server';
import { auth } from '@/app/auth';
import { cookies } from 'next/headers';

export async function POST(request) {
  try {
    // Get the session to access tokens
    const session = await auth();
    
    // Parse the incoming request
    const data = await request.json();
    
    // Get Google access token from the session if not provided in the request
    const googleAccessToken = data.google_access_token || session?.accessToken || null;
    
    // Get spreadsheet ID from request or from cookies
    let spreadsheetId;
    try {
      spreadsheetId = data.spreadsheet_id || cookies().get('spreadsheetId')?.value || null;
    } catch (error) {
      console.error('Error accessing cookies:', error);
      spreadsheetId = data.spreadsheet_id || null;
    }
    
    // Prepare the request to the backend
    const backendRequest = {
      message: data.message,
      conversation_id: data.conversation_id || 'default',
      google_access_token: googleAccessToken,
      spreadsheet_id: spreadsheetId
    };
    
    // Forward the request to the backend
    const backendResponse = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });
    
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
    console.error('Error in agent chat API route:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
} 