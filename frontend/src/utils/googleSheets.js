'use client';

/**
 * Creates a new Google Sheet and returns its ID
 * @param {string} accessToken - Google OAuth access token
 * @param {string} title - The title for the new spreadsheet
 * @returns {Promise<string>} - The ID of the created spreadsheet
 */
export async function createSpreadsheet(accessToken, title) {
  try {
    const response = await fetch('https://sheets.googleapis.com/v4/spreadsheets', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
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

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to create spreadsheet');
    }

    const data = await response.json();
    return data.spreadsheetId;
  } catch (error) {
    console.error('Error creating spreadsheet:', error);
    throw error;
  }
}

/**
 * Sets up initial data and formatting in the spreadsheet
 * @param {string} accessToken - Google OAuth access token
 * @param {string} spreadsheetId - The ID of the spreadsheet to update
 */
export async function setupSpreadsheet(accessToken, spreadsheetId) {
  try {
    // Add header row
    await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}:batchUpdate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
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
  } catch (error) {
    console.error('Error setting up spreadsheet:', error);
    throw error;
  }
} 