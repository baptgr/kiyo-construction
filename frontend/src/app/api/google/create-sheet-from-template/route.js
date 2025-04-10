import { auth } from '@/app/auth';
import { NextResponse } from 'next/server';

export async function POST(request) {
  // 1. Check authentication and get access token
  const session = await auth();
  if (!session || !session.accessToken) {
    return NextResponse.json(
      { error: "Authentication required. Please sign in again." },
      { status: 401 }
    );
  }

  try {
    const accessToken = session.accessToken;
    
    // 2. Parse the incoming request for the file
    const formData = await request.formData();
    const file = formData.get('templateFile');

    if (!file) {
      return NextResponse.json({ error: "No template file provided." }, { status: 400 });
    }

    if (file.type !== 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
      return NextResponse.json({ error: "Invalid file type. Please upload an XLSX file." }, { status: 400 });
    }

    // 3. Upload the XLSX file to Google Drive
    const fileMetadata = {
      name: file.name,
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    };

    const driveFormData = new FormData();
    driveFormData.append('metadata', new Blob([JSON.stringify(fileMetadata)], { type: 'application/json' }));
    driveFormData.append('file', file);

    const uploadResponse = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: driveFormData,
    });

    if (!uploadResponse.ok) {
      const errorData = await uploadResponse.json();
      console.error("Drive upload error:", errorData);
      return NextResponse.json(
        { error: `Failed to upload template to Google Drive: ${errorData.error?.message || 'Unknown error'}` },
        { status: uploadResponse.status }
      );
    }

    const uploadedFileData = await uploadResponse.json();
    const uploadedFileId = uploadedFileData.id;

    // 4. Convert the uploaded XLSX to a Google Sheet by copying
    const copyResponse = await fetch(`https://www.googleapis.com/drive/v3/files/${uploadedFileId}/copy`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mimeType: 'application/vnd.google-apps.spreadsheet',
        name: `Sheet from ${file.name}` // You can customize the new sheet's name here
      })
    });

    if (!copyResponse.ok) {
      const errorData = await copyResponse.json();
      console.error("Drive copy/convert error:", errorData);
      // Optional: Clean up the initially uploaded XLSX file if conversion fails
      await fetch(`https://www.googleapis.com/drive/v3/files/${uploadedFileId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      return NextResponse.json(
        { error: `Failed to convert template to Google Sheet: ${errorData.error?.message || 'Unknown error'}` },
        { status: copyResponse.status }
      );
    }

    const newSheetData = await copyResponse.json();
    const newSheetId = newSheetData.id;

    // Optional: Clean up the initially uploaded XLSX file after successful conversion
    await fetch(`https://www.googleapis.com/drive/v3/files/${uploadedFileId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    // 5. Return the ID of the newly created Google Sheet
    return NextResponse.json({ spreadsheetId: newSheetId });

  } catch (error) {
    console.error("Create sheet from template error:", error);
    return NextResponse.json(
      { error: error.message || "An internal server error occurred." },
      { status: 500 }
    );
  }
} 