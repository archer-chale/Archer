# Performance-to-Client Frontend Implementation Checklist

This checklist outlines all the necessary steps to implement the stock performance data display in the frontend application.

## 1. Create TickerCard Component

**File:** `client\src\pages\Dashboard\Component\TickerCard.Component.tsx`

**Why:** We need to create a dedicated component for displaying stock information including performance data in a mobile-friendly format. This will help us separate concerns and make the main Dashboard component cleaner.

**Tasks:**
- [ ] Create the new component file and directory structure
- [ ] Design a mobile-friendly card layout
- [ ] Include price display similar to current implementation
- [ ] Add performance data section showing total, unrealized, and realized values
- [ ] Apply color-coding (green for positive, red for negative) with clear signs
- [ ] Add up/down arrow icons beside each value
- [ ] Make the component accept stock data via props
- [ ] Remove orders section from the display

**Pseudo Code:**
```tsx
import { 
  Box, 
  Card, 
  CardContent, 
  Chip, 
  Typography 
} from '@mui/material';
import { 
  AttachMoney, 
  ArrowUpward, 
  ArrowDownward 
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
                  justifyContent: 'space-between'
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
```

## 2. Update Dashboard Component

**File:** `client\src\pages\Dashboard\index.tsx`

**Why:** We need to update the main Dashboard component to use our new TickerCard component and remove the orders section.

**Tasks:**
- [ ] Import the new TickerCard component
- [ ] Replace the existing card implementation with the new component
- [ ] Remove orders-related code
- [ ] Pass the necessary props to the TickerCard component

**Pseudo Code:**
```tsx
import { 
  Alert,
  CircularProgress,
  Grid, 
  Typography,
} from '@mui/material';
import { 
  AttachMoney, 
} from '@mui/icons-material';
import { useFirebaseServices } from '../../hooks/useFirebaseServices';
import TickerCard from './Component/TickerCard.Component';

const Dashboard = () => {
  const { services, loading, error } = useFirebaseServices();
  console.log("services", services);

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

  // Format timestamp to a readable date
  const formatDate = (timestamp: string) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div style={{
      padding: '1.5rem',
      width: '100%',
      height: '100%',
      backgroundColor: '#f5f5f5'
    }}>
      <Grid container spacing={3} sx={{
        width: '100%',
        maxWidth: { xs: '100%', lg: 1200 },
        margin: '0 auto',
      }}>
        <Grid item xs={12} sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ 
            mb: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2
          }}>
            <AttachMoney fontSize="large" />
            Stock Market Dashboard
          </Typography>
        </Grid>

        {/* Stock Cards */}
        {services.map((service) => (
          <Grid item xs={12} md={6} lg={4} key={service.ticker}>
            <TickerCard service={service} formatDate={formatDate} />
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default Dashboard;
```

## 3. Update useFirebaseServices Hook

**File:** `client\src\hooks\useFirebaseServices.ts`

**Why:** We need to update the hook to retrieve and handle the performance data from Firebase.

**Tasks:**
- [ ] Update the data structure to include performance data
- [ ] Update the hook to listen for performance data changes
- [ ] Handle the type definitions for the new performance data

**Pseudo Code:**
```typescript
import { useEffect, useState } from 'react';
import { db } from '../firebase';
import { ref, onValue } from 'firebase/database';

// Define interface for service performance
interface Performance {
  total: string;
  unrealized: string;
  realized: string;
  converted: string;
  timestamp: string;
}

// Define interface for service data
interface Service {
  ticker: string;
  price?: string;
  timestamp?: string;
  status?: string;
  performance?: Performance;
  bots?: Record<string, {
    status: string;
    count: number;
  }>;
}

export const useFirebaseServices = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const servicesRef = ref(db, 'services');
    
    const unsubscribe = onValue(servicesRef, (snapshot) => {
      try {
        setLoading(true);
        const data = snapshot.val();
        
        if (!data) {
          setServices([]);
          return;
        }
        
        // Transform data from object to array
        const servicesArray: Service[] = Object.keys(data).map(ticker => {
          const serviceData = data[ticker];
          
          return {
            ticker,
            price: serviceData.price,
            timestamp: serviceData.timestamp,
            status: serviceData.status,
            performance: serviceData.performance,
            bots: serviceData.bots
          };
        });
        
        setServices(servicesArray);
        setError(null);
      } catch (err) {
        console.error('Error parsing services data:', err);
        setError('Failed to parse services data');
      } finally {
        setLoading(false);
      }
    }, (err) => {
      console.error('Firebase database error:', err);
      setError(err.message);
      setLoading(false);
    });
    
    return () => unsubscribe();
  }, []);
  
  return { services, loading, error };
};
```
## 5. Check and Update TypeScript Types

**File:** `client\src\types\index.ts` (or create if it doesn't exist)

**Why:** We need to ensure we have proper type definitions for our data structures.

**Tasks:**
- [ ] Define common interfaces for use across components
- [ ] Create types for service, performance, and other shared data structures

**Pseudo Code:**
```typescript
// Service Performance data
export interface Performance {
  total: string;
  unrealized: string;
  realized: string;
  converted?: string;
  timestamp: string;
}

// Bot data
export interface Bot {
  status: string;
  count: number;
}

// Main service data structure
export interface Service {
  ticker: string;
  price?: string;
  timestamp?: string;
  status?: string;
  performance?: Performance;
  bots?: Record<string, Bot>;
}
```
