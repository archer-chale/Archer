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
  DialogContentText
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
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
  const { saveMessage, loading, error } = useMessage();
  
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
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
              {Object.entries(customConfigs).length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No custom configurations added.
                </Typography>
              ) : (
                Object.entries(customConfigs).map(([key, value]) => {
                  const valueType = configTypes[key] || 'string';
                  let chipColor = 'default';
                  if (valueType === 'number') chipColor = 'primary';
                  if (valueType === 'boolean') chipColor = 'secondary';
                  
                  return (
                    <Chip
                      key={key}
                      label={`${key}: ${value}`}
                      onDelete={() => handleRemoveConfig(key)}
                      disabled={loading}
                      color={chipColor as any}
                      sx={{ 
                        maxWidth: '100%', 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        borderRadius: 1.5,
                        '& .MuiChip-deleteIcon': {
                          color: 'inherit',
                          opacity: 0.7,
                          '&:hover': { opacity: 1 }
                        }
                      }}
                      deleteIcon={<DeleteIcon />}
                    />
                  );
                })
              )}
            </Box>
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
