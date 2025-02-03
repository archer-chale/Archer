import { 
    Accordion, 
    AccordionSummary, 
    AccordionDetails, 
    Typography, 
    Grid, 
    Chip,
    Avatar,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    CircularProgress,
    IconButton,
    Fab
  } from '@mui/material';
  import {
    ExpandMore,
    Add,
    TrendingUp,
    PauseCircleOutline,
    PlayCircleOutline,
    Settings
  } from '@mui/icons-material';
  
  const services = [
    { 
      ticker: 'AAPL', 
      status: 'running', 
      bots: [
        { id: 1, count: 142, status: 'active' },
        { id: 2, count: 89, status: 'paused' }
      ]
    },
    { 
      ticker: 'META', 
      status: 'paused', 
      bots: [
        { id: 1, count: 256, status: 'active' }
      ]
    },
    { 
      ticker: 'AMZN', 
      status: 'stopped', 
      bots: []
    }
  ];
  
  const statusColor = {
    running: 'success',
    paused: 'warning',
    stopped: 'error'
  } as const;
  
  const Dashboard = () => (
    <div style={{
      padding: '2rem',
      width: '100%',
      height: '100%'
    }}>
      <Grid container spacing={2} sx={{
        width: '100%',
        maxWidth: 1200,
        margin: '0 auto',
        justifyContent: 'center'
      }}>
        <Grid item xs={12} sx={{ textAlign: 'center' }}>
          <Typography variant="h4" sx={{ 
            mb: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}>
            <TrendingUp fontSize="large" />
            Trading Bot Services
          </Typography>
        </Grid>

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
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      {service.ticker[0]}
                    </Avatar>
                  </Grid>
                  <Grid item xs>
                    <Typography variant="h6">{service.ticker}</Typography>
                  </Grid>
                  <Grid item>
                    <Chip 
                      label={service.status}
                      color={statusColor[service.status]}
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
              </AccordionSummary>

              <AccordionDetails>
                {service.bots.length > 0 ? (
                  <List dense>
                    {service.bots.map((bot) => (
                      <ListItem 
                        key={bot.id}
                        secondaryAction={
                          <IconButton edge="end">
                            <Settings />
                          </IconButton>
                        }
                      >
                        <ListItemAvatar>
                          <CircularProgress 
                            variant="determinate" 
                            value={Math.min((bot.count % 100), 100)}
                            size={32}
                            thickness={4}
                          />
                        </ListItemAvatar>
                        <ListItemText
                          primary={`Bot #${bot.id}`}
                          secondary={`Count: ${bot.count} • ${bot.status}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="textSecondary" align="center">
                    No active bots
                  </Typography>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>
    </div>
  );
  
  export default Dashboard;