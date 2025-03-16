import { ref, onValue } from 'firebase/database';
import { 
  collection, 
  addDoc, 
  deleteDoc, 
  doc, 
  onSnapshot, 
  query, 
  orderBy,
  serverTimestamp,
  getFirestore
} from 'firebase/firestore';
import { db } from '../../firebaseConfig';
import { firestore } from '../../firebaseConfig';
import { v4 as uuidv4 } from 'uuid';
import { IConfigMessage } from '../../types/pubsubmessage.type';

/**
 * Firebase service for managing messages
 */
class MessageServiceFirebase {
  private readonly MESSAGES_COLLECTION = 'messages';
  private readonly MESSAGES_REF = 'messages';

  /**
   * Save a new message to Firestore
   * @param message - The message to save
   * @returns The saved message with generated id and timestamps
   */
  async saveMessage(message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>): Promise<IConfigMessage | null> {
    try {
      console.log('Saving message firebase:', message);

      // Create a reference to the messages collection
      const messagesCollection = collection(firestore, this.MESSAGES_COLLECTION);
      
      // Generate a unique ID for the message
      const messageId = uuidv4();
      
      // Create the complete message with acknowledgement info
      const completeMessage: IConfigMessage = {
        id: messageId,
        description: message.description,
        config: message.config,
        target: message.target,
        acknowledgement: [],
        acknowledgementCount: 0
      };
      
      // Save message to Firestore
      console.log('Saving message to Firestore:', completeMessage);
      await addDoc(messagesCollection, {
        ...completeMessage,
        // Add Firestore timestamps
        firestoreCreatedAt: serverTimestamp(),
        firestoreUpdatedAt: serverTimestamp()
      });
      
      return completeMessage;
    } catch (error) {
      console.error('Error saving message:', error);
      return null;
    }
  }

  /**
   * Get all messages from Firestore
   * @param callback - Callback function to receive messages
   * @returns Unsubscribe function
   */
  getMessages(callback: (messages: IConfigMessage[]) => void): () => void {
    try {
      // Create a query for messages ordered by creation time
      const messagesQuery = query(
        collection(firestore, this.MESSAGES_COLLECTION),
        orderBy('firestoreCreatedAt', 'desc')
      );
      
      // Subscribe to real-time updates
      const unsubscribe = onSnapshot(messagesQuery, (snapshot) => {
        const messagesList: IConfigMessage[] = [];
        
        snapshot.forEach((doc) => {
          const data = doc.data();
          // Format the data for the IConfigMessage type
          messagesList.push({
            ...data,
            id: doc.id, // Use the Firestore document ID
            acknowledgement: data.acknowledgement || [],
            acknowledgementCount: data.acknowledgementCount || 0
          } as IConfigMessage);
        });
        
        callback(messagesList);
      });
      
      return unsubscribe;
    } catch (error) {
      console.error('Error getting messages:', error);
      callback([]);
      
      // Return dummy unsubscribe function
      return () => {};
    }
  }

  /**
   * Delete a message by ID
   * @param messageId - The ID of the message to delete
   * @returns Whether the deletion was successful
   */
  async deleteMessage(messageId: string): Promise<boolean> {
    try {
      // Delete the message from Firestore
      const messageRef = doc(firestore, this.MESSAGES_COLLECTION, messageId);
      await deleteDoc(messageRef);
      
      return true;
    } catch (error) {
      console.error('Error deleting message:', error);
      return false;
    }
  }

  /**
   * Subscribe to message acknowledgements from bots
   * @param messageId - The message ID to subscribe to
   * @param callback - Callback function to receive acknowledgement updates
   * @returns Unsubscribe function
   */
  subscribeToMessageAcknowledgements(
    messageId: string,
    callback: (ack: IConfigMessage['acknowledgement'], count: number) => void
  ): () => void {
    try {
      // We'll still use Realtime Database for acknowledgements since they'll change frequently
      const ackRef = ref(db, `${this.MESSAGES_REF}/${messageId}/acknowledgement`);
      
      const unsubscribe = onValue(ackRef, (snapshot) => {
        const ackData = snapshot.val();
        
        if (!ackData) {
          console.warn(`No acknowledgement data found for message ${messageId}`);
          return;
        }
        
        // Get the acknowledgement count
        const countRef = ref(db, `${this.MESSAGES_REF}/${messageId}/acknowledgementCount`);
        onValue(countRef, (countSnapshot) => {
          const count = countSnapshot.val() || 0;
          callback(ackData, count);
        }, {
          onlyOnce: true
        });
      });
      
      return unsubscribe;
    } catch (error) {
      console.error('Error subscribing to acknowledgements:', error);
      
      // Return dummy unsubscribe function
      return () => {};
    }
  }
}

// Singleton instance
export const messageServiceFirebase = new MessageServiceFirebase();
