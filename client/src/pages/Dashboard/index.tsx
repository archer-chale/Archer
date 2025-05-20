import { 
  Alert,
  CircularProgress,
  Grid, 
  Typography 
} from '@mui/material';
import { 
  AttachMoney
} from '@mui/icons-material';
import { useFirebaseServices } from '../../hooks/useFirebaseServices';
import TickerCard from './Component/TickerCard.Component';
import AggregatePerformanceCard from './Component/AggregatePerformanceCard.Component';

const Dashboard = () => {
  // Use the Firebase hook to get real data
  const { services: allServices, loading, error } = useFirebaseServices();
  
  // Find the aggregate data if it exists
  const aggregateData = allServices?.find(service => service.ticker?.toLowerCase() === 'aggregate');
  
  // Filter out the aggregate ticker from the regular services
  const services = allServices?.filter(service => service.ticker?.toLowerCase() !== 'aggregate') || [];
  
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
        <Grid item xs={12} sx={{ textAlign: 'center', mb: 0 }}>
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
        
        {/* Aggregate Performance Card - only show if we have aggregate data */}
        {aggregateData?.performance && (
          <Grid item xs={12} sx={{ mb: 3 }}>
            <AggregatePerformanceCard 
              performance={aggregateData.performance} 
              formatDate={formatDate} 
            />
          </Grid>
        )}

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
