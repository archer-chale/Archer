import { 
  messageServiceFirebase 
} from '../firebase/message.service.firebase';
import { IConfigMessage, IConfigMessageSimple, IMessageTarget } from '../../types/pubsubmessage.type';

/**
 * Message Service Controller for managing message operations
 * Acts as an intermediary between UI components and the Firebase message service
 * Adds validation, error handling, and provides a clean API
 */
class MessageServiceController {
  /**
   * Save a new message
   * @param message - The message to save (without id, acknowledgement, and acknowledgementCount)
   * @returns Promise resolving to the saved message with id
   */
  async saveMessage(
    message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>
  ): Promise<IConfigMessage | null> {
    // Validate the message
    console.log('Saving message controller:', message);
    try {
      // Save message via Firebase service
      const savedMessage = await messageServiceFirebase.saveMessage(message);
      console.log('Message saved controller:', savedMessage);
      if (!savedMessage) {
        throw new Error('Failed to save message');
      }
      
      return savedMessage;
    } catch (error) {
      console.error('Error in saveMessage controller:', error);
      throw error;
    }

    return null;
  }

  /**
   * Get all messages in simplified form
   * @returns Promise resolving to array of simplified messages
   */
  async getAllMessages(): Promise<IConfigMessageSimple[]> {
    try {
      // Create a promise to get messages
      return new Promise((resolve, reject) => {
        // Use the getMessages method from the Firebase service with a callback
        const unsubscribe = messageServiceFirebase.getMessages((messages) => {
          // Convert full messages to simplified form
          const simplifiedMessages: IConfigMessageSimple[] = messages.map(msg => ({
            id: msg.id,
            description: msg.description,
            acknowledgementCount: msg.acknowledgementCount
          }));
          
          // Resolve the promise with simplified messages
          resolve(simplifiedMessages);
          
          // Unsubscribe since we only need a one-time fetch
          unsubscribe();
        });
      });
    } catch (error) {
      console.error('Error in getAllMessages controller:', error);
      throw error;
    }
  }

  /**
   * Get detailed information about a specific message
   * @param id - ID of the message to retrieve
   * @returns Promise resolving to the message details
   */
  async getMessageDetailsById(id: string): Promise<IConfigMessage | null> {
    if (!id) {
      console.error('Invalid message ID: empty string');
      throw new Error('Message ID is required');
    }

    try {
      // Create a promise to get message details
      return new Promise((resolve, reject) => {
        // Use the getMessages method to fetch all messages
        const unsubscribe = messageServiceFirebase.getMessages((messages) => {
          // Find the message with the specified ID
          const message = messages.find(msg => msg.id === id);
          
          if (!message) {
            reject(new Error(`Message with ID ${id} not found`));
          } else {
            resolve(message);
          }
          
          // Unsubscribe since we only need a one-time fetch
          unsubscribe();
        });
      });
    } catch (error) {
      console.error(`Error in getMessageDetailsById controller for ID ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete a message by ID
   * @param id - ID of the message to delete
   * @returns Promise resolving to true if deletion was successful
   */
  async deleteMessageById(id: string): Promise<boolean> {
    if (!id) {
      console.error('Invalid message ID: empty string');
      throw new Error('Message ID is required');
    }

    try {
      // Delete message via Firebase service
      const success = await messageServiceFirebase.deleteMessage(id);
      
      if (!success) {
        throw new Error(`Failed to delete message with ID ${id}`);
      }
      
      return true;
    } catch (error) {
      console.error(`Error in deleteMessageById controller for ID ${id}:`, error);
      throw error;
    }
  }

  /**
   * Set up a real-time listener for a specific message to monitor acknowledgements
   * @param messageId - ID of the message to monitor
   * @param callback - Function to call when the message changes
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToMessageUpdates(
    messageId: string, 
    callback: (message: IConfigMessage | null) => void
  ): () => void {
    if (!messageId) {
      console.error('Invalid message ID: empty string');
      callback(null);
      return () => {};
    }

    try {
      // Create a message tracker object for updates
      let currentMessage: IConfigMessage | null = null;
      
      // Subscribe to all messages to get the full message data
      const messagesUnsubscribe = messageServiceFirebase.getMessages((messages) => {
        const message = messages.find(msg => msg.id === messageId) || null;
        
        // Store the found message for use with acknowledgement updates
        if (message) {
          currentMessage = message;
          callback(message);
        }
      });
      
      // Subscribe to acknowledgement updates
      const ackUnsubscribe = messageServiceFirebase.subscribeToMessageAcknowledgements(
        messageId,
        (acknowledgement, count) => {
          // Only update if we have a current message
          if (currentMessage) {
            // Update acknowledgement and count
            const updatedMessage: IConfigMessage = {
              ...currentMessage,
              acknowledgement: acknowledgement || [],
              acknowledgementCount: count
            };
            
            // Send updated message to callback
            callback(updatedMessage);
          }
        }
      );
      
      // Return a combined unsubscribe function
      return () => {
        messagesUnsubscribe();
        ackUnsubscribe();
      };
    } catch (error) {
      console.error(`Error in subscribeToMessageUpdates controller for ID ${messageId}:`, error);
      callback(null);
      return () => {};
    }
  }

  /**
   * Set up a real-time listener for all messages
   * @param callback - Function to call when messages change
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToAllMessages(
    callback: (messages: IConfigMessageSimple[]) => void
  ): () => void {
    try {
      // Set up subscription to messages
      return messageServiceFirebase.getMessages((messages) => {
        // Convert to simplified form
        const simplifiedMessages: IConfigMessageSimple[] = messages.map(msg => ({
          id: msg.id,
          description: msg.description,
          acknowledgementCount: msg.acknowledgementCount
        }));
        
        // Send to callback
        callback(simplifiedMessages);
      });
    } catch (error) {
      console.error('Error in subscribeToAllMessages controller:', error);
      callback([]);
      return () => {};
    }
  }

  /**
   * Validate a message for required fields and proper structure
   * @param message - The message to validate
   * @returns Error message if validation fails, null if valid
   */
  private validateMessage(
    message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>
  ): string | null {
    // Check for required fields
    if (!message) {
      return 'Message is required';
    }

    if (!message.description || message.description.trim().length === 0) {
      return 'Message description is required';
    }

    if (!message.config) {
      return 'Message configuration is required';
    }

    // Validate startCountAt for counter bot
    if (typeof message.config.startCountAt !== 'number') {
      return 'startCountAt must be a number';
    }

    // Validate target
    if (!message.target) {
      return 'Message target is required';
    }

    return this.validateMessageTarget(message.target);
  }

  /**
   * Validate message target
   * @param target - The target to validate
   * @returns Error message if validation fails, null if valid
   */
  private validateMessageTarget(target: IMessageTarget): string | null {
    // Check if target type is valid
    if (target.type !== 'ALL' && target.type !== 'SELECTED') {
      return 'Target type must be "ALL" or "SELECTED"';
    }

    // Check if selected array exists
    if (!Array.isArray(target.selected)) {
      return 'Target selected must be an array';
    }

    // For "ALL" type, selected should be empty
    if (target.type === 'ALL' && target.selected.length > 0) {
      return 'Target selected should be empty for type "ALL"';
    }

    // For "SELECTED" type, selected should have at least one entry
    if (target.type === 'SELECTED' && target.selected.length === 0) {
      return 'At least one target must be selected for type "SELECTED"';
    }

    return null;
  }
}

// Singleton instance
export const messageServiceController = new MessageServiceController();
