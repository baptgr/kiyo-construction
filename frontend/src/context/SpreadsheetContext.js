'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';

const SpreadsheetContext = createContext();

export function SpreadsheetProvider({ children }) {
  const { data: session, status } = useSession();
  const [spreadsheetId, setSpreadsheetId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [attempts, setAttempts] = useState(0);

  // Create a spreadsheet when user authenticates
  useEffect(() => {
    const createSheetIfNeeded = async () => {
      // Only create if authenticated and we don't already have a spreadsheet ID
      if (status === 'authenticated' && !spreadsheetId && !isLoading && attempts < 3) {
        setIsLoading(true);
        setError(null);
        setAttempts(prev => prev + 1);
        
        try {
          const response = await fetch('/api/google/create-sheet', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: `Bid Comparison - ${session?.user?.name || 'User'} - ${new Date().toLocaleDateString()}`
            }),
          });
          
          if (!response.ok) {
            let errorData;
            try {
              errorData = await response.json();
            } catch (e) {
              const text = await response.text();
              errorData = { message: `HTTP Error ${response.status}: ${text.substring(0, 100)}` };
            }
            throw new Error(errorData.error || 'Failed to create spreadsheet');
          }
          
          const data = await response.json();
          setSpreadsheetId(data.spreadsheetId);
        } catch (err) {
          setError(err.message || 'Failed to create spreadsheet');
        } finally {
          setIsLoading(false);
        }
      }
    };
    
    createSheetIfNeeded();
  }, [status, session, spreadsheetId, isLoading, attempts]);

  // Clear spreadsheet ID on logout
  useEffect(() => {
    if (status === 'unauthenticated') {
      setSpreadsheetId(null);
      setAttempts(0);
      setError(null);
    }
  }, [status]);

  // Function to manually retry spreadsheet creation
  const retryCreateSpreadsheet = () => {
    if (status === 'authenticated' && !isLoading) {
      setAttempts(0); // Reset attempts
      setError(null);  // Clear any errors
      setSpreadsheetId(null); // Clear existing spreadsheet ID to force new creation
    }
  };

  // Function to create a new spreadsheet
  const createNewSpreadsheet = () => {
    if (status === 'authenticated' && !isLoading) {
      setSpreadsheetId(null); // Clear existing spreadsheet ID
      setAttempts(0); // Reset attempts
      setError(null); // Clear any errors
    }
  };

  // Function to get spreadsheet URL
  const getSpreadsheetUrl = () => {
    if (!spreadsheetId) return null;
    return `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`;
  };

  const value = {
    spreadsheetId,
    setSpreadsheetId,
    isLoading,
    error,
    retryCreateSpreadsheet,
    createNewSpreadsheet,
    getSpreadsheetUrl
  };

  return (
    <SpreadsheetContext.Provider value={value}>
      {children}
    </SpreadsheetContext.Provider>
  );
}

export function useSpreadsheet() {
  const context = useContext(SpreadsheetContext);
  if (context === undefined) {
    throw new Error('useSpreadsheet must be used within a SpreadsheetProvider');
  }
  return context;
} 