import * as admin from 'firebase-admin';
import { onDocumentCreated } from 'firebase-functions/v2/firestore';

// This Cloud Function triggers when a new message is added to the 'messages' collection
// It uses Firebase Messaging to notify subscribers that a new message has been created
export const onMessageCreated = onDocumentCreated('messages/{messageId}', async (event) => {
  if (!event.data || !event.data.data()) {
    console.error('No event data found');
    return null;
  }

  const message = event.data.data();
  if (!message) {
    console.error('No message data found');
    return null;
  }

  // Construct the notification payload
  const payload: admin.messaging.MessagingPayload = {
    notification: {
      title: 'New Message',
      body: message.content ? String(message.content).substring(0, 100) : 'A new message has been posted.'
    },
    data: {
      messageId: event.data.id
    }
  };

  try {
    // Send a message to devices subscribed to the 'messages' topic
    const response = await admin.messaging().sendToTopic('messages', payload);
    console.log('Successfully sent message:', response);
    return response;
  } catch (error) {
    console.error('Error sending message:', error);
    return null;
  }
});
