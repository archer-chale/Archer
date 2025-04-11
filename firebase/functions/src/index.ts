/**
 * Main Firebase Functions entry point
 * This file initializes the Firebase Admin SDK and exports all functions from service modules
 */

import * as admin from 'firebase-admin';

// Initialize Firebase Admin SDK
admin.initializeApp();

// Export all service functions
export { createNewMessage } from "./service/message.service";

