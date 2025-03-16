/**
 * Routes Path Constants
 * 
 * This file centralizes all route path definitions used throughout the application.
 * By using these constants instead of hardcoded strings, we make navigation more
 * consistent and future route changes easier to implement across the application.
 */

/**
 * Main Dashboard route
 * Landing page showing service status and monitoring
 */
export const DASHBOARD = '/';

/**
 * Messages route
 * Page for creating, viewing, and managing messages sent to bots
 */
export const MESSAGES = '/messages';

/**
 * Object containing all routes for easier imports
 */
export const ROUTES = {
  DASHBOARD,
  MESSAGES
} as const;

/**
 * Navigation items for the sidebar/menu
 * Each item has a path, label, and optional icon identifier
 */
export const NAV_ITEMS = [
  {
    path: DASHBOARD,
    label: 'Dashboard',
    icon: 'TrendingUp'
  },
  {
    path: MESSAGES,
    label: 'Messages',
    icon: 'Assessment'
  }
] as const;
