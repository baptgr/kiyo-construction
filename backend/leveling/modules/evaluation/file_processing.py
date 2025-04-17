from typing import Optional
import os
import requests

def get_or_create_folder(google_access_token: str, folder_name: str, parent_id: str = None) -> str:
    """
    Get or create a folder in Google Drive.
    
    Args:
        google_access_token: Google OAuth access token
        folder_name: Name of the folder to create/find
        parent_id: ID of the parent folder (optional)
        
    Returns:
        The ID of the folder
    """
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    search_response = requests.get(
        'https://www.googleapis.com/drive/v3/files',
        headers={'Authorization': f'Bearer {google_access_token}'},
        params={'q': query}
    )
    
    if search_response.ok:
        folders = search_response.json().get('files', [])
        if folders:
            return folders[0]['id']
    
    # Create new folder if not found
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]
    
    create_response = requests.post(
        'https://www.googleapis.com/drive/v3/files',
        headers={
            'Authorization': f'Bearer {google_access_token}',
            'Content-Type': 'application/json'
        },
        json=folder_metadata
    )
    
    if not create_response.ok:
        print(f"Failed to create folder: {create_response.text}")
        return None
        
    return create_response.json()['id']

def create_sheet_from_template(template_path: str, google_access_token: str, run_id: str) -> Optional[str]:
    """
    Creates a Google Sheet from an Excel template file in the evaluation/run folder structure.
    
    Args:
        template_path: Path to the Excel template file
        google_access_token: Google OAuth access token
        run_id: Unique identifier for this evaluation run
        
    Returns:
        The ID of the created Google Sheet, or None if creation failed
    """
    try:
        # 1. Create/get evaluation folder
        evaluation_folder_id = get_or_create_folder(google_access_token, "evaluation")
        if not evaluation_folder_id:
            print("Failed to create/get evaluation folder")
            return None
            
        # 2. Create/get run folder
        run_folder_id = get_or_create_folder(google_access_token, run_id, evaluation_folder_id)
        if not run_folder_id:
            print("Failed to create/get run folder")
            return None
        
        # 3. Upload the XLSX file to Google Drive
        file_name = os.path.basename(template_path)
        
        # Prepare the file metadata
        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'parents': [run_folder_id]
        }
        
        # Prepare the multipart request
        files = {
            'metadata': ('metadata', str(file_metadata), 'application/json'),
            'file': (file_name, open(template_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        # Upload the file
        upload_response = requests.post(
            'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
            headers={'Authorization': f'Bearer {google_access_token}'},
            files=files
        )
        
        if not upload_response.ok:
            print(f"Failed to upload template to Google Drive: {upload_response.text}")
            return None
            
        uploaded_file_id = upload_response.json()['id']
        
        # 4. Convert the uploaded XLSX to a Google Sheet by copying
        copy_response = requests.post(
            f'https://www.googleapis.com/drive/v3/files/{uploaded_file_id}/copy',
            headers={
                'Authorization': f'Bearer {google_access_token}',
                'Content-Type': 'application/json'
            },
            json={
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'name': f'Sheet from {file_name}',
                'parents': [run_folder_id]
            }
        )
        
        if not copy_response.ok:
            print(f"Failed to convert template to Google Sheet: {copy_response.text}")
            # Clean up the uploaded file
            requests.delete(
                f'https://www.googleapis.com/drive/v3/files/{uploaded_file_id}',
                headers={'Authorization': f'Bearer {google_access_token}'}
            )
            return None
            
        new_sheet_id = copy_response.json()['id']
        
        # 5. Clean up the uploaded XLSX file
        requests.delete(
            f'https://www.googleapis.com/drive/v3/files/{uploaded_file_id}',
            headers={'Authorization': f'Bearer {google_access_token}'}
        )
        
        return new_sheet_id
        
    except Exception as e:
        print(f"Error creating sheet from template: {str(e)}")
        return None

