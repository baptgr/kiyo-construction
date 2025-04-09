import { Box, IconButton, TextareaAutosize, Chip } from '@mui/material';
import SendIcon from '../components/SendIcon';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CloseIcon from '@mui/icons-material/Close';
import { useState, useRef } from 'react';

export default function MessageInput({ onSendMessage, isTyping }) {
  const [inputMessage, setInputMessage] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setAttachedFile(file);
    } else {
      // Optional: Add some user feedback if the file is not a PDF
      console.warn("Please select a PDF file.");
      setAttachedFile(null); // Clear if invalid file type
    }
    // Reset file input value to allow selecting the same file again
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const removeAttachment = () => {
    setAttachedFile(null);
  };


  const handleSubmit = (e) => {
    e.preventDefault();
    const messageToSend = inputMessage.trim();
    
    if (messageToSend || attachedFile) {
      if (attachedFile) {
        const formData = new FormData();
        formData.append('message', messageToSend);
        formData.append('pdf_file', attachedFile);
        onSendMessage(formData); // Parent needs to handle FormData
      } else {
        onSendMessage(messageToSend); // Send as plain text
      }
      setInputMessage('');
      setAttachedFile(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isTyping) { // Only submit if not typing
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const canSubmit = (inputMessage.trim() || attachedFile) && !isTyping;

  return (
    <Box sx={{ width: '100%' }}> 
      <Box 
        component="form" 
        onSubmit={handleSubmit}
        sx={{ 
          display: 'flex',
          alignItems: 'flex-end', // Align items to bottom
          gap: 1,
          position: 'relative',
          padding: '8px', // Add some padding around
          border: '1px solid var(--input-border)',
          borderRadius: '3px',
          backgroundColor: 'var(--input-background)',
        }}
      >
        {/* Hidden File Input */}
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        {/* Attachment Button */}
        <IconButton 
            onClick={triggerFileInput}
            size="small" // Keep it visually similar to send
            disabled={isTyping}
            sx={{ 
              color: 'var(--color-text-secondary)',
              padding: '8px',
              flexShrink: 0,
              alignSelf: 'flex-end',
               mb: '2px', // Fine-tune vertical alignment if needed
               '&:hover': {
                  bgcolor: 'var(--color-surface)',
                  color: 'var(--color-text-primary)',
               },
               '&.Mui-disabled': {
                  opacity: 0.5,
               }
            }}
          >
          <AttachFileIcon sx={{ fontSize: 20 }}/>
        </IconButton>

        {/* Text Input */}
        <TextareaAutosize
          placeholder="Message your agent..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isTyping}
          autoComplete="off"
          maxRows={6}
          style={{
            width: '100%',
            resize: 'none',
            padding: '8px 12px', // Adjusted padding
            borderRadius: '3px',
            border: 'none', // Border is now on the outer Box
            backgroundColor: 'transparent', // Inherit from parent Box
            color: 'var(--color-text-primary)',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            fontFamily: 'inherit',
            outline: 'none',
          }}
        />
        {/* Send Button */}
        <IconButton 
          color="primary" 
          type="submit" 
          disabled={!canSubmit} // Use combined condition
          sx={{ 
            bgcolor: 'transparent', 
            color: 'var(--color-text-secondary)',
            border: 'none',
            borderRadius: '3px',
            padding: '8px',
            alignSelf: 'flex-end',
            height: '36px',
            width: '36px',
            flexShrink: 0,
            transition: 'all 0.2s ease',
            '&:hover': {
              bgcolor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
            },
            '&.Mui-disabled': {
              opacity: 0.5,
              color: 'var(--color-text-secondary)',
            }
          }}
        >
          <SendIcon sx={{ fontSize: 20 }} />
        </IconButton>
      </Box>
      {/* Attached File Indicator */}
      {attachedFile && (
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-start' }}>
            <Chip
                icon={<AttachFileIcon />}
                label={attachedFile.name}
                size="small"
                onDelete={removeAttachment}
                deleteIcon={<CloseIcon />}
                sx={{ 
                    maxWidth: 'calc(100% - 16px)', // Ensure chip doesn't overflow container padding
                     backgroundColor: 'var(--color-surface-secondary)', 
                     color: 'var(--color-text-secondary)' 
                 }}
            />
        </Box>
      )}
    </Box>
  );
} 