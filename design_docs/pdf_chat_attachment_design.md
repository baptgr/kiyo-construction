# PDF Chat Attachment Design

This document outlines the target solution for allowing users to attach **multiple** PDF files within the chat interface.

## Target Solution

### User Experience (Frontend)

1.  **Attachment UI:** A "paperclip" icon will be added to the chat input area.
2.  **File Selection:** Clicking the icon opens the native file browser, allowing the selection of **one or more** PDF files (restricted to PDF type).
3.  **Attachment Indication:** Upon selection, the chosen **PDFs' filenames** are displayed near the input area (e.g., as a list or chips), with an option to remove/cancel individual or all attachments before sending.
4.  **Sending:** The user types their message as usual and clicks the send button. If **PDF(s)** are attached, both the message text and the **PDF files** are submitted together in a single `multipart/form-data` request. If no files are attached, only the text message is sent (potentially as `application/json`).

### Backend Processing

1.  **Unified Endpoint:** The existing chat API endpoint will handle text-only messages and messages with **one or more** PDF attachments.
2.  **Content Handling:**
    *   The endpoint will detect if a request contains PDF files (`multipart/form-data`) or just text (`application/json`).
    *   If **PDFs** are present, the backend will receive a list of files. It will iterate through this list, extracting text content from each PDF using a suitable library (e.g., PyPDFLoader).
    *   The extracted text from **all PDFs** will be combined (e.g., concatenated with clear separators indicating the source file, like `--- PDF Content Start: file1.pdf --- ... --- PDF Content End: file1.pdf --- --- PDF Content Start: file2.pdf --- ... --- PDF Content End: file2.pdf ---`) and prepended to the user's typed message (if any).
3.  **Agent Input:** The combined text (extracted PDF(s) + user message) or just the user message is passed as a single string input to the backend agent.

### Agent Interaction

1.  **Input Format:** The agent receives a text string which may contain clearly demarcated text extracted from **one or more** user-attached PDFs, followed by the user's message.
2.  **Processing:** The agent processes this potentially augmented input as part of the conversational context, utilizing the information from the **PDF(s)** as needed. 