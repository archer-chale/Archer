import { useState, useEffect } from 'react';
import { Service } from '../service/firebase/firebase-endpoint.service';
import { firebaseServiceController } from '../service/controllers/firebase.service.controller';
import { useServicesStore } from '../store/services.store';

/**
 * Custom hook for accessing Firebase services
 * Provides real-time updates of service status and bots
 * Updates the services store with the latest data
 */
export const useFirebaseServices = () => {
  // Get direct access to local state for backwards compatibility
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Get access to store actions
  const setStoreServices = useServicesStore(state => state.setServices);
  const setStoreLoading = useServicesStore(state => state.setLoading);
  const setStoreError = useServicesStore(state => state.setError);

  useEffect(() => {
    // Update store loading state
    setStoreLoading(true);
    
    try {
      // Subscribe to services using the controller
      const unsubscribe = firebaseServiceController.getServices((servicesData) => {
        // Update local state
        setServices(servicesData);
        setLoading(false);
        
        // Update store state
        setStoreServices(servicesData);
        setStoreLoading(false);
      });

      // Cleanup subscription
      return () => {
        unsubscribe();
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      
      // Update local state
      setError(errorMessage);
      setLoading(false);
      
      // Update store state
      setStoreError(errorMessage);
      setStoreLoading(false);
      
      return () => {}; // Empty cleanup if setup failed
    }
  }, [setStoreServices, setStoreLoading, setStoreError]);

  return { services, loading, error };
};
