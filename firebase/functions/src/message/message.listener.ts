import * as functions from 'firebase-functions';
import { onDocumentCreated } from 'firebase-functions/v2/firestore';
import * as logger from 'firebase-functions/logger';
import { IConfigMessage } from '../types/message.types';
import '../firebase'; // Import firebase first to ensure initialization happens
import * as admin from 'firebase-admin';

// Topic that all bots subscribe to
const BOTS_TOPIC = 'messages';

/**
 * Firebase function that listens for new messages in Firestore
 * and sends notifications to the appropriate bots
 */
export const messageCreatedHandler = onDocumentCreated('messages/{messageId}', async (event) => {
  try {
    // Get the message data
    const messageData = event.data?.data() as IConfigMessage | undefined;
    if (!messageData) {
      logger.warn('Message data is empty or not in expected format');
      return;
    }

    const messageId = event.params.messageId;
    logger.info(`New message created with ID: ${messageId}`, messageData);

    // Get messaging service inside the function
    const messaging = admin.messaging();

    // Format the message for FCM
    const message = {
      data: {
        messageId: messageId,
        description: messageData.description,
        config: JSON.stringify(messageData.config),
        targetType: messageData.target.type,
        targetSelected: JSON.stringify(messageData.target.selected || []),
      },
      topic: BOTS_TOPIC,
    };

    // Send the message to all bots via FCM topic
    // Bots will filter messages based on target information
    const response = await messaging.send(message);
    logger.info(`Successfully sent message to topic ${BOTS_TOPIC}:`, response);

  } catch (error) {
    logger.error('Error sending message notification:', error);
  }
});

/**
 * Firebase function that updates the acknowledgement count when a 
 * bot acknowledges a message (will be implemented later)
 */
export const onMessageAcknowledged = functions.https.onCall(async (data, context) => {
  // This will be implemented in a future sprint
  // Will handle bot acknowledgement of messages
  logger.info('Message acknowledgement function called, implementation pending');
  
  // Return a placeholder response
  return { success: true, message: 'Acknowledgement endpoint ready for implementation' };
});
