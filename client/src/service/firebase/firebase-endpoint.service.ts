import { ref, onValue, push, set } from 'firebase/database';
import { db } from '../../firebaseConfig';

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
  [key: string]: any;
}

export interface Message {
  id: string;
  message: string;
  target: string; // "ALL" or container ID
  timestamp: string;
}

export interface LogEntry {
  id: string;
  containerId: string;
  message: string;
  timestamp: string;
}

/**
 * Firebase service for interacting with the Firebase database
 * Provides methods to fetch services, send messages, and subscribe to logs
 */
class FirebaseEndpointService {
  /**
   * Set up a real-time listener for services
   * @param callback - Function to call when services change
   * @returns Unsubscribe function to clean up the listener
   */
  getServices(callback: (services: Service[]) => void): () => void {
    const servicesRef = ref(db, 'services');
    
    // Set up real-time listener
    const unsubscribe = onValue(servicesRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const servicesArray = Object.entries(data).map(([ticker, serviceData]) => {
          // Cast to any to work with the data
          const typedData = serviceData as any;
          
          // Create a properly typed service object with defaults for missing properties
          const service: Service = {
            ticker,
            status: typedData.status || 'stopped',  // Default status
            bots: typedData.bots || {},            // Default empty bots object
            ...typedData                           // Include all other data
          };
          
          return service;
        });
        console.log(servicesArray);
        callback(servicesArray);
      } else {
        callback([]);
      }
    }, (error) => {
      console.error('Error fetching services:', error);
      callback([]);
    });
    
    // Return unsubscribe function
    return unsubscribe;
  }

  /**
   * Send a message to bots
   * @param message - Message content
   * @param target - Target container ID or "ALL" for all containers
   * @returns Promise resolving to true if successful
   */
  async sendMessage(message: string, target: string): Promise<boolean> {
    try {
      // Create a reference to the messages in the database
      const messagesRef = ref(db, 'messages');
      
      // Generate a new key for the message
      const newMessageRef = push(messagesRef);
      
      // Create message object
      const messageData: Omit<Message, 'id'> = {
        message,
        target,
        timestamp: new Date().toISOString()
      };
      
      // Save message to Firebase
      await set(newMessageRef, messageData);
      
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }

  /**
   * Set up a real-time listener for logs
   * @param callback - Function to call when logs change
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToLogs(callback: (logs: LogEntry[]) => void): () => void {
    const logsRef = ref(db, 'logs');
    
    // Set up real-time listener
    const unsubscribe = onValue(logsRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const logsArray = Object.entries(data).map(([id, logData]) => ({
          id,
          ...logData as Omit<LogEntry, 'id'>
        }));
        
        // Sort logs by timestamp (newest first)
        logsArray.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        
        callback(logsArray);
      } else {
        callback([]);
      }
    }, (error) => {
      console.error('Error fetching logs:', error);
      callback([]);
    });
    
    // Return unsubscribe function
    return unsubscribe;
  }
}

// Singleton instance
export const firebaseEndpointService = new FirebaseEndpointService();
