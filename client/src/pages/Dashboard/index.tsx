import { 
  Accordion, 
  AccordionDetails, 
  AccordionSummary, 
  Alert,
  Box,
  Chip,
  CircularProgress,
  Grid, 
  Typography,
} from '@mui/material';
import { ExpandMore, TrendingUp } from '@mui/icons-material';
import { useFirebaseServices } from '../../hooks/useFirebaseServices';

// Status color mapping
const statusColors = {
  running: 'success',
  paused: 'warning',
  stopped: 'error',
  active: 'success'
} as const;

const Dashboard = () => {
  const { services, loading, error } = useFirebaseServices();

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

  return (
    <div style={{
      padding: '2rem',
      width: '100%',
      height: '100%'
    }}>
      <Grid container spacing={2} sx={{
        width: '100%',
        maxWidth: { xs: '100%', lg: 1200 },
        margin: '0 auto',
        justifyContent: 'center'
      }}>
        <Grid item xs={12} sx={{ textAlign: 'center' }}>
          <Typography variant="h4" sx={{ 
            mb: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2
          }}>
            <TrendingUp fontSize="large" />
            Trading Bot Services
          </Typography>
        </Grid>

        {/* Bot Cards */}
        {services.map((service) => (
          <Grid item xs={12} md={8} key={service.ticker}>
            <Accordion sx={{
              width: '100%',
              borderRadius: '8px!important',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              transition: '0.3s',
              '&:hover': { transform: 'translateY(-2px)' },
              backgroundColor: 'white'
            }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Grid container alignItems="center" spacing={2}>
                  <Grid item>
                    <Typography variant="h6">{service.ticker}</Typography>
                  </Grid>
                  <Grid item>
                    <Chip 
                      label={service.status} 
                      color={statusColors[service.status]} 
                      size="small" 
                    />
                  </Grid>
                </Grid>
              </AccordionSummary>
              
              <AccordionDetails>
                <Grid container spacing={2}>
                  {service.bots && Object.entries(service.bots).map(([botId, bot]) => (
                    <Grid item xs={12} key={botId} sx={{
                      display: 'flex',
                      flexDirection: { xs: 'column', sm: 'row' },
                      justifyContent: 'space-between',
                      alignItems: { xs: 'flex-start', sm: 'center' },
                      borderBottom: '1px solid #eee',
                      pb: 2,
                      mb: 2
                    }}>
                      <Box>
                        <Typography variant="body1">
                          Bot {botId}: {bot.count} trades
                          <Chip 
                            label={bot.status}
                            color={statusColors[bot.status]}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last updated: {new Date(bot.last_updated).toLocaleString()}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                  {(!service.bots || Object.keys(service.bots).length === 0) && (
                    <Grid item xs={12}>
                      <Typography color="text.secondary">
                        No active bots
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default Dashboard;
