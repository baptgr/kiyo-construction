'use client';

import { SessionProvider } from 'next-auth/react';
import { SpreadsheetProvider } from '@/context/SpreadsheetContext';
import { ConversationProvider } from '@/context/ConversationContext';

export function Providers({ children }) {
  return (
    <SessionProvider debug={true}>
      <SpreadsheetProvider>
        <ConversationProvider>
          {children}
        </ConversationProvider>
      </SpreadsheetProvider>
    </SessionProvider>
  );
} 