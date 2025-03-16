import { useState, useCallback, useEffect } from 'react';
import { IConfigMessage, IConfigMessageSimple } from '../types/pubsubmessage.type';
import { messageServiceController } from '../service/controllers/message.service.controller';

/**
 * Custom hook for managing messages
 * Provides functions for creating, retrieving, and deleting messages
 */
export const useMessage = () => {
  const [messages, setMessages] = useState<IConfigMessageSimple[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load messages when the hook is initialized
  useEffect(() => {
    loadAllMessages();
    
    // Set up real-time subscription for all messages
    const unsubscribe = messageServiceController.subscribeToAllMessages((updatedMessages) => {
      setMessages(updatedMessages);
    });
    
    // Clean up subscription when component unmounts
    return () => {
      unsubscribe();
    };
  }, []);

  /**
   * Load all messages initially
   * Private function to avoid exposing it in the hook's return value
   */
  const loadAllMessages = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const allMessages = await messageServiceController.getAllMessages();
      setMessages(allMessages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages');
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Retrieves all messages in simplified form
   * Used for displaying the message list
   */
  const getAllMessages = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const allMessages = await messageServiceController.getAllMessages();
      setLoading(false);
      return allMessages;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get messages');
      console.error('Error getting all messages:', err);
      setLoading(false);
      return [];
    }
  }, []);

  /**
   * Retrieves detailed information about a specific message
   * @param id - ID of the message to retrieve
   */
  const getMessageDetailsById = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const messageDetails = await messageServiceController.getMessageDetailsById(id);
      setLoading(false);
      return messageDetails;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get message details');
      console.error(`Error getting message details for ID ${id}:`, err);
      setLoading(false);
      return null;
    }
  }, []);

  /**
   * Saves a new message
   * @param message - Message to save
   */
  const saveMessage = useCallback(async (message: Omit<IConfigMessage, 'id' | 'acknowledgement' | 'acknowledgementCount'>) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Saving message hook:', message);
      const savedMessage = await messageServiceController.saveMessage(message);
      setLoading(false);
      return savedMessage;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save message');
      console.error('Error saving message:', err);
      setLoading(false);
      return null;
    }
  }, []);

  /**
   * Deletes a message by ID
   * @param id - ID of the message to delete
   */
  const deleteMessageById = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const success = await messageServiceController.deleteMessageById(id);
      setLoading(false);
      return success;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete message');
      console.error(`Error deleting message with ID ${id}:`, err);
      setLoading(false);
      return false;
    }
  }, []);

  /**
   * Set up a real-time listener for a specific message to monitor acknowledgements
   * @param messageId - ID of the message to monitor
   * @param callback - Function to call when the message changes
   * @returns Unsubscribe function to clean up the listener
   */
  const subscribeToMessageUpdates = useCallback((messageId: string, callback: (message: IConfigMessage | null) => void) => {
    return messageServiceController.subscribeToMessageUpdates(messageId, callback);
  }, []);

  return {
    messages,
    loading,
    error,
    getAllMessages,
    getMessageDetailsById,
    saveMessage,
    deleteMessageById,
    subscribeToMessageUpdates
  };
};
