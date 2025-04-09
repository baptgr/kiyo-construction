'use client';

import { useSession } from 'next-auth/react';
import { useSpreadsheet } from '@/context/SpreadsheetContext';
import { useConversation } from '@/context/ConversationContext';

/**
 * Core function to send requests to the agent API
 * @param {string | FormData} payload - The message string or FormData to send to the agent
 * @param {Object} options - Additional options
 * @returns {Promise<Response>} - The response object
 */
async function sendAgentRequest(payload, options = {}) {
  const {
    googleAccessToken = null,
    spreadsheetId = null,
    conversationId = null,
    isStreaming = false
  } = options;

  const endpoint = isStreaming ? '/api/agent/chat/stream/' : '/api/agent/chat/';
  
  let headers = {};
  let body;

  if (payload instanceof FormData) {
    // Append context data to FormData
    if (googleAccessToken) payload.append('google_access_token', googleAccessToken);
    if (spreadsheetId) payload.append('spreadsheet_id', spreadsheetId);
    if (conversationId) payload.append('conversation_id', conversationId);
    
    // Don't set Content-Type, browser will set it with boundary for FormData
    body = payload;
  } else if (typeof payload === 'string') {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify({
      message: payload,
      google_access_token: googleAccessToken,
      spreadsheet_id: spreadsheetId,
      conversation_id: conversationId
    });
  } else {
      console.error("sendAgentRequest: Invalid payload type", typeof payload);
      // You might want to return a rejected Promise or throw an error here
      return Promise.reject(new Error("Invalid payload type"));
  }

  return fetch(endpoint, {
    method: 'POST',
    headers: headers,
    body: body,
  });
}

/**
 * Send a message to the agent and get a response
 * @param {string} message - The message to send to the agent
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @param {string} conversationId - Optional conversation ID to use for the task
 * @returns {Promise<Object>} - The agent's response
 */
export async function sendMessageToAgent(message, googleAccessToken = null, spreadsheetId = null, conversationId = null) {
  try {
    const response = await sendAgentRequest(message, {
      googleAccessToken,
      spreadsheetId,
      conversationId,
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
 * @param {string | FormData} messagePayload - The message string or FormData to send
 * @param {string} googleAccessToken - Optional Google access token for Sheets access
 * @param {string} spreadsheetId - Optional spreadsheet ID to use for the task
 * @param {string} conversationId - Optional conversation ID to use for the task
 * @returns {Promise<Response>} - The streaming response object
 */
export async function getAgentStreamResponse(messagePayload, googleAccessToken = null, spreadsheetId = null, conversationId = null) {
  return sendAgentRequest(messagePayload, {
    googleAccessToken,
    spreadsheetId,
    conversationId,
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
  const { currentConversationId, startNewConversation } = useConversation();
  
  const sendMessage = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return sendMessageToAgent(
      message, 
      googleAccessToken, 
      spreadsheetId,
      currentConversationId
    );
  };

  const getStreamResponse = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return getAgentStreamResponse(
      message, 
      googleAccessToken, 
      spreadsheetId,
      currentConversationId
    );
  };
  
  return {
    sendMessage,
    getStreamResponse,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId,
    currentConversationId,
    startNewConversation
  };
}

/**
 * Hook specifically for streaming responses from the agent
 * Automatically includes Google access token from session when available
 */
export function useAgentStreamApi() {
  const { data: session } = useSession();
  const { spreadsheetId } = useSpreadsheet();
  const { currentConversationId, startNewConversation } = useConversation();
  
  const getStreamResponse = async (message) => {
    // Extract Google access token from session if available
    const googleAccessToken = session?.accessToken || null;
    
    return getAgentStreamResponse(
      message, 
      googleAccessToken, 
      spreadsheetId,
      currentConversationId
    );
  };

  return {
    getStreamResponse,
    isAuthenticated: !!session,
    googleAccessToken: session?.accessToken,
    spreadsheetId,
    currentConversationId,
    startNewConversation
  };
} 