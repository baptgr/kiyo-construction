import { auth } from '@/app/auth';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server'; // Import NextResponse for cleaner error responses

export async function POST(request) {
  let payload;
  let contentType = request.headers.get('content-type');
  let conversationId = 'default';
  let googleAccessToken;
  let spreadsheetId;
  let bodyToSend;
  let headersToSend = {};

  try {
    // Get the session to potentially retrieve the access token later
    const session = await auth();
    googleAccessToken = session?.accessToken || null;

    // --- Determine request type and parse payload --- 
    if (contentType?.includes('application/json')) {
      const data = await request.json();
      payload = data.message;
      googleAccessToken = data.google_access_token || googleAccessToken;
      spreadsheetId = data.spreadsheet_id || cookies().get('spreadsheetId')?.value || null;
      conversationId = data.conversation_id || conversationId;
      
      // Prepare JSON body for backend
      bodyToSend = JSON.stringify({
        message: payload,
        google_access_token: googleAccessToken,
        spreadsheet_id: spreadsheetId,
        conversation_id: conversationId
      });
      headersToSend['Content-Type'] = 'application/json';
      
    } else if (contentType?.includes('multipart/form-data')) {
      const formData = await request.formData();
      payload = formData; // Keep as FormData
      // Extract other fields from FormData, falling back to session/cookies if needed
      googleAccessToken = formData.get('google_access_token') || googleAccessToken;
      spreadsheetId = formData.get('spreadsheet_id') || cookies().get('spreadsheetId')?.value || null;
      conversationId = formData.get('conversation_id') || conversationId;

      // Append potentially missing context data back to FormData
      if (googleAccessToken && !formData.has('google_access_token')) formData.append('google_access_token', googleAccessToken);
      if (spreadsheetId && !formData.has('spreadsheet_id')) formData.append('spreadsheet_id', spreadsheetId);
      if (conversationId && !formData.has('conversation_id')) formData.append('conversation_id', conversationId);

      // Prepare FormData body for backend (NO Content-Type header)
      bodyToSend = formData;

    } else {
      console.error('Unsupported Content-Type:', contentType);
      return new Response(
        `event: error\ndata: ${JSON.stringify({ error: 'Unsupported request format' })}\n\n`,
        { status: 415, headers: { 'Content-Type': 'text/event-stream' } }
      );
    }

    // --- Forward the request to the backend streaming endpoint --- 
    const backendUrl = `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/chat/stream/`;
    console.log(`Forwarding request to backend: ${backendUrl}`); // Add logging
    
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: headersToSend, // Send appropriate headers
      body: bodyToSend,       // Send appropriate body (JSON string or FormData)
      // Important for Node.js fetch streaming duplex
      // @ts-ignore
      duplex: 'half' 
    });

    // --- Stream the backend response back to the client --- 
    if (!backendResponse.ok) {
       const errorText = await backendResponse.text();
       console.error(`Backend error: ${backendResponse.status}`, errorText);
       throw new Error(`Backend request failed with status ${backendResponse.status}`);
    }
    
    return new Response(backendResponse.body, {
      status: backendResponse.status,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        // Optionally copy other relevant headers from backendResponse.headers if needed
      }
    });
    
  } catch (error) {
    console.error('Error in agent stream API route:', error);
    
    // Return error as SSE using NextResponse for cleaner JSON error payload
    const errorPayload = JSON.stringify({ error: error.message || 'Internal server error' });
    return new Response(
      `event: error\ndata: ${errorPayload}\n\n`,
      {
        status: 500,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        }
      }
    );
  }
} 