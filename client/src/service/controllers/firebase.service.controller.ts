import { 
  firebaseEndpointService,
  Service,
  LogEntry 
} from '../firebase/firebase-endpoint.service';

/**
 * Firebase service controller for managing Firebase operations
 * Acts as an intermediary between UI components and the Firebase endpoint service
 */
class FirebaseServiceController {
  /**
   * Set up a real-time listener for services
   * @param callback - Function to call when services change
   * @returns Unsubscribe function to clean up the listener
   */
  getServices(callback: (services: Service[]) => void): () => void {
    return firebaseEndpointService.getServices(callback);
  }

  /**
   * Send a message to bots
   * @param message - Message content
   * @param target - Target container ID or "ALL" for all containers
   * @returns Promise resolving to true if successful
   */
  async sendMessage(message: string, target: string): Promise<boolean> {
    if (!message.trim()) {
      console.warn('Attempted to send empty message');
      return false;
    }

    try {
      const result = await firebaseEndpointService.sendMessage(message, target);
      return result;
    } catch (error) {
      console.error('Error in sendMessage controller:', error);
      return false;
    }
  }

  /**
   * Set up a real-time listener for logs
   * @param callback - Function to call when logs change
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToLogs(callback: (logs: LogEntry[]) => void): () => void {
    return firebaseEndpointService.subscribeToLogs(callback);
  }
}

// Singleton instance
export const firebaseServiceController = new FirebaseServiceController();
