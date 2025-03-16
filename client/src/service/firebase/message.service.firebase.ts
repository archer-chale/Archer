import { ref, onValue, push, set, get, remove, update, query, orderByChild } from 'firebase/database';
import { db } from '../../firebaseConfig';
import { IConfigMessage, IConfigMessageSimple } from '../../types/pubsubmessage.type';

/**
 * Firebase service for interacting with messages in the Firebase database
 * Provides methods to create, read, update, and delete messages
 */
class MessageServiceFirebase {
  private readonly MESSAGES_REF = 'messages';

  /**
   * Save a new message to the Firebase database
   * @param message - The message to save (without id, acknowledgement, and acknowledgementCount)
   * @returns Promise resolving to the saved message with id
   */
  async saveMessage(message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>): Promise<IConfigMessage | null> {
    try {
      // Create a reference to the messages in the database
      const messagesRef = ref(db, this.MESSAGES_REF);
      
      // Generate a new key for the message
      const newMessageRef = push(messagesRef);
      const messageId = newMessageRef.key;
      
      if (!messageId) {
        throw new Error('Failed to generate message ID');
      }
      
      // Create complete message object with ID and empty acknowledgements
      const completeMessage: IConfigMessage = {
        ...message,
        id: messageId,
        acknowledgement: [],
        acknowledgementCount: 0
      };
      
      // Save message to Firebase
      await set(newMessageRef, completeMessage);
      
      return completeMessage;
    } catch (error) {
      console.error('Error saving message:', error);
      return null;
    }
  }

  /**
   * Get all messages in simplified form
   * @returns Promise resolving to array of simplified messages
   */
  async getAllMessages(): Promise<IConfigMessageSimple[]> {
    try {
      // Create a reference to the messages in the database
      const messagesRef = ref(db, this.MESSAGES_REF);
      
      // Get messages snapshot
      const snapshot = await get(messagesRef);
      
      if (!snapshot.exists()) {
        return [];
      }
      
      // Convert messages to array and map to simplified form
      const messages: IConfigMessageSimple[] = [];
      snapshot.forEach((childSnapshot) => {
        const messageData = childSnapshot.val() as IConfigMessage;
        messages.push({
          id: messageData.id,
          description: messageData.description,
          acknowledgementCount: messageData.acknowledgementCount
        });
      });
      
      // Sort by most recent first (assuming ids are timestamp-based)
      messages.sort((a, b) => b.id.localeCompare(a.id));
      
      return messages;
    } catch (error) {
      console.error('Error getting messages:', error);
      return [];
    }
  }

  /**
   * Get detailed information about a specific message
   * @param id - ID of the message to retrieve
   * @returns Promise resolving to the message details
   */
  async getMessageDetailsById(id: string): Promise<IConfigMessage | null> {
    try {
      // Create a reference to the specific message
      const messageRef = ref(db, `${this.MESSAGES_REF}/${id}`);
      
      // Get message snapshot
      const snapshot = await get(messageRef);
      
      if (!snapshot.exists()) {
        return null;
      }
      
      // Return message data
      return snapshot.val() as IConfigMessage;
    } catch (error) {
      console.error('Error getting message details:', error);
      return null;
    }
  }

  /**
   * Delete a message by ID
   * @param id - ID of the message to delete
   * @returns Promise resolving to true if deletion was successful
   */
  async deleteMessageById(id: string): Promise<boolean> {
    try {
      // Create a reference to the specific message
      const messageRef = ref(db, `${this.MESSAGES_REF}/${id}`);
      
      // Remove the message
      await remove(messageRef);
      
      return true;
    } catch (error) {
      console.error('Error deleting message:', error);
      return false;
    }
  }

  /**
   * Set up a real-time listener for a specific message to monitor acknowledgements
   * @param messageId - ID of the message to monitor
   * @param callback - Function to call when the message changes
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToMessageUpdates(messageId: string, callback: (message: IConfigMessage | null) => void): () => void {
    const messageRef = ref(db, `${this.MESSAGES_REF}/${messageId}`);
    
    // Set up real-time listener
    const unsubscribe = onValue(messageRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        callback(data as IConfigMessage);
      } else {
        callback(null);
      }
    }, (error) => {
      console.error(`Error monitoring message ${messageId}:`, error);
      callback(null);
    });
    
    // Return unsubscribe function
    return unsubscribe;
  }

  /**
   * Set up a real-time listener for all messages
   * @param callback - Function to call when messages change
   * @returns Unsubscribe function to clean up the listener
   */
  subscribeToAllMessages(callback: (messages: IConfigMessageSimple[]) => void): () => void {
    const messagesRef = ref(db, this.MESSAGES_REF);
    
    // Set up real-time listener
    const unsubscribe = onValue(messagesRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const messagesArray: IConfigMessageSimple[] = Object.entries(data).map(([_, messageData]) => {
          const typedData = messageData as IConfigMessage;
          return {
            id: typedData.id,
            description: typedData.description,
            acknowledgementCount: typedData.acknowledgementCount
          };
        });
        
        // Sort by most recent first (assuming ids are timestamp-based)
        messagesArray.sort((a, b) => b.id.localeCompare(a.id));
        
        callback(messagesArray);
      } else {
        callback([]);
      }
    }, (error) => {
      console.error('Error monitoring messages:', error);
      callback([]);
    });
    
    // Return unsubscribe function
    return unsubscribe;
  }
}

// Singleton instance
export const messageServiceFirebase = new MessageServiceFirebase();
