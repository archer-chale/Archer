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

  return { services, loading, error };
};
