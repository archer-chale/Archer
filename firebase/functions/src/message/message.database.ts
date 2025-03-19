import * as admin from 'firebase-admin';
import { db } from '../firebase';
import { IConfigMessage } from '../types/message.types';
import * as logger from 'firebase-functions/logger';

/**
 * Message database service for handling Firestore operations
 */
export class MessageDatabase {
  private readonly MESSAGES_COLLECTION = 'messages';
  /**
   * Update acknowledgement for a message
   * @param messageId - ID of the message to update
   * @param botId - ID of the bot acknowledging the message
   * @returns Whether the update was successful
   */
  async updateMessageAcknowledgement(messageId: string, botId: string): Promise<boolean> {
    try {
      const messageRef = db.collection(this.MESSAGES_COLLECTION).doc(messageId);
      const messageDoc = await messageRef.get();
      
      if (!messageDoc.exists) {
        logger.warn(`Cannot update acknowledgement: Message with ID ${messageId} not found`);
        return false;
      }
      
      // Update using a transaction to ensure atomic updates
      await db.runTransaction(async (transaction) => {
        const doc = await transaction.get(messageRef);
        const data = doc.data() as IConfigMessage;
        
        // Check if bot has already acknowledged
        if (data.acknowledgement && data.acknowledgement.includes(botId)) {
          logger.info(`Bot ${botId} has already acknowledged message ${messageId}`);
          return;
        }
        
        // Add bot to acknowledgement array and increment count
        const newAcknowledgement = [...(data.acknowledgement || []), botId];
        const newCount = (data.acknowledgementCount || 0) + 1;
        
        transaction.update(messageRef, {
          acknowledgement: newAcknowledgement,
          acknowledgementCount: newCount,
          firestoreUpdatedAt: admin.firestore.FieldValue.serverTimestamp(),
        });
      });
      
      return true;
    } catch (error) {
      logger.error('Error updating message acknowledgement:', error);
      return false;
    }
  }
}

// Singleton instance
export const messageDatabase = new MessageDatabase();
