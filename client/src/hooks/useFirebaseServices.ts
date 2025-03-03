import { useState, useEffect } from 'react';
import { Service } from '../service/firebase/firebase-endpoint.service';
import { firebaseServiceController } from '../service/controllers/firebase.service.controller';

/**
 * Custom hook for accessing Firebase services
 * Provides real-time updates of service status and bots
 */
export const useFirebaseServices = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      // Subscribe to services using the controller
      const unsubscribe = firebaseServiceController.getServices((servicesData) => {
        setServices(servicesData);
        setLoading(false);
      });

      // Cleanup subscription
      return () => unsubscribe();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setLoading(false);
      return () => {}; // Empty cleanup if setup failed
    }
  }, []);

  /**
   * Send a message to a specific bot or all bots
   * @param message - Message content
   * @param target - Target container ID or "ALL" for all bots
   * @returns Promise resolving to true if successful
   */
  const sendMessage = async (message: string, target: string): Promise<boolean> => {
    try {
      return await firebaseServiceController.sendMessage(message, target);
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  };

  return { services, loading, error, sendMessage };
};
