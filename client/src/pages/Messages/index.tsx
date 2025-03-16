import React from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  CircularProgress,
  Alert
} from '@mui/material';
import { useFirebaseLogs } from '../../hooks/useFirebaseLogs';

/**
 * Logs page component
 * Displays log entries from the pub/sub system
 */
const Messages = () => {
  const { logs, loading, error } = useFirebaseLogs();

  // Format timestamp to human-readable format
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <Box sx={{
      p: 3,
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
        {/* Page Title */}
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" gutterBottom>
            System Logs
          </Typography>
          <Typography variant="subtitle1" gutterBottom>
            View real-time logs from all trading bots
          </Typography>
        </Grid>

        {/* Error message */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error">
              Error loading logs: {error}
            </Alert>
          </Grid>
        )}

        {/* Loading indicator */}
        {loading && (
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Grid>
        )}

        {/* Logs Table */}
        {!loading && !error && (
          <Grid item xs={12}>
            <TableContainer component={Paper} sx={{ 
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              borderRadius: '8px',
              overflow: 'auto',
              width: '100%'
            }}>
              <Table sx={{ minWidth: { xs: 300, sm: 650 } }}>
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Container ID</TableCell>
                    <TableCell>Message</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} align="center">
                        No logs available
                      </TableCell>
                    </TableRow>
                  ) : (
                    logs.map((log) => (
                      <TableRow key={log.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                        <TableCell>{formatDate(log.timestamp)}</TableCell>
                        <TableCell>{log.containerId}</TableCell>
                        <TableCell>{log.message}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Messages;
