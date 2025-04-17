import { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { Menu, TrendingUp, Assessment } from '@mui/icons-material';
import Dashboard from '../pages/Dashboard';
import Messages from '../pages/Messages';
import { DASHBOARD, MESSAGES } from './routes.path';

/**
 * Navigation component for the application
 * Handles top navigation bar and mobile drawer navigation
 */
const Navigation = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();

  /**
   * Handles opening the mobile navigation drawer
   */
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  /**
   * Determines if a navigation item is currently active
   * @param path - The path to check against current location
   */
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  /**
   * Renders the navigation drawer content
   * Used by both the permanent and temporary drawers
   */
  const drawerContent = (
    <Box sx={{ width: 250 }}>
      <Toolbar /> {/* Empty toolbar to push content below AppBar */}
      <List>
        <ListItem disablePadding>
          <ListItemButton 
            component={Link} 
            to={DASHBOARD}
            selected={isActive(DASHBOARD)}
            onClick={() => setDrawerOpen(false)}
          >
            <ListItemIcon>
              <TrendingUp />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton 
            component={Link} 
            to={MESSAGES}
            selected={isActive(MESSAGES)}
            onClick={() => setDrawerOpen(false)}
          >
            <ListItemIcon>
              <Assessment />
            </ListItemIcon>
            <ListItemText primary="Messages" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <Menu />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Trading Bot System
          </Typography>
          
          {/* Desktop horizontal navigation */}
          {!isMobile && (
            <Box sx={{ display: 'flex' }}>
              <Box 
                component={Link} 
                to={DASHBOARD}
                sx={{
                  color: 'white',
                  textDecoration: 'none',
                  mx: 2,
                  fontWeight: isActive(DASHBOARD) ? 'bold' : 'normal',
                  borderBottom: isActive(DASHBOARD) ? '2px solid white' : 'none',
                }}
              >
                Dashboard
              </Box>
              <Box 
                component={Link} 
                to={MESSAGES}
                sx={{
                  color: 'white',
                  textDecoration: 'none',
                  mx: 2,
                  fontWeight: isActive(MESSAGES) ? 'bold' : 'normal',
                  borderBottom: isActive(MESSAGES) ? '2px solid white' : 'none',
                }}
              >
                Messages
              </Box>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
          zIndex: theme.zIndex.drawer + 2
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ 
        flexGrow: 1, 
        p: { xs: 2, md: 3 },
        width: '100%',
        overflow: 'hidden',
        maxWidth: '100vw',
      }}>
        <Toolbar /> {/* Empty toolbar to push content below AppBar */}
        <Routes>
          <Route path={DASHBOARD} element={<Dashboard />} />
          <Route path={MESSAGES} element={<Messages />} />
        </Routes>
      </Box>
    </Box>
  );
};

/**
 * AppRouter component
 * Sets up the React Router with the Navigation component
 */
const AppRouter = () => {
  return (
    <BrowserRouter>
      <Navigation />
    </BrowserRouter>
  );
};

export default AppRouter;
