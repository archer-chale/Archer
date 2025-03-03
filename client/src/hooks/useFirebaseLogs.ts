import { useState, useEffect } from 'react';
import { LogEntry } from '../service/firebase/firebase-endpoint.service';
import { firebaseServiceController } from '../service/controllers/firebase.service.controller';

/**
 * Custom hook for accessing Firebase logs
 * Provides real-time updates of log entries from bots
 */
export const useFirebaseLogs = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      // Subscribe to logs using the controller
      const unsubscribe = firebaseServiceController.subscribeToLogs((logsData) => {
        setLogs(logsData);
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

  return { logs, loading, error };
};
