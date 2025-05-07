import { 
  Accordion, 
  AccordionDetails, 
  AccordionSummary, 
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid, 
  List,
  ListItem,
  Paper,
  Typography,
} from '@mui/material';
import { 
  ExpandMore, 
  TrendingUp, 
  TrendingDown, 
  AttachMoney, 
  AccessTime, 
  LocalOffer 
} from '@mui/icons-material';
import { useFirebaseServices } from '../../hooks/useFirebaseServices';

// Status color mapping
const statusColors = {
  running: 'success',
  paused: 'warning',
  stopped: 'error',
  active: 'success',
  filled: 'success'
} as const;

// Order side color and icon mapping
const sideColors = {
  buy: 'success',
  sell: 'error'
} as const;

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
        {services.map((service) => {
          const hasOrders = service.orders && Object.keys(service.orders).length > 0;
          return (
            <Grid item xs={12} md={6} lg={4} key={service.ticker}>
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
                        color={statusColors[service.status]} 
                        size="small" 
                        sx={{ mt: 1 }}
                      />
                    )}
                  </Box>
                  
                  {/* Stock Price and Info */}
                  <Box sx={{ p: 2, backgroundColor: 'white' }}>
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
                          mt: 0.5 
                        }}>
                          <AccessTime fontSize="small" sx={{ mr: 0.5 }} />
                          Updated: {formatDate(service.timestamp)}
                        </Typography>
                      </Box>
                    )}

                    {/* Orders Accordion */}
                    {hasOrders && (
                      <Accordion sx={{ 
                        boxShadow: 'none', 
                        '&:before': { display: 'none' },
                        mt: 1
                      }}>
                        <AccordionSummary 
                          expandIcon={<ExpandMore />}
                          sx={{ backgroundColor: '#f5f5f5', borderRadius: '8px' }}
                        >
                          <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                            {Object.keys(service.orders).length} Recent Orders
                          </Typography>
                        </AccordionSummary>
                        
                        <AccordionDetails sx={{ p: 0, maxHeight: '300px', overflow: 'auto' }}>
                          <List sx={{ p: 0 }}>
                            {Object.entries(service.orders).map(([orderId, orderData]) => (
                              <ListItem 
                                key={orderId} 
                                divider 
                                sx={{ 
                                  flexDirection: 'column', 
                                  alignItems: 'flex-start',
                                  p: 1.5
                                }}
                              >
                                <Box sx={{ 
                                  display: 'flex', 
                                  width: '100%', 
                                  justifyContent: 'space-between', 
                                  alignItems: 'center',
                                  mb: 1
                                }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Chip 
                                      label={orderData.order.side.toUpperCase()}
                                      color={sideColors[orderData.order.side as keyof typeof sideColors]}
                                      size="small"
                                      sx={{ mr: 1 }}
                                    />
                                    <Typography variant="subtitle2">
                                      {orderData.order.order_type.toUpperCase()}
                                    </Typography>
                                  </Box>
                                  <Typography variant="body2" color="text.secondary">
                                    ID: {orderData.order.id.slice(0, 8)}...
                                  </Typography>
                                </Box>

                                <Divider flexItem sx={{ mb: 1 }} />
                                <Grid container spacing={1}>
                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">
                                      Quantity
                                    </Typography>
                                    <Typography variant="body2">
                                      {orderData.qty}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">
                                      Price
                                    </Typography>
                                    <Typography variant="body2">
                                      ${parseFloat(orderData.price).toFixed(2)}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">
                                      Position Qty
                                    </Typography>
                                    <Typography variant="body2">
                                      {orderData.position_qty}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">
                                      Status
                                    </Typography>
                                    <Typography variant="body2">
                                      <Chip 
                                        label={orderData.order.status}
                                        color={statusColors[orderData.order.status as keyof typeof statusColors] || 'default'}
                                        size="small"
                                      />
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={12}>
                                    <Typography variant="caption" color="text.secondary">
                                      Timestamp
                                    </Typography>
                                    <Typography variant="body2">
                                      {formatDate(orderData.timestamp)}
                                    </Typography>
                                  </Grid>
                                </Grid>
                              </ListItem>
                            ))}
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    )}

                    {/* Bots Section */}
                    {service.bots && Object.keys(service.bots).length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'medium', mb: 1 }}>
                          Active Bots
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1.5, borderRadius: '8px' }}>
                          {Object.entries(service.bots).map(([botId, bot]) => (
                            <Box key={botId} sx={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              mb: 1,
                              pb: 1,
                              borderBottom: '1px solid #eee',
                              '&:last-child': { mb: 0, pb: 0, borderBottom: 'none' }
                            }}>
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                  Bot {botId.slice(0, 6)}...
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {bot.count} trades
                                </Typography>
                              </Box>
                              <Chip 
                                label={bot.status}
                                color={statusColors[bot.status]}
                                size="small"
                              />
                            </Box>
                          ))}
                        </Paper>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </div>
  );
};

export default Dashboard;
