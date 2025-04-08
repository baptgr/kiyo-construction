'use client';

import { useSession } from 'next-auth/react';
import { useSpreadsheet } from '@/context/SpreadsheetContext';

/**
 * Core function to send requests to the agent API
 * @param {string} message - The message to send to the agent
 * @param {Object} options - Additional options
 * @returns {Promise<Response>} - The response object
 */
async function sendAgentRequest(message, options = {}) {
  const {
    googleAccessToken = null,
    spreadsheetId = null,
    isStreaming = false
  } = options;

  const endpoint = isStreaming ? '/api/agent/chat/stream' : '/api/agent/chat';
  
  return fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      google_access_token: googleAccessToken,
      spreadsheet_id: spreadsheetId
    }),
  });
}

/**
 * Send a message to the agent and get a response
 * @param {string} message - The message to send to the agent
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @returns {Promise<Object>} - The agent's response
 */
export async function sendMessageToAgent(message, googleAccessToken = null, spreadsheetId = null) {
  try {
    const response = await sendAgentRequest(message, {
      googleAccessToken,
      spreadsheetId,
      isStreaming: false
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
 * Get a streaming response from the agent
 * @param {string} message - The message to send to the agent
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @returns {Promise<Response>} - The streaming response object
 */
export async function getAgentStreamResponse(message, googleAccessToken = null, spreadsheetId = null) {
  return sendAgentRequest(message, {
    googleAccessToken,
    spreadsheetId,
    isStreaming: true
  });
}

/**
 * Hook to use agent API with current session
 * Automatically includes Google access token from session when available
 */
export function useAgentApi() {
  const { data: session } = useSession();
  const { spreadsheetId } = useSpreadsheet();
  
  const sendMessage = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return sendMessageToAgent(message, googleAccessToken, spreadsheetId);
  };

  const getStreamResponse = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return getAgentStreamResponse(message, googleAccessToken, spreadsheetId);
  };
  
  return {
    sendMessage,
    getStreamResponse,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId
  };
}

/**
 * Hook specifically for streaming responses from the agent
 * Automatically includes Google access token from session when available
 */
export function useAgentStreamApi() {
  const { data: session } = useSession();
  const { spreadsheetId } = useSpreadsheet();
  
  const getStreamResponse = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return getAgentStreamResponse(message, googleAccessToken, spreadsheetId);
  };

  return {
    getStreamResponse,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId
  };
} 