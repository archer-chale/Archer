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
  FormHelperText,
  Box,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Autocomplete
} from '@mui/material';
import { IConfigMessage, IMessageTarget } from '../../../types/pubsubmessage.type';
import { useMessage } from '../../../hooks/useMessage.hook';
import { useServicesStore } from '../../../store/services.store';

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
  const { services, loading: servicesLoading } = useServicesStore();
  
  // Form state
  const [description, setDescription] = useState('');
  const [startCountAt, setStartCountAt] = useState<number>(0);
  const [targetType, setTargetType] = useState<IMessageTarget['type']>('ALL');
  const [selectedTargets, setSelectedTargets] = useState<string[]>([]);
  const [newTarget, setNewTarget] = useState('');
  
  // Validation errors
  const [descriptionError, setDescriptionError] = useState('');
  const [startCountError, setStartCountError] = useState('');
  const [targetError, setTargetError] = useState('');

  /**
   * Reset form state to default values
   */
  const resetForm = () => {
    setDescription('');
    setStartCountAt(0);
    setTargetType('ALL');
    setSelectedTargets([]);
    setNewTarget('');
    setDescriptionError('');
    setStartCountError('');
    setTargetError('');
  };

  /**
   * Handle dialog close and reset form
   */
  const handleClose = () => {
    resetForm();
    onClose();
  };

  /**
   * Add a new target to the selected targets list
   */
  const handleAddTarget = () => {
    if (!newTarget) return;
    
    if (selectedTargets.includes(newTarget)) {
      setTargetError('This target is already added');
      return;
    }
    
    setSelectedTargets([...selectedTargets, newTarget]);
    setNewTarget('');
    setTargetError('');
  };

  /**
   * Remove a target from the selected targets list
   * @param targetToRemove - The target to remove
   */
  const handleRemoveTarget = (targetToRemove: string) => {
    setSelectedTargets(selectedTargets.filter(target => target !== targetToRemove));
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
    
    // Validate starting count
    if (startCountAt < 0) {
      setStartCountError('Starting count must be a positive number');
      isValid = false;
    } else {
      setStartCountError('');
    }
    
    // Validate targets for SELECTED type
    if (targetType === 'SELECTED' && selectedTargets.length === 0) {
      setTargetError('At least one target must be selected');
      isValid = false;
    } else {
      setTargetError('');
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
      config: { startCountAt },
      target: {
        type: targetType,
        selected: targetType === 'ALL' ? [] : selectedTargets
      }
    };
    
    // Save message
    const result = await saveMessage(message);
    
    if (result && onMessageCreated) {
      onMessageCreated(result);
      handleClose();
    }
  };

  /**
   * Handle selecting a service from the dropdown
   */
  const handleServiceSelect = (value: string | null) => {
    if (value && !selectedTargets.includes(value)) {
      setSelectedTargets([...selectedTargets, value]);
      setNewTarget('');
    }
  };

  // Get available service IDs/tickers for selection
  const availableServices = services
    .filter(service => {
      const serviceId = service.ticker;
      return !selectedTargets.includes(serviceId);
    })
    .map(service => service.ticker);

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ 
        sx: { 
          borderRadius: 2,
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        } 
      }}
    >
      <DialogTitle sx={{ 
        borderBottom: '1px solid #eee',
        fontSize: '1.5rem',
        fontWeight: 'bold',
        pb: 2
      }}>
        Create New Message
      </DialogTitle>
      
      <DialogContent sx={{ pt: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {/* Description field */}
        <TextField
          label="Description"
          fullWidth
          margin="normal"
          variant="outlined"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          error={!!descriptionError}
          helperText={descriptionError || 'Provide a description for this message'}
          disabled={loading}
        />
        
        {/* Configuration field */}
        <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>
          Counter Bot Configuration
        </Typography>
        
        <TextField
          label="Start Count At"
          type="number"
          fullWidth
          margin="normal"
          variant="outlined"
          value={startCountAt}
          onChange={(e) => setStartCountAt(Number(e.target.value))}
          error={!!startCountError}
          helperText={startCountError || 'The value to set the counter to'}
          disabled={loading}
          InputProps={{ inputProps: { min: 0 } }}
        />
        
        {/* Target selection */}
        <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>
          Target Configuration
        </Typography>
        
        <FormControl fullWidth error={!!targetError}>
          <InputLabel>Target Type</InputLabel>
          <Select
            value={targetType}
            label="Target Type"
            onChange={(e) => setTargetType(e.target.value as IMessageTarget['type'])}
            disabled={loading}
          >
            <MenuItem value="ALL">All Bots</MenuItem>
            <MenuItem value="SELECTED">Selected Bots</MenuItem>
          </Select>
          {targetError && <FormHelperText>{targetError}</FormHelperText>}
        </FormControl>
        
        {/* Target selection UI for SELECTED type */}
        {targetType === 'SELECTED' && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Autocomplete
                options={availableServices}
                value={null}
                onChange={(_, value) => handleServiceSelect(value)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Service"
                    variant="outlined"
                    size="small"
                    sx={{ flexGrow: 1 }}
                  />
                )}
                disabled={loading || servicesLoading}
                fullWidth
              />
              {servicesLoading && (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={24} />
                </Box>
              )}
            </Box>
            
            {/* Manual entry option */}
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                label="Add Custom Target"
                value={newTarget}
                onChange={(e) => setNewTarget(e.target.value)}
                variant="outlined"
                size="small"
                disabled={loading}
                sx={{ flexGrow: 1 }}
              />
              <Button 
                variant="contained" 
                onClick={handleAddTarget}
                disabled={!newTarget.trim() || loading}
              >
                Add
              </Button>
            </Box>
            
            {/* Display selected targets */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {selectedTargets.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No targets selected. Add at least one target.
                </Typography>
              ) : (
                selectedTargets.map((target) => (
                  <Chip
                    key={target}
                    label={target}
                    onDelete={() => handleRemoveTarget(target)}
                    disabled={loading}
                  />
                ))
              )}
            </Box>

            {/* Show service information */}
            {services.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Available Services: {services.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {services.map(s => s.ticker).join(', ')}
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>
      
      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #eee' }}>
        <Button 
          onClick={handleClose}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
        >
          {loading ? 'Creating...' : 'Create Message'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateMessageDialog;
