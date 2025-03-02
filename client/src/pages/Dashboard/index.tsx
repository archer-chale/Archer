import { useState } from 'react';
import { 
  Accordion, 
  AccordionDetails, 
  AccordionSummary, 
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid, 
  TextField,
  Typography,
} from '@mui/material';
import { ExpandMore, TrendingUp, Send } from '@mui/icons-material';
import { useFirebaseServices } from '../../hooks/useFirebaseServices';

// Status color mapping
const statusColors = {
  running: 'success',
  paused: 'warning',
  stopped: 'error',
  active: 'success'
} as const;

const Dashboard = () => {
  const { services, loading, error } = useFirebaseServices();
  
  // State for the global message form
  const [globalMessage, setGlobalMessage] = useState('');
  
  // State for the bot-specific message dialog
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedBotId, setSelectedBotId] = useState<string | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [botMessage, setBotMessage] = useState('');

  /**
   * Handles submission of a global message to all bots
   * Uses the Firebase service to send a message to all bots
   */
  const handleSendGlobalMessage = () => {
    if (globalMessage.trim()) {
      // TODO: Replace with actual send message functionality
      alert(`Sending to ALL bots: ${globalMessage}`);
      setGlobalMessage('');
    }
  };

  /**
   * Opens the dialog for sending a message to a specific bot
   * @param ticker - The ticker symbol of the service
   * @param botId - The ID of the bot to send a message to
   */
  const handleOpenBotDialog = (ticker: string, botId: string) => {
    setSelectedBotId(botId);
    setSelectedTicker(ticker);
    setOpenDialog(true);
  };

  /**
   * Closes the bot message dialog and resets its state
   */
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setBotMessage('');
    setSelectedBotId(null);
    setSelectedTicker(null);
  };

  /**
   * Handles submission of a message to a specific bot
   * Uses the Firebase service to send a message to the selected bot
   */
  const handleSendBotMessage = () => {
    if (botMessage.trim() && selectedBotId && selectedTicker) {
      // TODO: Replace with actual send message functionality
      alert(`Sending to ${selectedTicker}/${selectedBotId}: ${botMessage}`);
      handleCloseDialog();
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem' }}>
        <Alert severity="error">
          Error loading services: {error}
        </Alert>
      </div>
    );
  }

  return (
    <div style={{
      padding: '2rem',
      width: '100%',
      height: '100%'
    }}>
      <Grid container spacing={2} sx={{
        width: '100%',
        maxWidth: 1200,
        margin: '0 auto',
        justifyContent: 'center'
      }}>
        <Grid item xs={12} sx={{ textAlign: 'center' }}>
          <Typography variant="h4" sx={{ 
            mb: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2
          }}>
            <TrendingUp fontSize="large" />
            Trading Bot Services
          </Typography>
        </Grid>

        {/* Global Message Form */}
        <Grid item xs={12} md={8} sx={{ mb: 4 }}>
          <Box 
            component="form" 
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              alignItems: 'center',
              gap: 2,
              p: 2,
              backgroundColor: 'white',
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            }}
            onSubmit={(e) => {
              e.preventDefault();
              handleSendGlobalMessage();
            }}
          >
            <TextField
              fullWidth
              label="Send message to ALL bots"
              variant="outlined"
              value={globalMessage}
              onChange={(e) => setGlobalMessage(e.target.value)}
              placeholder="Type your message here..."
            />
            <Button 
              variant="contained" 
              color="primary" 
              type="submit"
              startIcon={<Send />}
              sx={{ 
                minWidth: { xs: '100%', sm: 'auto' },
                whiteSpace: 'nowrap'
              }}
            >
              Send to All
            </Button>
          </Box>
        </Grid>

        {/* Bot Cards */}
        {services.map((service) => (
          <Grid item xs={12} md={8} key={service.ticker}>
            <Accordion sx={{
              width: '100%',
              borderRadius: '8px!important',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              transition: '0.3s',
              '&:hover': { transform: 'translateY(-2px)' },
              backgroundColor: 'white'
            }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Grid container alignItems="center" spacing={2}>
                  <Grid item>
                    <Typography variant="h6">{service.ticker}</Typography>
                  </Grid>
                  <Grid item>
                    <Chip 
                      label={service.status} 
                      color={statusColors[service.status]} 
                      size="small" 
                    />
                  </Grid>
                </Grid>
              </AccordionSummary>
              
              <AccordionDetails>
                <Grid container spacing={2}>
                  {service.bots && Object.entries(service.bots).map(([botId, bot]) => (
                    <Grid item xs={12} key={botId} sx={{
                      display: 'flex',
                      flexDirection: { xs: 'column', sm: 'row' },
                      justifyContent: 'space-between',
                      alignItems: { xs: 'flex-start', sm: 'center' },
                      borderBottom: '1px solid #eee',
                      pb: 2,
                      mb: 2
                    }}>
                      <Box>
                        <Typography variant="body1">
                          Bot {botId}: {bot.count} trades
                          <Chip 
                            label={bot.status}
                            color={statusColors[bot.status]}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last updated: {new Date(bot.last_updated).toLocaleString()}
                        </Typography>
                      </Box>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Send />}
                        onClick={() => handleOpenBotDialog(service.ticker, botId)}
                        sx={{ mt: { xs: 1, sm: 0 } }}
                      >
                        Send Message
                      </Button>
                    </Grid>
                  ))}
                  {(!service.bots || Object.keys(service.bots).length === 0) && (
                    <Grid item xs={12}>
                      <Typography color="text.secondary">
                        No active bots
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>

      {/* Bot Message Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          Send Message to {selectedTicker} - Bot {selectedBotId}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter a message to send to this specific bot:
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Message"
            type="text"
            fullWidth
            variant="outlined"
            value={botMessage}
            onChange={(e) => setBotMessage(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSendBotMessage} color="primary" variant="contained" startIcon={<Send />}>
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Dashboard;
