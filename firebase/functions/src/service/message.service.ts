import { logger } from 'firebase-functions';
import { onCall } from 'firebase-functions/v2/https';
import { IConfigMessage } from '../types/message.types';
import messageDatabaseService from '../database/message.database';

/**
 * Firebase callable function to create a new message
 * Client can call this function to create a new configuration message
 */
export const createNewMessage = onCall(async (request) => {
  try {
    const messageData = request.data as Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>;
    logger.info('Received request to create message', { data: messageData });
    
    // Validate the message data has required fields
    if (!messageData || !messageData.description || !messageData.config || !messageData.target) {
      throw new Error('Invalid message data: Missing required fields');
    }
    
    // Initialize acknowledgement fields
    const messageWithAck = {
      ...messageData,
      acknowledgement: [],
      acknowledgementCount: 0
    };
    
    // Save to database using the database service
    const createdMessage = await messageDatabaseService.create(messageWithAck);
    
    logger.info('Message created successfully', { messageId: createdMessage.id });
    return createdMessage;
  } catch (error: any) {
    logger.error('Error creating message', error);
    throw new Error(`Failed to create message: ${error.message}`);
  }
});
