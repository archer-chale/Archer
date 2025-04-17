import { create } from 'zustand';
import { Service } from '../service/firebase/firebase-endpoint.service';

interface ServicesState {
  // State
  services: Service[];
  loading: boolean;
  error: string | null;
  
  // Actions
  setServices: (services: Service[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  
  // Selectors
  getServices: () => Service[];
}

/**
 * Store for managing services
 * Simple state container that gets updated by the useFirebaseServices hook
 */
export const useServicesStore = create<ServicesState>((set, get) => {
  return {
    // State
    services: [],
    loading: false,
    error: null,
    
    // Actions
    setServices: (services) => {
      set({ services });
    },
    
    setLoading: (loading) => {
      set({ loading });
    },
    
    setError: (error) => {
      set({ error });
    },
    
    reset: () => {
      set({
        services: [],
        loading: false,
        error: null
      });
    },
    
    // Selectors
    getServices: () => {
      return get().services;
    }
  };
});
