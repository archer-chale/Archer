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
import { IConfigMessage } from '../../types/pubsubmessage.type';

/**
 * Props for the ViewAllMessages component
 */
interface ViewAllMessagesProps {
  messages: IConfigMessage[];
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
  const [expandedId, setExpandedId] = useState<string | null>(null);

  /**
   * Toggles expansion of a card
   * @param messageId - ID of the message to expand/collapse
   */
  const handleExpandClick = (messageId: string) => {
    if (expandedId === messageId) {
      // If already expanded, collapse it
      setExpandedId(null);
    } else {
      // If not expanded, expand it
      setExpandedId(messageId);
    }
  };

  console.log("messages", messages)
  console.log("expandedId", expandedId)

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
                subheader={`Acknowledgements: ${message.acknowledgement?.length || 0}`}
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
                {expandedId === message.id && (
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
                        fontSize: '0.9rem',
                        fontFamily: 'monospace'
                      }}>
                        {!message.config || Object.keys(message.config).length === 0 ? (
                          <Typography color="text.secondary">No configuration values.</Typography>
                        ) : (
                          <Grid container spacing={1}>
                            {Object.entries(message.config).map(([key, value]) => {
                              // Determine the type of value for styling
                              const valueType = typeof value;
                              let chipColor = 'default';
                              let valueDisplay = String(value);
                              
                              if (valueType === 'number') {
                                chipColor = 'primary';
                              } else if (valueType === 'boolean') {
                                chipColor = 'secondary';
                              } else if (valueType === 'string') {
                                valueDisplay = `"${value}"`;
                              }
                              
                              return (
                                <Grid item xs={12} key={key}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Typography sx={{ fontWeight: 'bold', mr: 1 }}>{key}:</Typography>
                                    <Chip 
                                      size="small" 
                                      label={valueType}
                                      color={chipColor as any}
                                      sx={{ 
                                        height: 20, 
                                        mr: 1,
                                        '& .MuiChip-label': { 
                                          px: 1,
                                          fontSize: '0.65rem',
                                          fontWeight: 500 
                                        } 
                                      }}
                                    />
                                    <Typography>{valueDisplay}</Typography>
                                  </Box>
                                </Grid>
                              );
                            })}
                          </Grid>
                        )}
                      </Box>
                    </Box>
                    
                    {/* Target information */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Target
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Chip 
                          label={message.target.type === 'ALL' ? 'All Bots' : 'Selected Bots'} 
                          color={message.target.type === 'ALL' ? 'primary' : 'secondary'}
                          size="small"
                        />
                      </Box>
                      
                      {message.target.type === 'SELECTED' && message.target.selected.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {message.target.selected.map((target) => (
                            <Chip key={target} label={target} size="small" />
                          ))}
                        </Box>
                      )}
                    </Box>
                    
                    {/* Acknowledgements */}
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Acknowledgements ({message.acknowledgement?.length || 0})
                      </Typography>
                      
                      {message.acknowledgement?.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">
                          No acknowledgements yet.
                        </Typography>
                      ) : (
                        <Grid container spacing={1}>
                          {message.acknowledgement?.map((botId) => (
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
