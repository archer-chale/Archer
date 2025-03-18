import * as admin from 'firebase-admin';
import { IMessage } from '../types/message.types';

/**
 * Stores a message in Firestore and returns the stored message with its generated id and timestamp
 */
export async function storeMessage(message: IMessage): Promise<IMessage> {
  const db = admin.firestore();
  // Set a server timestamp for the message
  message.timestamp = admin.firestore.FieldValue.serverTimestamp();
  const docRef = await db.collection('messages').add(message);
  const docSnap = await docRef.get();
  return { id: docRef.id, ...docSnap.data() } as IMessage;
}

/**
 * Retrieves a message from Firestore by id
 */
export async function getMessage(id: string): Promise<IMessage | null> {
  const db = admin.firestore();
  const docRef = db.collection('messages').doc(id);
  const docSnap = await docRef.get();
  if (!docSnap.exists) {
    return null;
  }
  return { id: docSnap.id, ...docSnap.data() } as IMessage;
}
