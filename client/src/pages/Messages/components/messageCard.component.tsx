import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  Divider,
  IconButton,
  Collapse,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CloseIcon from '@mui/icons-material/Close';
import { IConfigMessage } from '../../../types/pubsubmessage.type';
import { useMessage } from '../../../hooks/useMessage.hook';

/**
 * Props for the MessageCard component
 */
interface MessageCardProps {
  messageId: string | null;
  onClose: () => void;
}

/**
 * Component for displaying detailed information about a message
 * Shows config settings, target information, and acknowledgments
 */
const MessageCard: React.FC<MessageCardProps> = ({ messageId, onClose }) => {
  const { getMessageDetailsById, loading, error } = useMessage();
  const [message, setMessage] = useState<IConfigMessage | null>(null);
  const [expanded, setExpanded] = useState(true);
  
  /**
   * Load message details when messageId changes
   */
  useEffect(() => {
    const fetchMessageDetails = async () => {
      if (messageId) {
        const messageDetails = await getMessageDetailsById(messageId);
        if (messageDetails) {
          setMessage(messageDetails);
        }
      } else {
        setMessage(null);
      }
    };
    
    fetchMessageDetails();
  }, [messageId, getMessageDetailsById]);
  
  /**
   * Toggle expansion state of the card
   */
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  
  // Don't render if no message ID is provided
  if (!messageId) return null;
  
  return (
    <Card sx={{ 
      width: '100%', 
      mb: 3, 
      boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
      borderRadius: '8px' 
    }}>
      <CardHeader
        title={
          <Typography variant="h6" component="div">
            Message Details
          </Typography>
        }
        action={
          <>
            <IconButton
              onClick={handleExpandClick}
              aria-expanded={expanded}
              aria-label="show more"
              sx={{ 
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s'
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </>
        }
        sx={{ 
          borderBottom: '1px solid #eee',
          backgroundColor: '#f9f9f9'
        }}
      />
      
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent>
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress />
            </Box>
          )}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {!loading && !error && message && (
            <>
              {/* Message description */}
              <Typography variant="h6" gutterBottom>
                {message.description}
              </Typography>
              
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
                    <strong>Start Count At:</strong> {message.config.startCountAt}
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
              
              <Divider sx={{ my: 2 }} />
              
              {/* Acknowledgements */}
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Acknowledgements ({message.acknowledgementCount})
                </Typography>
                
                {message.acknowledgement.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No acknowledgements yet.
                  </Typography>
                ) : (
                  <List dense>
                    {message.acknowledgement.map((botId) => (
                      <ListItem key={botId}>
                        <ListItemText 
                          primary={botId} 
                          primaryTypographyProps={{ 
                            variant: 'body2' 
                          }} 
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Collapse>
    </Card>
  );
};

export default MessageCard;
