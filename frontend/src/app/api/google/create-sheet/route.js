import { auth } from '@/app/auth';
import { NextResponse } from 'next/server';

export async function POST(request) {
  // Check authentication
  const session = await auth();
  
  if (!session || !session.accessToken) {
    return NextResponse.json(
      { error: "Authentication required" },
      { status: 401 }
    );
  }

  try {
    const body = await request.json();
    const { title } = body;
    
    // Create a new spreadsheet
    const sheetResponse = await fetch('https://sheets.googleapis.com/v4/spreadsheets', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        properties: {
          title: title || `Bid Leveling - ${new Date().toLocaleDateString()}`
        },
        sheets: [
          {
            properties: {
              title: 'Bid Comparison',
              gridProperties: {
                rowCount: 50,
                columnCount: 20
              }
            }
          }
        ]
      })
    });
    
    if (!sheetResponse.ok) {
      const errorText = await sheetResponse.text();
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        errorData = { rawText: errorText };
      }
      
      return NextResponse.json(
        { error: errorData.error?.message || "Failed to create spreadsheet" },
        { status: sheetResponse.status }
      );
    }

    const data = await sheetResponse.json();
    const spreadsheetId = data.spreadsheetId;
    
    // Set up initial data (header row)
    const setupResponse = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}:batchUpdate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        requests: [
          {
            updateCells: {
              rows: [
                {
                  values: [
                    { userEnteredValue: { stringValue: 'Item' } },
                    { userEnteredValue: { stringValue: 'Description' } },
                    { userEnteredValue: { stringValue: 'Quantity' } },
                    { userEnteredValue: { stringValue: 'Unit' } },
                    { userEnteredValue: { stringValue: 'Bidder 1' } },
                    { userEnteredValue: { stringValue: 'Bidder 2' } },
                    { userEnteredValue: { stringValue: 'Bidder 3' } },
                    { userEnteredValue: { stringValue: 'Notes' } }
                  ]
                }
              ],
              fields: 'userEnteredValue',
              start: { sheetId: 0, rowIndex: 0, columnIndex: 0 }
            }
          },
          {
            updateSheetProperties: {
              properties: {
                sheetId: 0,
                gridProperties: {
                  frozenRowCount: 1
                }
              },
              fields: 'gridProperties.frozenRowCount'
            }
          }
        ]
      })
    });

    // Return successful response with spreadsheet ID
    return NextResponse.json({ spreadsheetId });
    
  } catch (error) {
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
} 