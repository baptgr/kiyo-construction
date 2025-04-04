'use client';

import { useSession } from 'next-auth/react';
import { useSpreadsheet } from '@/context/SpreadsheetContext';

/**
 * Send a message to the agent and get a response
 * @param {string} message - The message to send to the agent
 * @param {string} conversationId - Optional conversation ID for context
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @returns {Promise<Object>} - The agent's response
 */
export async function sendMessageToAgent(message, conversationId = 'default', googleAccessToken = null, spreadsheetId = null) {
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
        spreadsheet_id: spreadsheetId
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
  const { spreadsheetId } = useSpreadsheet();
  
  const sendMessage = async (message, conversationId = 'default') => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return sendMessageToAgent(message, conversationId, googleAccessToken, spreadsheetId);
  };
  
  return {
    sendMessage,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId
  };
}

/**
 * Send a streaming message request to the agent API
 * This uses fetch's streaming capability instead of EventSource
 * @param {string} message - The message to send to the agent
 * @param {string} conversationId - Optional conversation ID for context
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @returns {Promise<Response>} - The streaming response object
 */
export async function getAgentStreamResponse(message, conversationId = 'default', googleAccessToken = null, spreadsheetId = null) {
  return fetch('/api/agent/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      google_access_token: googleAccessToken,
      spreadsheet_id: spreadsheetId
    }),
  });
}

/**
 * Hook to use agent streaming capabilities with current session
 */
export function useAgentStreamApi() {
  const { data: session } = useSession();
  const { spreadsheetId } = useSpreadsheet();
  
  const getStreamResponse = async (message, conversationId = 'default') => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return getAgentStreamResponse(message, conversationId, googleAccessToken, spreadsheetId);
  };
  
  return {
    getStreamResponse,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId
  };
} 