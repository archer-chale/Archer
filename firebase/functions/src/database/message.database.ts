import { IConfigMessage } from '../types/message.types';
import BaseDatabaseService from './base.database';


class MessageDatabaseService extends BaseDatabaseService<IConfigMessage, "messages"> {
  constructor() {
    super("messages")
  }
}

export default new MessageDatabaseService();
