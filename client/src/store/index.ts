import { useServicesStore } from './services.store';
import { useMessagesStore } from './message.store';

// Export all stores
export { useServicesStore };
export { useMessagesStore };

// Add utility functions for working with both stores

/**
 * Helper function to get all active bots across services
 * Useful for populating target selection dropdowns
 */
export const getActiveBotOptions = () => {
  const { getActiveBots } = useServicesStore.getState();
  
  const bots = getActiveBots();
  return bots.map(bot => ({
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
