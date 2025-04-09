# PDF Chat Attachment Design

This document outlines the target solution for allowing users to attach PDF files within the chat interface.

## Target Solution

### User Experience (Frontend)

1.  **Attachment UI:** A "paperclip" icon will be added to the chat input area.
2.  **File Selection:** Clicking the icon opens the native file browser, restricted to PDF files.
3.  **Attachment Indication:** Upon selection, the chosen PDF's filename is displayed near the input area, with an option to remove/cancel the attachment before sending.
4.  **Sending:** The user types their message as usual and clicks the send button. If a PDF is attached, both the message text and the PDF file are submitted together in a single request. If no file is attached, only the text message is sent.

### Backend Processing

1.  **Unified Endpoint:** The existing chat API endpoint will handle both text-only messages and messages with PDF attachments.
2.  **Content Handling:**
    *   The endpoint will detect if a request contains a PDF file (`multipart/form-data`) or just text (`application/json`).
    *   If a PDF is present, the backend will extract its text content using a standard library (e.g., PyPDFLoader initially).
    *   The extracted text will be clearly labeled (e.g., enclosed in markers like `--- PDF Content Start --- ... --- PDF Content End ---`) and prepended to the user's typed message (if any).
3.  **Agent Input:** The combined text (extracted PDF + user message) or just the user message is passed as a single string input to the backend agent.

### Agent Interaction

1.  **Input Format:** The agent receives a text string which may contain clearly demarcated text extracted from a user-attached PDF, followed by the user's message.
2.  **Processing:** The agent processes this potentially augmented input as part of the conversational context, utilizing the information from the PDF as needed. 