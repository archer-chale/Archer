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
import Logs from '../pages/Logs';

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
      <List>
        <ListItem disablePadding>
          <ListItemButton 
            component={Link} 
            to="/"
            selected={isActive('/')}
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
            to="/logs"
            selected={isActive('/logs')}
            onClick={() => setDrawerOpen(false)}
          >
            <ListItemIcon>
              <Assessment />
            </ListItemIcon>
            <ListItemText primary="Logs" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <Menu />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div">
            Trading Bot System
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: 250 
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Desktop drawer - always visible */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          sx={{
            width: 250,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 250,
              boxSizing: 'border-box',
            },
          }}
          open
        >
          <Toolbar /> {/* Empty toolbar to push content below AppBar */}
          {drawerContent}
        </Drawer>
      )}

      {/* Main content */}
      <Box component="main" sx={{ 
        flexGrow: 1, 
        p: 3,
        width: { sm: `calc(100% - ${250}px)` },
        marginLeft: { sm: '250px' }
      }}>
        <Toolbar /> {/* Empty toolbar to push content below AppBar */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/logs" element={<Logs />} />
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
