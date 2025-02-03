import { Card, CardContent, Typography, Grid } from '@mui/material';

const Dashboard = () => {
  const services = [
    { ticker: 'AAPL', status: 'Running' },
    { ticker: 'META', status: 'Running' },
    { ticker: 'AMZN', status: 'Running' }
  ];

  return (
    <div style={{ padding: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Trading Bot Services
      </Typography>
      <Grid container spacing={3}>
        {services.map((service) => (
          <Grid item xs={12} sm={6} md={4} key={service.ticker}>
            <Card>
              <CardContent>
                <Typography variant="h5">{service.ticker}</Typography>
                <Typography color="textSecondary">
                  Status: {service.status}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default Dashboard;