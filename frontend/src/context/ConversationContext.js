'use client';

import { createContext, useContext, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ConversationContext = createContext();

export function ConversationProvider({ children }) {
  const [conversationId, setConversationId] = useState(null);

  const startNewConversation = () => {
    const newConversationId = uuidv4();
    setConversationId(newConversationId);
    return newConversationId;
  };

  return (
    <ConversationContext.Provider value={{ conversationId, startNewConversation }}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
} 