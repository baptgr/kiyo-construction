'use client';

import { SessionProvider } from 'next-auth/react';
import { SpreadsheetProvider } from '@/context/SpreadsheetContext';

export function Providers({ children }) {
  return (
    <SessionProvider debug={true}>
      <SpreadsheetProvider>
        {children}
      </SpreadsheetProvider>
    </SessionProvider>
  );
} 