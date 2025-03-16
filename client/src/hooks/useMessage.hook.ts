import { useState, useCallback } from 'react';
import { IConfigMessage, IConfigMessageSimple } from '../types/pubsubmessage.type';

/**
 * Mock data for testing the Messages UI
 */
const mockMessages: IConfigMessageSimple[] = [
  {
    id: '1',
    description: 'Reset counter to 5',
    acknowledgementCount: 3
  },
  {
    id: '2',
    description: 'Set all counters to 10',
    acknowledgementCount: 5
  },
  {
    id: '3',
    description: 'Pause AAPL counter',
    acknowledgementCount: 1
  },
  {
    id: '4',
    description: 'Reset all counters',
    acknowledgementCount: 0
  }
];

/**
 * Mock message details
 */
const mockMessageDetails: Record<string, IConfigMessage> = {
  '1': {
    id: '1',
    description: 'Reset counter to 5',
    acknowledgement: ['bot1', 'bot2', 'bot3'],
    acknowledgementCount: 3,
    config: { startCountAt: 5 },
    target: { type: 'SELECTED', selected: ['bot1', 'bot2', 'bot3'] }
  },
  '2': {
    id: '2',
    description: 'Set all counters to 10',
    acknowledgement: ['bot1', 'bot2', 'bot3', 'bot4', 'bot5'],
    acknowledgementCount: 5,
    config: { startCountAt: 10 },
    target: { type: 'ALL', selected: [] }
  },
  '3': {
    id: '3',
    description: 'Pause AAPL counter',
    acknowledgement: ['bot1'],
    acknowledgementCount: 1,
    config: { startCountAt: 0 },
    target: { type: 'SELECTED', selected: ['bot1'] }
  },
  '4': {
    id: '4',
    description: 'Reset all counters',
    acknowledgement: [],
    acknowledgementCount: 0,
    config: { startCountAt: 0 },
    target: { type: 'ALL', selected: [] }
  }
};

/**
 * Custom hook for managing messages
 * Provides functions for creating, retrieving, and deleting messages
 */
export const useMessage = () => {
  const [messages, setMessages] = useState<IConfigMessageSimple[]>(mockMessages);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Retrieves all messages in simplified form
   * Used for displaying the message list
   */
  const getAllMessages = useCallback(async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Return mock data
      setLoading(false);
      return mockMessages;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get messages');
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
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const messageDetails = mockMessageDetails[id];
      if (!messageDetails) {
        throw new Error('Message not found');
      }
      
      setLoading(false);
      return messageDetails;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get message details');
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
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Create new message with ID and empty acknowledgements
      const newMessage: IConfigMessage = {
        ...message,
        id: `msg-${Date.now()}`,
        acknowledgement: [],
        acknowledgementCount: 0
      };
      
      // Update mock data
      mockMessageDetails[newMessage.id] = newMessage;
      const newSimpleMessage: IConfigMessageSimple = {
        id: newMessage.id,
        description: newMessage.description,
        acknowledgementCount: 0
      };
      
      setMessages(prev => [newSimpleMessage, ...prev]);
      setLoading(false);
      return newMessage;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save message');
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
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Remove from mock data
      delete mockMessageDetails[id];
      setMessages(prev => prev.filter(message => message.id !== id));
      
      setLoading(false);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete message');
      setLoading(false);
      return false;
    }
  }, []);

  return {
    messages,
    loading,
    error,
    getAllMessages,
    getMessageDetailsById,
    saveMessage,
    deleteMessageById
  };
};
