/**
 * Interface for defining message target recipients
 * Used to specify whether a message should be sent to all bots
 * or only selected ones
 */
export interface IMessageTarget {
  /**
   * Type of target - ALL for broadcasting to all bots,
   * SELECTED for sending to specific bots
   */
  type: "ALL" | "SELECTED";
  
  /**
   * Array of bot IDs that should receive the message
   * Should be empty when type is "ALL"
   * Should have at least one ID when type is "SELECTED"
   */
  selected: string[];
}

/**
 * Interface for counter bot configuration
 * Contains settings that will be applied to the counter bot
 */
export interface IMessageConfig {
  /**
   * The value at which the counter bot should start counting
   * For example, if startCountAt is 3, the bot will reset its count to 3
   */
  startCountAt: number;
}

/**
 * Main interface for configuration messages
 * Contains all details about a message including targets, config and acknowledgements
 */
export interface IConfigMessage {
  /**
   * Unique identifier for the message
   */
  id: string;
  
  /**
   * Array of bot IDs that have acknowledged/acted on the message
   */
  acknowledgement: string[];
  
  /**
   * Number of bots that have acknowledged the message
   */
  acknowledgementCount: number;
  
  /**
   * User-provided description of what the configuration is for
   */
  description: string;
  
  /**
   * Configuration settings the bots should apply
   * For the counter bot POC, this will contain startCountAt
   */
  config: IMessageConfig;
  
  /**
   * Defines which bots should receive and act on this message
   */
  target: IMessageTarget;
}

/**
 * Simplified version of IConfigMessage for list views
 * Contains only essential information without full acknowledgement details
 */
export interface IConfigMessageSimple {
  /**
   * Unique identifier for the message
   */
  id: string;
  
  /**
   * User-provided description of what the configuration is for
   */
  description: string;
  
  /**
   * Number of bots that have acknowledged the message
   */
  acknowledgementCount: number;
}