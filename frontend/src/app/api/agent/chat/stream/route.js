import { auth } from '@/app/auth';

export async function POST(request) {
  try {
    // Get the session to access tokens
    const session = await auth();
    
    // Parse the incoming request
    const data = await request.json();
    
    // Get Google access token from the session if not provided in the request
    const googleAccessToken = data.google_access_token || session?.accessToken || null;
    
    // Prepare the request to the backend
    const backendRequest = {
      message: data.message,
      conversation_id: data.conversation_id || 'default',
      google_access_token: googleAccessToken
    };
    
    // Forward the request to the backend streaming endpoint
    const backendResponse = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/api/chat/stream/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });
    
    return new Response(backendResponse.body, {
      status: backendResponse.status,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    });
    
  } catch (error) {
    console.error('Error in agent stream API route:', error);
    
    // Return error as SSE
    return new Response(
      `event: error\ndata: ${JSON.stringify({ error: error.message || 'Internal server error' })}\n\n`,
      {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        }
      }
    );
  }
} 