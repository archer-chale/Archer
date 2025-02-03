import { useState, useEffect } from 'react';
import { ref, onValue } from 'firebase/database';
import { db } from '../firebaseConfig';

export interface Bot {
  id: string;
  count: number;
  status: 'active' | 'paused';
  last_updated: string;
}

export interface Service {
  ticker: string;
  status: 'running' | 'paused' | 'stopped';
  bots: Record<string, Bot>;
}

export const useFirebaseServices = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const servicesRef = ref(db, 'services');

    const unsubscribe = onValue(servicesRef, (snapshot) => {
      try {
        const data = snapshot.val();
        if (data) {
          const servicesArray = Object.entries(data).map(([ticker, serviceData]) => ({
            ticker,
            ...serviceData as Omit<Service, 'ticker'>
          }));
          setServices(servicesArray);
        } else {
          setServices([]);
        }
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        setLoading(false);
      }
    }, (error) => {
      setError(error.message);
      setLoading(false);
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  return { services, loading, error };
};
