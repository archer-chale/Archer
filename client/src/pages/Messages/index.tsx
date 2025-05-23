import  { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  CircularProgress,
  Alert,
  Button,
  Fab,
  Switch,
  FormControlLabel
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useMessage } from '../../hooks/useMessage.hook';
import ViewAllMessages from '../../components/messages/viewAllMessages.component';
import CreateMessageDialog from '../../components/messages/createMessageDialog.component';
import { IConfigMessage } from '../../types/pubsubmessage.type';

/**
 * Messages page component
 * Displays messages and provides interface for creating new messages
 */
// Mock data for IConfigMessage objects
const mockMessages: IConfigMessage[] = [
  {
    id: 'msg-001',
    description: 'Start counter at 10',
    acknowledgement: ['bot-1', 'bot-3'],
    acknowledgementCount: 2,
    config: { startCountAt: 10 },
    target: { type: 'ALL', selected: [] }
  },
  {
    id: 'msg-002',
    description: 'Reset selected counters',
    acknowledgement: ['bot-2'],
    acknowledgementCount: 1,
    config: { startCountAt: 0 },
    target: { 
      type: 'SELECTED', 
      selected: ['bot-2', 'bot-4'] 
    }
  },
  {
    id: 'msg-003',
    description: 'Configure all bots with advanced settings',
    acknowledgement: [],
    acknowledgementCount: 0,
    config: { 
      startCountAt: 5,
      interval: 2000,
      enableLogging: true,
      maxCount: 100
    },
    target: { type: 'ALL', selected: [] }
  }
];

const Messages = () => {
  const { messagesV2, loading, error, getAllMessages, deleteMessageById } = useMessage();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [useMockData, setUseMockData] = useState(true);
  
  // Use mock data or real data based on the toggle
  const displayMessages = useMockData || messagesV2.length === 0 ? mockMessages : messagesV2;

  // Load messages when component mounts
  useEffect(() => {
    getAllMessages();
    // Note: messagesV2 is populated by the useMessage hook via the saveMessage function
    // and the Firebase real-time subscription
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
        {/* Mock data toggle - only for development */}
        <Grid item xs={12} sx={{ mb: 2 }}>
          <FormControlLabel
            control={<Switch checked={useMockData} onChange={(e) => setUseMockData(e.target.checked)} />}
            label="Use mock data"
          />
        </Grid>
        
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
              messages={displayMessages}
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
