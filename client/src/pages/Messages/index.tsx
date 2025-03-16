import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  CircularProgress,
  Alert,
  Button,
  Fab
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useMessage } from '../../hooks/useMessage.hook';
import ViewAllMessages from './components/viewAllMessages.component';
import CreateMessageDialog from './components/createMessageDialog.component';

/**
 * Messages page component
 * Displays messages and provides interface for creating new messages
 */
const Messages = () => {
  const { messages, loading, error, getAllMessages, deleteMessageById } = useMessage();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // Load messages when component mounts
  useEffect(() => {
    getAllMessages();
  }, [getAllMessages]);

  /**
   * Opens the create message dialog
   */
  const handleOpenCreateDialog = () => {
    setCreateDialogOpen(true);
  };

  /**
   * Closes the create message dialog
   */
  const handleCloseCreateDialog = () => {
    setCreateDialogOpen(false);
  };

  /**
   * Deletes a message
   * @param messageId - ID of the message to delete
   */
  const handleDeleteMessage = async (messageId: string) => {
    await deleteMessageById(messageId);
  };

  /**
   * Refreshes the message list after a new message is created
   */
  const handleMessageCreated = () => {
    getAllMessages();
  };

  return (
    <Box sx={{
      p: { xs: 2, sm: 3 },
      width: '100%',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      <Grid container spacing={2} sx={{
        width: '100%',
        maxWidth: { xs: '100%', lg: 1200 },
        margin: '0 auto',
        justifyContent: 'center'
      }}>
        {/* Page Title and Actions */}
        <Grid item xs={12} sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: { xs: 1, sm: 2 } 
        }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Messages
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              Create and manage messages for your bots
            </Typography>
          </Box>
          <Button 
            variant="contained" 
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenCreateDialog}
            sx={{ display: { xs: 'none', sm: 'flex' } }}
          >
            New Message
          </Button>
        </Grid>

        {/* Error message */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error">
              Error: {error}
            </Alert>
          </Grid>
        )}

        {/* Loading indicator */}
        {loading && (
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Grid>
        )}

        {/* Messages list */}
        {!loading && !error && (
          <Grid item xs={12}>
            <ViewAllMessages 
              messages={messages}
              onDeleteMessage={handleDeleteMessage}
              loading={loading}
            />
          </Grid>
        )}
      </Grid>

      {/* Mobile floating action button for creating messages */}
      <Box sx={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        display: { xs: 'block', sm: 'none' } 
      }}>
        <Fab 
          color="primary" 
          aria-label="add" 
          onClick={handleOpenCreateDialog}
        >
          <AddIcon />
        </Fab>
      </Box>

      {/* Create message dialog */}
      <CreateMessageDialog 
        open={createDialogOpen} 
        onClose={handleCloseCreateDialog}
        onMessageCreated={handleMessageCreated}
      />
    </Box>
  );
};

export default Messages;
