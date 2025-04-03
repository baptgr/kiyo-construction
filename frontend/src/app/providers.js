'use client';

import { SessionProvider } from 'next-auth/react';

export function Providers({ children }) {
  return (
    <SessionProvider debug={true}>
      {children}
    </SessionProvider>
  );
} 