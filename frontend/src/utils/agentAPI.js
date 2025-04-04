'use client';

import { useSession } from 'next-auth/react';

/**
 * Send a message to the agent and get a response
 * @param {string} message - The message to send to the agent
 * @param {string} conversationId - Optional conversation ID for context
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @returns {Promise<Object>} - The agent's response
 */
export async function sendMessageToAgent(message, conversationId = 'default', googleAccessToken = null) {
  try {
    const response = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        google_access_token: googleAccessToken,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error sending message to agent:', error);
    throw error;
  }
}

/**
 * Hook to use agent API with current session
 * Automatically includes Google access token from session when available
 */
export function useAgentApi() {
  const { data: session } = useSession();
  
  const sendMessage = async (message, conversationId = 'default') => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return sendMessageToAgent(message, conversationId, googleAccessToken);
  };
  
  return {
    sendMessage,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
  };
}

/**
 * Create an event source for streaming responses from the agent
 * @param {string} message - The message to send to the agent
 * @param {string} conversationId - Optional conversation ID for context
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @returns {EventSource} - The event source for streaming responses
 */
export function createAgentStreamSource(message, conversationId = 'default', googleAccessToken = null) {
  // Create the URL with query parameters
  const url = '/api/agent/stream';
  
  // Create the event source
  const eventSource = new EventSource(url);
  
  // Send the message as a POST request
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      google_access_token: googleAccessToken,
    }),
  }).catch(error => {
    console.error('Error initiating stream:', error);
    eventSource.close();
  });
  
  return eventSource;
}

/**
 * Hook to use agent streaming API with current session
 * Automatically includes Google access token from session when available
 */
export function useAgentStreamApi() {
  const { data: session } = useSession();
  
  const createStreamSource = (message, conversationId = 'default') => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return createAgentStreamSource(message, conversationId, googleAccessToken);
  };
  
  return {
    createStreamSource,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
  };
} 