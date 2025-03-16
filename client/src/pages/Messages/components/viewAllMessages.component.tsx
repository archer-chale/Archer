import React, { useState } from 'react';
import {
  Typography,
  Box,
  IconButton,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Collapse,
  Divider,
  Chip,
  Grid
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DeleteIcon from '@mui/icons-material/Delete';
import { IConfigMessage, IConfigMessageSimple } from '../../../types/pubsubmessage.type';
import { useMessage } from '../../../hooks/useMessage.hook';

/**
 * Props for the ViewAllMessages component
 */
interface ViewAllMessagesProps {
  messages: IConfigMessageSimple[];
  onDeleteMessage?: (messageId: string) => void;
  loading?: boolean;
}

/**
 * Component for displaying all messages using expandable cards
 * Each card can be expanded to show message details
 */
const ViewAllMessages: React.FC<ViewAllMessagesProps> = ({
  messages,
  onDeleteMessage,
  loading = false
}) => {
  const { getMessageDetailsById } = useMessage();
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedMessage, setExpandedMessage] = useState<IConfigMessage | null>(null);

  /**
   * Toggles expansion of a card
   * @param messageId - ID of the message to expand/collapse
   */
  const handleExpandClick = async (messageId: string) => {
    if (expandedId === messageId) {
      // If already expanded, collapse it
      setExpandedId(null);
      setExpandedMessage(null);
    } else {
      // If not expanded, fetch details and expand it
      setExpandedId(messageId);
      const messageDetails = await getMessageDetailsById(messageId);
      if (messageDetails) {
        setExpandedMessage(messageDetails);
      }
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #eee' }}>
        <Typography variant="h6">
          Message History
        </Typography>
        <Typography variant="body2" color="text.secondary">
          View and manage all messages sent to bots
        </Typography>
      </Box>

      {messages.length === 0 ? (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No messages available. Create a new message to get started.
          </Typography>
        </Box>
      ) : (
        <Box sx={{ mt: 2 }}>
          {messages.map((message) => (
            <Card 
              key={message.id} 
              sx={{ 
                mb: 2, 
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                }
              }}
            >
              <CardHeader
                title={message.description}
                subheader={`Acknowledgements: ${message.acknowledgementCount}`}
                action={
                  <IconButton
                    onClick={() => handleExpandClick(message.id)}
                    aria-expanded={expandedId === message.id}
                    aria-label="show more"
                    sx={{ 
                      transform: expandedId === message.id ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.2s'
                    }}
                  >
                    <ExpandMoreIcon />
                  </IconButton>
                }
              />
              
              <Collapse in={expandedId === message.id} timeout="auto" unmountOnExit>
                {expandedMessage && expandedMessage.id === message.id && (
                  <CardContent>
                    <Divider sx={{ mb: 2 }} />
                    
                    {/* Message configuration */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Configuration
                      </Typography>
                      <Box sx={{ 
                        p: 2, 
                        borderRadius: 1, 
                        backgroundColor: '#f5f5f5',
                        fontSize: '0.9rem'
                      }}>
                        <Typography>
                          <strong>Start Count At:</strong> {expandedMessage.config.startCountAt}
                        </Typography>
                      </Box>
                    </Box>
                    
                    {/* Target information */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Target
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Chip 
                          label={expandedMessage.target.type === 'ALL' ? 'All Bots' : 'Selected Bots'} 
                          color={expandedMessage.target.type === 'ALL' ? 'primary' : 'secondary'}
                          size="small"
                        />
                      </Box>
                      
                      {expandedMessage.target.type === 'SELECTED' && expandedMessage.target.selected.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {expandedMessage.target.selected.map((target) => (
                            <Chip key={target} label={target} size="small" />
                          ))}
                        </Box>
                      )}
                    </Box>
                    
                    {/* Acknowledgements */}
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Acknowledgements ({expandedMessage.acknowledgementCount})
                      </Typography>
                      
                      {expandedMessage.acknowledgement.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">
                          No acknowledgements yet.
                        </Typography>
                      ) : (
                        <Grid container spacing={1}>
                          {expandedMessage.acknowledgement.map((botId) => (
                            <Grid item key={botId}>
                              <Chip label={botId} size="small" />
                            </Grid>
                          ))}
                        </Grid>
                      )}
                    </Box>
                  </CardContent>
                )}
              </Collapse>
              
              <CardActions sx={{ 
                display: 'flex', 
                justifyContent: 'flex-end',
                borderTop: expandedId === message.id ? '1px solid #eee' : 'none',
                p: 1 
              }}>
                {onDeleteMessage && (
                  <IconButton
                    color="error"
                    onClick={() => onDeleteMessage(message.id)}
                    disabled={loading}
                    size="small"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                )}
              </CardActions>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default ViewAllMessages;
