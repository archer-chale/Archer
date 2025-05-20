import { 
  Box, 
  Card, 
  CardContent, 
  Chip, 
  Typography 
} from '@mui/material';
import { 
  ArrowUpward, 
  ArrowDownward,
  AccessTime
} from '@mui/icons-material';

// Status color mapping (reused from Dashboard)
const statusColors = {
  running: 'success',
  paused: 'warning',
  stopped: 'error',
  active: 'success',
  filled: 'success'
} as const;

// Interface for component props
interface TickerCardProps {
  service: {
    ticker: string;
    price?: string;
    status?: string;
    timestamp?: string;
    performance?: {
      total: string;
      unrealized: string;
      realized: string;
      converted: string; // Added converted field
      timestamp: string;
    };
  };
  formatDate: (timestamp: string) => string;
}

const TickerCard = ({ service, formatDate }: TickerCardProps) => {
  // Helper function to determine if a value is positive
  const isPositive = (value: string) => {
    const numValue = parseFloat(value);
    return numValue > 0;
  };
  
  // Helper function to format performance values
  const formatPerformance = (value: string) => {
    const numValue = parseFloat(value);
    const formatted = Math.abs(numValue).toFixed(2);
    return numValue >= 0 ? `+$${formatted}` : `-$${formatted}`;
  };
  
  return (
    <Card raised sx={{
      width: '100%',
      borderRadius: '12px',
      overflow: 'hidden',
      transition: 'all 0.3s ease',
      '&:hover': { transform: 'translateY(-5px)' },
    }}>
      <CardContent sx={{ p: 0 }}>
        {/* Stock Header */}
        <Box sx={{ 
          p: 2, 
          backgroundColor: '#1e88e5', 
          color: 'white', 
          borderBottom: '1px solid rgba(0,0,0,0.1)' 
        }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            {service.ticker}
          </Typography>
          {service.status && (
            <Chip 
              label={service.status} 
              color={statusColors[service.status as keyof typeof statusColors] || 'default'} 
              size="small" 
              sx={{ mt: 1 }}
            />
          )}
        </Box>
        
        {/* Stock Price and Info */}
        <Box sx={{ p: 2, backgroundColor: 'white' }}>
          {/* Price Section */}
          {service.price && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="h4" sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                fontWeight: 'bold' 
              }}>
                ${parseFloat(service.price).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 0.5 
              }}>
                <AccessTime fontSize="small" />
                Last updated: {formatDate(service.timestamp || '')}
              </Typography>
            </Box>
          )}
          
          {/* Performance Section */}
          {service.performance && (
            <Box sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'medium', mb: 1 }}>
                Performance
              </Typography>
              
              {/* Total Performance */}
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                mb: 1,
                p: 1.5,
                backgroundColor: '#f5f5f5',
                borderRadius: '8px'
              }}>
                <Typography variant="body1">Total Profit/Loss:</Typography>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 0.5,
                  color: isPositive(service.performance.total) ? 'success.main' : 'error.main',
                  fontWeight: 'bold'
                }}>
                  {isPositive(service.performance.total) ? (
                    <ArrowUpward fontSize="small" />
                  ) : (
                    <ArrowDownward fontSize="small" />
                  )}
                  <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                    {formatPerformance(service.performance.total)}
                  </Typography>
                </Box>
              </Box>
              
              {/* Detailed Performance Section */}
              <Box sx={{ 
                mt: 1.5, 
                p: 1.5, 
                border: '1px solid #e0e0e0', 
                borderRadius: '8px' 
              }}>
                {/* Unrealized Section */}
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 1
                }}>
                  <Typography variant="body2">Unrealized:</Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 0.5,
                    color: isPositive(service.performance.unrealized) ? 'success.main' : 'error.main'
                  }}>
                    {isPositive(service.performance.unrealized) ? (
                      <ArrowUpward fontSize="small" />
                    ) : (
                      <ArrowDownward fontSize="small" />
                    )}
                    <Typography variant="body2">
                      {formatPerformance(service.performance.unrealized)}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Realized Section */}
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 1
                }}>
                  <Typography variant="body2">Realized:</Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 0.5,
                    color: isPositive(service.performance.realized) ? 'success.main' : 'error.main'
                  }}>
                    {isPositive(service.performance.realized) ? (
                      <ArrowUpward fontSize="small" />
                    ) : (
                      <ArrowDownward fontSize="small" />
                    )}
                    <Typography variant="body2">
                      {formatPerformance(service.performance.realized)}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Converted Section */}
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <Typography variant="body2">Converted:</Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 0.5,
                    color: isPositive(service.performance.converted) ? 'success.main' : 'error.main'
                  }}>
                    {isPositive(service.performance.converted) ? (
                      <ArrowUpward fontSize="small" />
                    ) : (
                      <ArrowDownward fontSize="small" />
                    )}
                    <Typography variant="body2">
                      {formatPerformance(service.performance.converted)}
                    </Typography>
                  </Box>
                </Box>
              </Box>
              
              {/* Performance Timestamp */}
              <Typography variant="caption" color="text.secondary" sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 0.5,
                mt: 1,
                justifyContent: 'flex-end'
              }}>
                <AccessTime fontSize="small" />
                Performance updated: {formatDate(service.performance.timestamp)}
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default TickerCard;
