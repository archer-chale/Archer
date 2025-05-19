import { useServicesStore } from './services.store';

// Export all stores
export { useServicesStore };

// Add utility functions for working with both stores

/**
 * Helper function to get all active bots across services
 * Useful for populating target selection dropdowns
 */
export const getActiveBotOptions = () => {
  const { getServices } = useServicesStore.getState();
  
  const bots = getServices();
  return bots.map((bot: any) => ({
    id: bot.botId,
    label: `${bot.ticker} - ${bot.botId} (${bot.status})`
  }));
};

/**
 * Helper function to get unique tickers from all services
 * Useful for grouping or filtering bots by ticker
 */
export const getUniqueTickers = () => {
  const { getServices } = useServicesStore.getState();
  
  const services = getServices();
  const tickers = services.map(service => service.ticker);
  return [...new Set(tickers)];
};
