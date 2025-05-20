import { 
  Box,
  Card,
  CardContent,
  Chip,
  Grid, 
  Typography 
} from '@mui/material';
import { 
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';

interface AggregatePerformanceCardProps {
  performance: {
    total: string;
    unrealized: string;
    realized: string;
    converted: string;
    timestamp: string;
  };
  formatDate: (timestamp: string) => string;
}

const AggregatePerformanceCard = ({ performance, formatDate }: AggregatePerformanceCardProps) => {
  return (
    <Card raised sx={{
      width: '100%',
      borderRadius: '12px',
      overflow: 'hidden',
      transition: 'all 0.3s ease',
      backgroundColor: '#37474f',
      color: 'white',
    }}>
      <CardContent>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 2 
        }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Portfolio Performance
          </Typography>
          <Chip
            label={parseFloat(performance.total) >= 0 ? 'PROFIT' : 'LOSS'}
            color={parseFloat(performance.total) >= 0 ? 'success' : 'error'}
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
        
        {/* Total Performance */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
            Total Profit/Loss
          </Typography>
          <Typography variant="h4" sx={{ 
            fontWeight: 'bold',
            color: parseFloat(performance.total) >= 0 ? '#4caf50' : '#f44336',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            {parseFloat(performance.total) >= 0 ? (
              <ArrowUpward />
            ) : (
              <ArrowDownward />
            )}
            {parseFloat(performance.total) >= 0 ? 
              `+$${parseFloat(performance.total).toFixed(2)}` : 
              `-$${Math.abs(parseFloat(performance.total)).toFixed(2)}`}
          </Typography>
        </Box>
        
        {/* Detailed Performance */}
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ 
              p: 1.5, 
              borderRadius: '8px', 
              bgcolor: 'rgba(255,255,255,0.1)',
              height: '100%'
            }}>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
                Unrealized
              </Typography>
              <Typography variant="h6" sx={{ 
                color: parseFloat(performance.unrealized) >= 0 ? '#4caf50' : '#f44336',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}>
                {parseFloat(performance.unrealized) >= 0 ? (
                  <ArrowUpward fontSize="small" />
                ) : (
                  <ArrowDownward fontSize="small" />
                )}
                {parseFloat(performance.unrealized) >= 0 ? 
                  `+$${parseFloat(performance.unrealized).toFixed(2)}` : 
                  `-$${Math.abs(parseFloat(performance.unrealized)).toFixed(2)}`}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ 
              p: 1.5, 
              borderRadius: '8px', 
              bgcolor: 'rgba(255,255,255,0.1)',
              height: '100%'
            }}>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
                Realized
              </Typography>
              <Typography variant="h6" sx={{ 
                color: parseFloat(performance.realized) >= 0 ? '#4caf50' : '#f44336',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}>
                {parseFloat(performance.realized) >= 0 ? (
                  <ArrowUpward fontSize="small" />
                ) : (
                  <ArrowDownward fontSize="small" />
                )}
                {parseFloat(performance.realized) >= 0 ? 
                  `+$${parseFloat(performance.realized).toFixed(2)}` : 
                  `-$${Math.abs(parseFloat(performance.realized)).toFixed(2)}`}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ 
              p: 1.5, 
              borderRadius: '8px', 
              bgcolor: 'rgba(255,255,255,0.1)',
              height: '100%'
            }}>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
                Converted
              </Typography>
              <Typography variant="h6" sx={{ 
                color: parseFloat(performance.converted) >= 0 ? '#4caf50' : '#f44336',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}>
                {parseFloat(performance.converted) >= 0 ? (
                  <ArrowUpward fontSize="small" />
                ) : (
                  <ArrowDownward fontSize="small" />
                )}
                {parseFloat(performance.converted) >= 0 ? 
                  `+$${parseFloat(performance.converted).toFixed(2)}` : 
                  `-$${Math.abs(parseFloat(performance.converted)).toFixed(2)}`}
              </Typography>
            </Box>
          </Grid>
        </Grid>
        
        <Typography variant="caption" sx={{ 
          display: 'block', 
          textAlign: 'right', 
          mt: 2, 
          opacity: 0.7 
        }}>
          Last updated: {formatDate(performance.timestamp)}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default AggregatePerformanceCard;
