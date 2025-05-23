import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  CircularProgress,
  Stack,
  Paper,
  Card,
  CardContent,
  DialogContentText,
  Grid,
  Tooltip,
  alpha
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { IConfigMessage } from '../../types/pubsubmessage.type';
import { useMessage } from '../../hooks/useMessage.hook';

/**
 * Props for the CreateMessageDialog component
 */
interface CreateMessageDialogProps {
  open: boolean;
  onClose: () => void;
  onMessageCreated?: (message: IConfigMessage) => void;
}

/**
 * Component for creating new messages to send to bots
 * Provides a form with validation for configuring messages
 */
const CreateMessageDialog: React.FC<CreateMessageDialogProps> = ({
  open,
  onClose,
  onMessageCreated
}) => {
  const { saveMessage, loading } = useMessage();
  
  // Form state
  const [description, setDescription] = useState('');
  
  // Custom config state
  const [customConfigs, setCustomConfigs] = useState<{[key: string]: string | number | boolean}>({});
  const [configTypes, setConfigTypes] = useState<{[key: string]: 'string' | 'number' | 'boolean'}>({});
  const [newConfigKey, setNewConfigKey] = useState('');
  const [newConfigValue, setNewConfigValue] = useState('');
  const [newConfigType, setNewConfigType] = useState<'string' | 'number' | 'boolean'>('string');

  // Validation errors
  const [descriptionError, setDescriptionError] = useState('');
  
  // Confirmation dialog state
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  /**
   * Reset form state to default values
   */
  const resetForm = () => {
    setDescription('');
    setCustomConfigs({});
    setConfigTypes({});
    setNewConfigKey('');
    setNewConfigValue('');
    setNewConfigType('string');
    setDescriptionError('');
  };

  /**
   * Handle dialog close and reset form
   */
  const handleClose = () => {
    resetForm();
    onClose();
  };
  
  /**
   * Handle the dialog close request with confirmation if needed
   */
  const handleCloseRequest = () => {
    // Check if there's any data to lose
    const hasData = description.trim() !== '' || Object.keys(customConfigs).length > 0;
    
    if (hasData) {
      setConfirmDialogOpen(true);
    } else {
      handleClose();
    }
  };
  
  /**
   * Cancel the close request
   */
  const handleCancelClose = () => {
    setConfirmDialogOpen(false);
  };

  /**
   * Add a new custom configuration
   */
  const handleAddConfig = () => {
    if (!newConfigKey.trim()) return;
    if (newConfigType !== 'boolean' && !newConfigValue.trim()) return;
    
    let typedValue: string | number | boolean = newConfigValue;
    
    // Convert value based on selected type
    if (newConfigType === 'number') {
      typedValue = Number(newConfigValue);
      if (isNaN(typedValue)) typedValue = 0;
    } else if (newConfigType === 'boolean') {
      typedValue = newConfigValue === 'true';
    }
    
    setCustomConfigs({ ...customConfigs, [newConfigKey]: typedValue });
    setConfigTypes({ ...configTypes, [newConfigKey]: newConfigType });
    setNewConfigKey('');
    setNewConfigValue('');
    setNewConfigType('string');
  };

  /**
   * Remove a custom configuration
   * @param configKeyToRemove - The key of the configuration to remove
   */
  const handleRemoveConfig = (configKeyToRemove: string) => {
    const updatedConfigs = { ...customConfigs };
    const updatedTypes = { ...configTypes };
    delete updatedConfigs[configKeyToRemove];
    delete updatedTypes[configKeyToRemove];
    setCustomConfigs(updatedConfigs);
    setConfigTypes(updatedTypes);
  };

  /**
   * Validate form inputs
   * @returns Whether the form is valid
   */
  const validateForm = (): boolean => {
    let isValid = true;
    
    // Validate description
    if (!description.trim()) {
      setDescriptionError('Description is required');
      isValid = false;
    } else {
      setDescriptionError('');
    }
    
    return isValid;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    // Create message object
    const message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'> = {
      description,
      config: { ...customConfigs },
      target: {
        type: 'ALL',
        selected: []
      }
    };

    console.log("message", message);
    
    // Save message
    const result = await saveMessage(message);
    
    if (result) {
      resetForm();
      onMessageCreated?.(result);
      onClose();
    }
  };



  return (
    <>
      {/* Main Dialog */}
      <Dialog 
        open={open} 
        onClose={handleCloseRequest} 
        fullWidth 
        maxWidth="md"
        PaperProps={{
          sx: {
            borderRadius: 2,
            overflow: 'hidden'
          }
        }}
      >
      <DialogTitle sx={{ 
        backgroundColor: 'primary.main', 
        color: 'primary.contrastText',
        py: 2.5
      }}>Create New Message</DialogTitle>
      <DialogContent sx={{ overflowY: 'auto' }}>
        {/* Custom configurations */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="h6" component="h3" sx={{ mb: 2, fontWeight: 500 }}>
              Custom Configurations
            </Typography>
            
            <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2, mb: 3 }}>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
                <TextField
                  label="Key"
                  placeholder="Enter key name"
                  value={newConfigKey}
                  onChange={(e) => setNewConfigKey(e.target.value.replace(/\s+/g, ''))}
                  variant="outlined"
                  size="small"
                  fullWidth
                  InputProps={{
                    sx: { borderRadius: 1.5 }
                  }}
                />
                
                {newConfigType !== 'boolean' ? (
                  <TextField
                    label="Value"
                    placeholder={newConfigType === 'number' ? "Enter a number" : "Enter value"}
                    value={newConfigValue}
                    onChange={(e) => setNewConfigValue(e.target.value)}
                    variant="outlined"
                    type={newConfigType === 'number' ? 'number' : 'text'}
                    size="small"
                    fullWidth
                    InputProps={{
                      sx: { borderRadius: 1.5 }
                    }}
                  />
                ) : (
                  <FormControl variant="outlined" size="small" fullWidth>
                    <InputLabel>Value</InputLabel>
                    <Select
                      value={newConfigValue}
                      onChange={(e) => setNewConfigValue(e.target.value)}
                      label="Value"
                      sx={{ borderRadius: 1.5 }}
                    >
                      <MenuItem value="true">True</MenuItem>
                      <MenuItem value="false">False</MenuItem>
                    </Select>
                  </FormControl>
                )}
                
                <FormControl variant="outlined" size="small" sx={{ minWidth: 140 }}>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={newConfigType}
                    onChange={(e) => setNewConfigType(e.target.value as 'string' | 'number' | 'boolean')}
                    label="Type"
                    sx={{ borderRadius: 1.5 }}
                  >
                    <MenuItem value="string">String</MenuItem>
                    <MenuItem value="number">Number</MenuItem>
                    <MenuItem value="boolean">Boolean</MenuItem>
                  </Select>
                </FormControl>
                
                <Button 
                  variant="contained" 
                  onClick={() => handleAddConfig()} 
                  disabled={!newConfigKey.trim() || (newConfigType !== 'boolean' && !newConfigValue.trim())}
                  startIcon={<AddIcon />}
                  sx={{ 
                    borderRadius: 1.5,
                    textTransform: 'none',
                    px: 3,
                    whiteSpace: 'nowrap'
                  }}
                >
                  Add
                </Button>
              </Stack>
            </Paper>
            
            {/* Display custom configurations */}
            <Box sx={{ mb: Object.entries(customConfigs).length > 0 ? 3 : 0 }}>
              <Grid container spacing={2}>
                {Object.entries(customConfigs).length === 0 ? (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary" sx={{ pl: 1 }}>
                      No custom configurations added.
                    </Typography>
                  </Grid>
                ) : (
                  Object.entries(customConfigs).map(([key, value]) => {
                    const valueType = configTypes[key] || 'string';
                    let chipColor = 'default';
                    let bgColor = 'rgba(0,0,0,0.04)';
                    let valueDisplay = String(value);
                    
                    if (valueType === 'number') {
                      chipColor = 'primary';
                      bgColor = alpha('#1976d2', 0.08);
                      valueDisplay = Number(value).toString();
                    } else if (valueType === 'boolean') {
                      chipColor = 'secondary';
                      bgColor = alpha('#9c27b0', 0.08);
                      valueDisplay = Boolean(value).toString();
                    } else if (valueType === 'string') {
                      valueDisplay = `"${value}"`;
                    }
                    
                    return (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 1.5, 
                            bgcolor: bgColor,
                            borderRadius: 2,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            height: '100%'
                          }}
                        >
                          <Box sx={{ overflow: 'hidden', flexGrow: 1 }}>
                            <Typography 
                              variant="subtitle2" 
                              sx={{ 
                                fontWeight: 600, 
                                mb: 0.5,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5 
                              }}
                            >
                              {key}
                              <Chip 
                                label={valueType} 
                                size="small" 
                                color={chipColor as any}
                                sx={{ 
                                  height: 20, 
                                  '& .MuiChip-label': { 
                                    px: 1,
                                    fontSize: '0.65rem',
                                    fontWeight: 500 
                                  } 
                                }}
                              />
                            </Typography>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                overflow: 'hidden', 
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                fontFamily: 'monospace',
                                fontSize: '0.85rem' 
                              }}
                            >
                              {valueDisplay}
                            </Typography>
                          </Box>
                          <Button
                            size="small"
                            variant="text"
                            color="inherit"
                            onClick={() => handleRemoveConfig(key)}
                            sx={{ 
                              minWidth: 32, 
                              width: 32, 
                              height: 32,
                              p: 0,
                              ml: 1,
                              opacity: 0.6,
                              '&:hover': { opacity: 1 } 
                            }}
                            disabled={loading}
                          >
                            <DeleteIcon fontSize="small" />
                          </Button>
                        </Paper>
                      </Grid>
                    );
                  })
                )}
              </Grid>
            </Box>
            
            {/* Config Preview */}
            {Object.entries(customConfigs).length > 0 && (
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 2, 
                  bgcolor: 'background.default', 
                  borderRadius: 2,
                  position: 'relative'
                }}
              >
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  mb: 1.5 
                }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CodeIcon fontSize="small" color="primary" />
                    <Typography variant="subtitle2">
                      Config Preview
                    </Typography>
                  </Stack>
                  <Tooltip title="This is how your configuration will appear in the message">
                    <InfoOutlinedIcon fontSize="small" sx={{ opacity: 0.6 }} />
                  </Tooltip>
                </Box>
                <Box 
                  sx={{ 
                    p: 1.5, 
                    bgcolor: alpha('#000', 0.03),
                    borderRadius: 1.5,
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    overflowX: 'auto'
                  }}
                >
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {JSON.stringify(customConfigs, null, 2)}
                  </pre>
                </Box>
              </Paper>
            )}
          </CardContent>
        </Card>

        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="h6" component="h3" sx={{ mb: 2, fontWeight: 500 }}>
              Message Details
            </Typography>
            <TextField
              label="Description"
              placeholder="Enter message description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              error={!!descriptionError}
              helperText={descriptionError}
              disabled={loading}
              InputProps={{
                sx: { borderRadius: 1.5 }
              }}
            />
          </CardContent>
        </Card>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, py: 2.5, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
        <Button 
          onClick={handleClose}
          disabled={loading}
          variant="outlined"
          sx={{ 
            borderRadius: 1.5,
            textTransform: 'none',
            px: 3
          }}
        >
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
          sx={{ 
            borderRadius: 1.5,
            textTransform: 'none',
            px: 3
          }}
        >
          {loading ? 'Creating...' : 'Create Message'}
        </Button>
      </DialogActions>
    </Dialog>
    
    {/* Confirmation Dialog */}
    <Dialog open={confirmDialogOpen} onClose={handleCancelClose}>
      <DialogTitle>Discard changes?</DialogTitle>
      <DialogContent>
        <DialogContentText>
          You have unsaved changes. Are you sure you want to close this dialog and discard your changes?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancelClose} color="primary" variant="outlined" sx={{ borderRadius: 1.5 }}>
          Cancel
        </Button>
        <Button onClick={handleClose} color="error" variant="contained" sx={{ borderRadius: 1.5 }}>
          Discard
        </Button>
      </DialogActions>
    </Dialog>
    </>
  );
};

export default CreateMessageDialog;
